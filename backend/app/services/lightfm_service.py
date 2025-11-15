"""
Serviço LightFM - Sistema de Recomendação Híbrido
Combina Content-Based Filtering (CBF) e Collaborative Filtering (CF)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.cross_validation import random_train_test_split
from lightfm.evaluation import (
    precision_at_k, 
    auc_score,
    recall_at_k,
    reciprocal_rank
)
import joblib
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.usuarios import Usuarios
from app.models.estabelecimentos import Estabelecimentos
from app.models.recomendacao_estabelecimento import RecomendacaoEstabelecimento
from app.models.usuario_preferencia import UsuarioPreferencia
from app.models.estabelecimento_preferencia import EstabelecimentoPreferencia
from app.models.preferencias import Preferencias

# Import MLflow (opcional - não quebra se não estiver instalado)
mlflow = None
MLFLOW_AVAILABLE = False
try:
    import mlflow
    from app.core.mlflow_config import (
        get_or_create_experiment,
        register_model_to_production,
        get_production_model_version,
        get_best_model_run,
        get_client,
        MODEL_NAME
    )
    MLFLOW_AVAILABLE = True
except ImportError:
    pass


class LightFMService:
    """
    Serviço para treinamento e predição usando LightFM
    
    Características:
    - Suporta features de usuários e estabelecimentos (CBF)
    - Suporta matriz de interações (CF)
    - Resolve cold start através de features
    - Múltiplas funções de perda: WARP, BPR, Logistic
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Inicializa o serviço LightFM
        
        Args:
            model_dir: Diretório para salvar/carregar modelos
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model: Optional[LightFM] = None
        self.dataset: Optional[Dataset] = None
        self.user_id_map: Dict[int, int] = {}  # user_id DB -> user_id LightFM
        self.item_id_map: Dict[int, int] = {}  # item_id DB -> item_id LightFM
        self.reverse_user_map: Dict[int, int] = {}  # user_id LightFM -> user_id DB
        self.reverse_item_map: Dict[int, int] = {}  # item_id LightFM -> item_id DB
        
    def _load_interactions(self, db: Session) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Carrega matriz de interações do banco de dados
        
        Returns:
            (user_ids, item_ids, ratings): Arrays numpy com interações
        """
        # Selecionar apenas colunas que existem (sem created_at e updated_at)
        from sqlalchemy import select
        stmt = select(
            RecomendacaoEstabelecimento.id_usuario,
            RecomendacaoEstabelecimento.id_lugar,
            RecomendacaoEstabelecimento.score
        )
        
        result = db.execute(stmt)
        rows = result.all()
        
        if not rows:
            return np.array([]), np.array([]), np.array([])
        
        user_ids = []
        item_ids = []
        ratings = []
        
        for row in rows:
            user_ids.append(row.id_usuario)
            item_ids.append(row.id_lugar)
            ratings.append(float(row.score))
        
        return np.array(user_ids), np.array(item_ids), np.array(ratings)
    
    def _load_user_features(self, db: Session) -> Dict[int, List[Tuple[int, float]]]:
        """
        Carrega features de usuários (preferências declaradas)
        
        Returns:
            Dict mapping user_id -> [(feature_id, weight), ...]
        """
        # Selecionar apenas colunas que existem (sem id, created_at e updated_at)
        from sqlalchemy import select
        stmt = select(
            UsuarioPreferencia.id_usuario,
            UsuarioPreferencia.id_preferencia,
            UsuarioPreferencia.peso
        )
        
        result = db.execute(stmt)
        rows = result.all()
        
        features_map = {}
        for row in rows:
            if row.id_usuario not in features_map:
                features_map[row.id_usuario] = []
            features_map[row.id_usuario].append((row.id_preferencia, float(row.peso)))
        
        return features_map
    
    def _load_item_features(self, db: Session) -> Dict[int, List[Tuple[int, float]]]:
        """
        Carrega features de estabelecimentos (características)
        
        Returns:
            Dict mapping item_id -> [(feature_id, weight), ...]
        """
        # Selecionar apenas colunas que existem (sem id, created_at e updated_at)
        from sqlalchemy import select
        stmt = select(
            EstabelecimentoPreferencia.id_estabelecimento,
            EstabelecimentoPreferencia.id_preferencia,
            EstabelecimentoPreferencia.peso
        )
        
        result = db.execute(stmt)
        rows = result.all()
        
        features_map = {}
        for row in rows:
            if row.id_estabelecimento not in features_map:
                features_map[row.id_estabelecimento] = []
            features_map[row.id_estabelecimento].append((row.id_preferencia, float(row.peso)))
        
        return features_map
    
    def _build_dataset(self, db: Session, use_features: bool = True):
        """
        Constrói o dataset LightFM a partir do banco de dados
        
        Args:
            db: Sessão do banco de dados
            use_features: Se True, inclui features de usuários e itens
        """
        # Carregar interações
        user_ids, item_ids, ratings = self._load_interactions(db)
        
        if len(user_ids) == 0:
            raise ValueError("Nenhuma interação encontrada no banco de dados")
        
        # Criar mapeamentos únicos
        unique_users = np.unique(user_ids)
        unique_items = np.unique(item_ids)
        
        # Criar mapeamentos bidirecionais
        # Converter valores NumPy para tipos Python nativos
        self.user_id_map = {
            int(db_id.item() if hasattr(db_id, 'item') else db_id): idx 
            for idx, db_id in enumerate(unique_users)
        }
        self.item_id_map = {
            int(db_id.item() if hasattr(db_id, 'item') else db_id): idx 
            for idx, db_id in enumerate(unique_items)
        }
        self.reverse_user_map = {
            idx: int(db_id.item() if hasattr(db_id, 'item') else db_id) 
            for db_id, idx in self.user_id_map.items()
        }
        self.reverse_item_map = {
            idx: int(db_id.item() if hasattr(db_id, 'item') else db_id) 
            for db_id, idx in self.item_id_map.items()
        }
        
        # Converter IDs para índices do LightFM
        user_indices = np.array([self.user_id_map[uid] for uid in user_ids])
        item_indices = np.array([self.item_id_map[iid] for iid in item_ids])
        
        # Criar dataset
        self.dataset = Dataset()
        self.dataset.fit(
            users=unique_users.tolist(),
            items=unique_items.tolist()
        )
        
        # Adicionar features se solicitado
        if use_features:
            user_features_map = self._load_user_features(db)
            item_features_map = self._load_item_features(db)
            
            # Obter todas as preferências únicas (usando select para evitar colunas que não existem)
            stmt_prefs = select(Preferencias.id)
            prefs_result = db.execute(stmt_prefs)
            all_prefs = prefs_result.all()
            feature_names = [f"pref_{p.id}" for p in all_prefs]
            
            # Adicionar features ao dataset
            self.dataset.fit_partial(
                user_features=feature_names,
                item_features=feature_names
            )
            
            # Construir matrizes de features
            user_features_list = []
            item_features_list = []
            
            for user_id in unique_users:
                user_feats = []
                if user_id in user_features_map:
                    for feat_id, weight in user_features_map[user_id]:
                        user_feats.append(f"pref_{feat_id}")
                user_features_list.append(user_feats)
            
            for item_id in unique_items:
                item_feats = []
                if item_id in item_features_map:
                    for feat_id, weight in item_features_map[item_id]:
                        item_feats.append(f"pref_{feat_id}")
                item_features_list.append(item_feats)
            
            # Construir interações com features
            interactions, weights = self.dataset.build_interactions(
                zip(user_ids.tolist(), item_ids.tolist(), ratings.tolist())
            )
            
            user_features = self.dataset.build_user_features(
                zip(unique_users.tolist(), user_features_list)
            )
            
            item_features = self.dataset.build_item_features(
                zip(unique_items.tolist(), item_features_list)
            )
            
            return interactions, weights, user_features, item_features
        else:
            # Sem features - apenas CF
            interactions, weights = self.dataset.build_interactions(
                zip(user_ids.tolist(), item_ids.tolist(), ratings.tolist())
            )
            return interactions, weights, None, None
    
    def train(
        self,
        db: Session,
        loss: str = "warp",
        learning_rate: float = 0.05,
        num_components: int = 30,
        num_epochs: int = 30,
        use_features: bool = True,
        num_threads: int = 4,
        use_mlflow: bool = True
    ) -> Dict[str, float]:
        """
        Treina o modelo LightFM
        
        Args:
            db: Sessão do banco de dados
            loss: Função de perda ('warp', 'bpr', 'logistic')
            learning_rate: Taxa de aprendizado
            num_components: Dimensão dos embeddings
            num_epochs: Número de épocas de treinamento
            use_features: Se True, usa features para CBF
            num_threads: Número de threads para treinamento
            use_mlflow: Se True, registra experimento no MLflow
            
        Returns:
            Dict com métricas de avaliação
        """
        # Construir dataset
        result = self._build_dataset(db, use_features=use_features)
        
        # _build_dataset sempre retorna 4 valores: interactions, weights, user_features, item_features
        # Quando use_features=False, user_features e item_features são None
        interactions, weights, user_features, item_features = result
        
        # Dividir em treino e teste
        train, test = random_train_test_split(
            interactions,
            test_percentage=0.2,
            random_state=42
        )
        
        # Estatísticas do dataset para registro no MLflow
        dataset_stats = {
            "num_users": len(self.user_id_map),
            "num_items": len(self.item_id_map),
            "num_interactions": interactions.nnz,
            "train_interactions": train.nnz,
            "test_interactions": test.nnz
        }
        
        # Configurar MLflow se disponível e solicitado
        mlflow_run = None
        if use_mlflow:
            if not MLFLOW_AVAILABLE:
                print(f"⚠️  MLflow solicitado mas não está disponível. Instale com: pip install mlflow")
            else:
                try:
                    print(f"🔬 MLflow: Configurando experimento...")
                    experiment_id = get_or_create_experiment()
                    mlflow.set_experiment(experiment_id=experiment_id)
                    mlflow_run = mlflow.start_run()
                    print(f"🔬 MLflow: Iniciando experimento (Run ID: {mlflow_run.info.run_id})")
                    
                    # Registrar hiperparâmetros
                    mlflow.log_params({
                        "loss": loss,
                        "learning_rate": learning_rate,
                        "num_components": num_components,
                        "num_epochs": num_epochs,
                        "use_features": use_features,
                        "num_threads": num_threads
                    })
                    print(f"📝 MLflow: Hiperparâmetros registrados")
                    
                    # Registrar estatísticas do dataset
                    mlflow.log_params(dataset_stats)
                    print(f"📊 MLflow: Estatísticas do dataset registradas")
                    
                except Exception as e:
                    import traceback
                    print(f"⚠️  Erro ao configurar MLflow: {e}")
                    print(f"   Traceback: {traceback.format_exc()}")
                    print(f"   Continuando sem MLflow...")
                    mlflow_run = None
        else:
            print(f"ℹ️  MLflow desabilitado para este treinamento")
        
        # Criar modelo
        self.model = LightFM(
            loss=loss,
            learning_rate=learning_rate,
            no_components=num_components,
            random_state=42
        )
        
        # Treinar
        # Nota: weights de build_interactions não pode ser usado como sample_weight
        # Se precisar de pesos, construa uma matriz separada
        self.model.fit(
            train,
            user_features=user_features,
            item_features=item_features,
            epochs=num_epochs,
            num_threads=num_threads,
            verbose=True
        )
        
        # Avaliar com múltiplas métricas
        metrics = {}
        try:
            # Precision@K (já existente)
            train_precision_10 = precision_at_k(
                self.model,
                train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
            test_precision_10 = precision_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
            # Precision@5 e Precision@20 para diferentes tamanhos de lista
            test_precision_5 = precision_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=5,
                num_threads=num_threads
            ).mean()
            
            test_precision_20 = precision_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=20,
                num_threads=num_threads
            ).mean()
            
            # Recall@K - quantos itens relevantes foram recuperados
            train_recall_10 = recall_at_k(
                self.model,
                train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
            test_recall_10 = recall_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
            test_recall_5 = recall_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=5,
                num_threads=num_threads
            ).mean()
            
            # AUC (já existente)
            train_auc = auc_score(
                self.model,
                train,
                user_features=user_features,
                item_features=item_features,
                num_threads=num_threads
            ).mean()
            
            test_auc = auc_score(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                num_threads=num_threads
            ).mean()
            
            # MRR (Mean Reciprocal Rank) - posição do primeiro item relevante
            train_mrr = reciprocal_rank(
                self.model,
                train,
                user_features=user_features,
                item_features=item_features,
                num_threads=num_threads
            ).mean()
            
            test_mrr = reciprocal_rank(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                num_threads=num_threads
            ).mean()
            
            # Compilar todas as métricas (MLflow não aceita @ nos nomes)
            metrics = {
                # Precision
                "train_precision_at_10": float(train_precision_10),
                "test_precision_at_5": float(test_precision_5),
                "test_precision_at_10": float(test_precision_10),
                "test_precision_at_20": float(test_precision_20),
                
                # Recall
                "train_recall_at_10": float(train_recall_10),
                "test_recall_at_5": float(test_recall_5),
                "test_recall_at_10": float(test_recall_10),
                
                # AUC
                "train_auc": float(train_auc),
                "test_auc": float(test_auc),
                
                # MRR
                "train_mrr": float(train_mrr),
                "test_mrr": float(test_mrr),
            }
            
            # Calcular F1-Score (média harmônica de Precision e Recall)
            if test_precision_10 > 0 and test_recall_10 > 0:
                test_f1_10 = 2 * (test_precision_10 * test_recall_10) / (test_precision_10 + test_recall_10)
                metrics["test_f1_at_10"] = float(test_f1_10)
            
            if test_precision_5 > 0 and test_recall_5 > 0:
                test_f1_5 = 2 * (test_precision_5 * test_recall_5) / (test_precision_5 + test_recall_5)
                metrics["test_f1_at_5"] = float(test_f1_5)
            
            # Registrar métricas no MLflow
            if mlflow_run is not None:
                try:
                    mlflow.log_metrics(metrics)
                    print(f"📊 MLflow: Métricas registradas:")
                    print(f"   Precision@10: {test_precision_10:.4f}, Recall@10: {test_recall_10:.4f}")
                    print(f"   AUC: {test_auc:.4f}, MRR: {test_mrr:.4f}")
                    if "test_f1_at_10" in metrics:
                        print(f"   F1@10: {metrics['test_f1_at_10']:.4f}")
                except Exception as e:
                    print(f"⚠️  Erro ao registrar métricas no MLflow: {e}")
        
        except ValueError as e:
            # O ValueError é lançado quando há overlap entre treino e teste
            # Solução: calcular métricas SEM passar train_interactions (menos preciso, mas funciona)
            print(f"⚠️  Overlap detectado entre treino e teste: {str(e)[:100]}")
            print(f"   Calculando métricas sem train_interactions (menos preciso, mas funcional)")
            
            try:
                # Calcular métricas básicas SEM train_interactions para evitar o ValueError
                train_precision_10 = precision_at_k(
                    self.model, train, 
                    user_features=user_features, 
                    item_features=item_features, 
                    k=10, 
                    num_threads=num_threads
                ).mean()
                
                # Para teste, NÃO passar train_interactions (isso evita o ValueError)
                test_precision_10 = precision_at_k(
                    self.model, test, 
                    user_features=user_features, 
                    item_features=item_features, 
                    k=10, 
                    num_threads=num_threads
                ).mean()
                
                train_auc = auc_score(
                    self.model, train, 
                    user_features=user_features, 
                    item_features=item_features, 
                    num_threads=num_threads
                ).mean()
                
                test_auc = auc_score(
                    self.model, test, 
                    user_features=user_features, 
                    item_features=item_features, 
                    num_threads=num_threads
                ).mean()
                
                metrics = {
                    "evaluation_warning": 1.0,  # Flag indicando overlap
                    "train_precision_at_10": float(train_precision_10),
                    "test_precision_at_10": float(test_precision_10),
                    "train_auc": float(train_auc),
                    "test_auc": float(test_auc),
                }
                
                # Registrar métricas no MLflow
                if mlflow_run is not None:
                    try:
                        mlflow.log_metrics(metrics)
                        mlflow.log_param("evaluation_warning_message", str(e)[:250])
                        mlflow.log_param("evaluation_method", "without_train_interactions")
                        print(f"⚠️  Métricas calculadas: Precision@10={test_precision_10:.4f}, AUC={test_auc:.4f}")
                        print(f"   (Overlap registrado, métricas podem não ser 100% precisas)")
                    except Exception as mlflow_err:
                        print(f"⚠️  Erro ao registrar no MLflow: {mlflow_err}")
                
            except Exception as metric_err:
                # Se ainda assim falhar, usar apenas o flag de warning
                print(f"⚠️  Não foi possível calcular métricas: {metric_err}")
                metrics = {"evaluation_warning": 1.0}
                if mlflow_run is not None:
                    try:
                        mlflow.log_metric("evaluation_warning", 1.0)
                        mlflow.log_param("evaluation_warning_message", str(e)[:250])
                        mlflow.log_param("evaluation_error", str(metric_err)[:250])
                    except:
                        pass
        
        # Salvar modelo no MLflow (sempre, mesmo com warnings)
        if mlflow_run is not None:
            try:
                # Salvar modelo usando MLflow
                # Nota: MLflow não tem suporte nativo para LightFM, então salvamos manualmente
                import tempfile
                with tempfile.TemporaryDirectory() as tmpdir:
                    model_path = Path(tmpdir) / "lightfm_model.pkl"
                    joblib.dump({
                        'model': self.model,
                        'dataset': self.dataset,
                        'user_id_map': self.user_id_map,
                        'item_id_map': self.item_id_map,
                        'reverse_user_map': self.reverse_user_map,
                        'reverse_item_map': self.reverse_item_map
                    }, model_path)
                    
                    # Salvar modelo usando pyfunc para poder registrar no Model Registry
                    # Criar wrapper simples para LightFM
                    class LightFMWrapper(mlflow.pyfunc.PythonModel):
                        def load_context(self, context):
                            import joblib
                            self.model_data = joblib.load(context.artifacts["model"])
                        
                        def predict(self, context, model_input):
                            """
                            Método predict para MLflow (placeholder - não usado para inferência direta)
                            
                            O LightFM usa seus próprios métodos para recomendações.
                            Este método é necessário apenas para o wrapper pyfunc do MLflow.
                            """
                            return model_input
                    
                    # Salvar usando pyfunc.log_model (usando 'name' em vez de 'artifact_path' deprecated)
                    mlflow.pyfunc.log_model(
                        name="model",  # Usar 'name' em vez de 'artifact_path' (deprecated)
                        python_model=LightFMWrapper(),
                        artifacts={"model": str(model_path)},
                        input_example={"user_id": 1, "item_ids": [1, 2, 3]}  # Exemplo de input para inferir signature
                    )
                    print(f"💾 MLflow: Modelo salvo como pyfunc (pode ser registrado no Model Registry)")
                
                # NÃO registrar automaticamente no Model Registry
                # Apenas salvar o run - o melhor modelo será selecionado e registrado depois
                run_id = mlflow_run.info.run_id
                print(f"💾 MLflow: Run salvo (ID: {run_id[:8]}...)")
                print(f"   O modelo será comparado com outros treinos e o melhor será selecionado automaticamente")
                
                # Verificar warnings
                if "evaluation_warning" in metrics:
                    print(f"⚠️  Modelo tem evaluation warning (sobreposição treino/teste)")
                    print(f"   Será considerado na seleção mas com menor prioridade")
                else:
                    print(f"✅ Modelo sem warnings - prioridade na seleção")
                
                # Verificar se ESTE treino é melhor que o modelo em produção
                try:
                    from app.core.mlflow_model_selector import evaluate_and_register_if_best
                    print(f"🔍 Comparando com modelo em produção...")
                    evaluate_and_register_if_best(
                        new_run_id=run_id,
                        metric_name="test_precision_at_10",
                        metric_value=metrics.get("test_precision_at_10", 0.0)
                    )
                except Exception as selector_err:
                    print(f"⚠️  Erro ao avaliar modelo: {selector_err}")
                    print(f"   Run salvo para comparação futura")
                
            except Exception as e:
                import traceback
                print(f"⚠️  Erro ao salvar modelo no MLflow: {e}")
                print(f"   Traceback: {traceback.format_exc()}")
            finally:
                if mlflow_run is not None:
                    try:
                        mlflow.end_run()
                        print(f"✅ MLflow: Experimento finalizado (Run ID: {mlflow_run.info.run_id})")
                    except Exception as e:
                        print(f"⚠️  Erro ao finalizar run do MLflow: {e}")

        return metrics
    
    def predict(
        self,
        user_id: int,
        item_ids: Optional[List[int]] = None,
        num_items: int = 10,
        db: Session = None
    ) -> List[Tuple[int, float]]:
        """
        Gera recomendações para um usuário
        
        Args:
            user_id: ID do usuário no banco de dados
            item_ids: Lista de IDs de itens para avaliar (None = todos)
            num_items: Número de recomendações a retornar
            db: Sessão do banco de dados (necessária se usar features)
            
        Returns:
            Lista de tuplas (item_id, score) ordenada por score
        """
        if self.model is None:
            raise ValueError("Modelo não treinado. Execute train() primeiro.")
        
        # Converter user_id para índice LightFM
        if user_id not in self.user_id_map:
            # Cold start - usuário novo sem interações
            # Retornar recomendações baseadas apenas em features se disponível
            if db is not None:
                return self._cold_start_predict(user_id, num_items, db)
            else:
                raise ValueError(f"Usuário {user_id} não encontrado no modelo")
        
        user_idx = self.user_id_map[user_id]
        
        # Obter features do usuário se disponível
        user_features = None
        if db is not None:
            user_features_map = self._load_user_features(db)
            if user_id in user_features_map:
                # Construir features para este usuário específico
                stmt_prefs = select(Preferencias.id)
                prefs_result = db.execute(stmt_prefs)
                all_prefs = prefs_result.all()
                feature_names = [f"pref_{p.id}" for p in all_prefs]
                user_feats = [f"pref_{feat_id}" for feat_id, _ in user_features_map[user_id]]
                # Nota: Esta é uma simplificação - em produção, construir matriz completa
                user_features = None  # Simplificado por enquanto
        
        # Determinar itens para avaliar
        if item_ids is None:
            # Avaliar todos os itens
            item_indices = list(range(len(self.reverse_item_map)))
        else:
            # Avaliar apenas itens especificados
            item_indices = [
                self.item_id_map[iid] for iid in item_ids
                if iid in self.item_id_map
            ]
        
        # Prever scores
        scores = self.model.predict(
            user_ids=user_idx,
            item_ids=item_indices,
            user_features=user_features
        )
        
        # Mapear de volta para IDs do banco
        results = []
        for idx, score in zip(item_indices, scores):
            idx_int = int(idx.item() if hasattr(idx, 'item') else idx)
            item_id = self.reverse_item_map[idx_int]
            item_id_int = int(item_id.item() if hasattr(item_id, 'item') else item_id)
            score_float = float(score.item() if hasattr(score, 'item') else score)
            results.append((item_id_int, score_float))
        
        # Ordenar por score e retornar top N
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:num_items]
    
    def _cold_start_predict(
        self,
        user_id: int,
        num_items: int,
        db: Session
    ) -> List[Tuple[int, float]]:
        """
        Predição para cold start (usuário novo sem interações)
        Usa apenas features (CBF)
        """
        # Carregar preferências do usuário (usando select para evitar colunas que não existem)
        from sqlalchemy import select
        stmt = select(
            UsuarioPreferencia.id_preferencia
        ).filter(UsuarioPreferencia.id_usuario == user_id)
        
        result = db.execute(stmt)
        user_prefs_rows = result.all()
        
        if not user_prefs_rows:
            # Sem preferências - retornar itens populares
            popular_items = db.query(
                RecomendacaoEstabelecimento.id_lugar,
                db.func.avg(RecomendacaoEstabelecimento.score).label('avg_score')
            ).group_by(
                RecomendacaoEstabelecimento.id_lugar
            ).order_by(
                db.func.avg(RecomendacaoEstabelecimento.score).desc()
            ).limit(num_items).all()
            
            return [(item.id_lugar, float(item.avg_score)) for item in popular_items]
        
        # Buscar estabelecimentos com features similares
        user_pref_ids = {row.id_preferencia for row in user_prefs_rows}
        
        # Buscar estabelecimentos que têm essas preferências
        stmt_matching = select(
            EstabelecimentoPreferencia.id_estabelecimento
        ).filter(
            EstabelecimentoPreferencia.id_preferencia.in_(user_pref_ids)
        ).distinct()
        
        matching_result = db.execute(stmt_matching)
        matching_items = matching_result.all()
        
        if not matching_items:
            return []
        
        # Calcular scores baseados em similaridade de features
        results = []
        for row in matching_items:
            item_id = row.id_estabelecimento
            
            # Buscar preferências do estabelecimento
            stmt_item = select(
                EstabelecimentoPreferencia.id_preferencia
            ).filter(
                EstabelecimentoPreferencia.id_estabelecimento == item_id
            )
            
            item_result = db.execute(stmt_item)
            item_prefs_rows = item_result.all()
            item_pref_ids = {row.id_preferencia for row in item_prefs_rows}
            
            # Calcular interseção de preferências
            common_prefs = user_pref_ids.intersection(item_pref_ids)
            score = len(common_prefs) / max(len(user_pref_ids), 1)
            
            results.append((item_id, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:num_items]
    
    def get_similar_users(
        self,
        user_id: int,
        num_users: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Encontra usuários similares (user-user similarity)
        
        Args:
            user_id: ID do usuário no banco de dados
            num_users: Número de usuários similares a retornar
            
        Returns:
            Lista de tuplas (user_id, similarity_score)
        """
        if self.model is None:
            raise ValueError("Modelo não treinado")
        
        if user_id not in self.user_id_map:
            raise ValueError(f"Usuário {user_id} não encontrado no modelo")
        
        user_idx = self.user_id_map[user_id]
        # Garantir que user_idx é int Python nativo
        user_idx = int(user_idx.item() if hasattr(user_idx, 'item') else user_idx)
        
        # Obter embeddings de usuários
        user_biases, user_embeddings = self.model.get_user_representations()
        
        # Normalizar embeddings para cálculo de similaridade de cosseno
        user_embeddings = user_embeddings / np.linalg.norm(user_embeddings, axis=1, keepdims=True)
        
        # Embedding do usuário de referência
        target_embedding = user_embeddings[user_idx]
        
        # Calcular similaridade de cosseno com todos os outros usuários
        similarities = np.dot(user_embeddings, target_embedding)
        
        # Remover o próprio usuário
        similarities[user_idx] = -np.inf
        
        # Obter top N
        top_indices = np.argsort(similarities)[::-1][:num_users]
        
        results = []
        for idx in top_indices:
            # Converter idx para int Python nativo
            idx_int = int(idx.item() if hasattr(idx, 'item') else idx)
            # Verificar se o índice existe no mapeamento
            if idx_int not in self.reverse_user_map:
                continue  # Pular índices que não existem no mapeamento
            # Obter user_id e converter para int Python nativo
            user_id = self.reverse_user_map[idx_int]
            user_id_int = int(user_id.item() if hasattr(user_id, 'item') else user_id)
            # Obter score e converter para float Python nativo
            score = similarities[idx_int]
            score_float = float(score.item() if hasattr(score, 'item') else score)
            results.append((user_id_int, score_float))
        
        return results

    def get_similar_items(
        self,
        item_id: int,
        num_items: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Encontra itens similares (item-item similarity)
        
        Args:
            item_id: ID do item no banco de dados
            num_items: Número de itens similares a retornar
            
        Returns:
            Lista de tuplas (item_id, similarity_score)
        """
        if self.model is None:
            raise ValueError("Modelo não treinado")
        
        if item_id not in self.item_id_map:
            raise ValueError(f"Item {item_id} não encontrado no modelo")
        
        item_idx = self.item_id_map[item_id]
        
        # Obter embedding do item
        item_biases, item_embeddings = self.model.get_item_representations()
        item_embedding = item_embeddings[item_idx]
        
        # Calcular similaridade com todos os outros itens
        all_item_embeddings = item_embeddings
        similarities = np.dot(all_item_embeddings, item_embedding)
        
        # Remover o próprio item
        similarities[item_idx] = -np.inf
        
        # Obter top N
        top_indices = np.argsort(similarities)[::-1][:num_items]
        
        results = []
        for idx in top_indices:
            # Converter idx para int Python nativo
            idx_int = int(idx.item() if hasattr(idx, 'item') else idx)
            # Obter item_id e converter para int Python nativo
            item_id = self.reverse_item_map[idx_int]
            item_id_int = int(item_id.item() if hasattr(item_id, 'item') else item_id)
            # Obter score e converter para float Python nativo
            score = similarities[idx_int]
            score_float = float(score.item() if hasattr(score, 'item') else score)
            results.append((item_id_int, score_float))
        
        return results
    
    def save_model(self, filename: str = "lightfm_model.pkl"):
        """Salva o modelo treinado"""
        if self.model is None:
            raise ValueError("Nenhum modelo para salvar")
        
        model_path = self.model_dir / filename
        joblib.dump({
            'model': self.model,
            'dataset': self.dataset,
            'user_id_map': self.user_id_map,
            'item_id_map': self.item_id_map,
            'reverse_user_map': self.reverse_user_map,
            'reverse_item_map': self.reverse_item_map
        }, model_path)
    
    def load_model(self, filename: str = "lightfm_model.pkl"):
        """Carrega um modelo salvo"""
        model_path = self.model_dir / filename
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        try:
            # Tentar carregar com tratamento de compatibilidade NumPy
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                # Usar pickle_load_compat para lidar com incompatibilidades de versão
                try:
                    data = joblib.load(model_path)
                except (ValueError, AttributeError) as e:
                    # Se houver erro de compatibilidade NumPy, tentar com pickle diretamente
                    import pickle
                    with open(model_path, 'rb') as f:
                        data = pickle.load(f)
            
            self.model = data['model']
            self.dataset = data['dataset']
            self.user_id_map = data['user_id_map']
            self.item_id_map = data['item_id_map']
            self.reverse_user_map = data['reverse_user_map']
            self.reverse_item_map = data['reverse_item_map']
        except Exception as e:
            error_msg = str(e)
            if "BitGenerator" in error_msg or "MT19937" in error_msg:
                raise ValueError(
                    f"Erro de compatibilidade NumPy ao carregar modelo. "
                    f"O modelo foi salvo com uma versão diferente do NumPy. "
                    f"Recomendação: Retreine o modelo com a versão atual do NumPy. "
                    f"Erro original: {error_msg}"
                )
            raise ValueError(f"Erro ao carregar modelo: {error_msg}")
    
    def load_model_from_mlflow(self, use_production: bool = True, run_id: Optional[str] = None):
        """
        Carrega modelo do MLflow
        
        Args:
            use_production: Se True, tenta carregar modelo marcado como Production.
                           Se False ou se não encontrar, carrega o melhor modelo por métrica.
            run_id: ID específico do run para carregar (opcional)
        
        Returns:
            Dict com informações do modelo carregado
        """
        if not MLFLOW_AVAILABLE:
            raise ValueError("MLflow não está disponível. Instale com: pip install mlflow")
        
        try:
            client = get_client()
            if client is None:
                raise ValueError("Não foi possível criar cliente MLflow")
            
            model_path = None
            model_info = {}
            
            if run_id:
                # Carregar run específico
                run = client.get_run(run_id)
                # Tentar baixar o modelo (pode estar em diferentes caminhos)
                try:
                    model_path = mlflow.artifacts.download_artifacts(
                        run_id=run_id,
                        artifact_path="model"
                    )
                    # Se for diretório, procurar .pkl
                    if Path(model_path).is_dir():
                        pkl_files = list(Path(model_path).glob("*.pkl"))
                        if pkl_files:
                            model_path = str(pkl_files[0])
                        else:
                            # Tentar baixar diretamente o arquivo
                            model_path = mlflow.artifacts.download_artifacts(
                                run_id=run_id,
                                artifact_path="model/lightfm_model.pkl"
                            )
                except:
                    # Tentar via pyfunc
                    try:
                        model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
                        # Extrair o caminho do modelo pickle do pyfunc
                        model_path = Path(model._model_impl.context.artifacts["model"])
                    except:
                        raise FileNotFoundError(f"Modelo não encontrado no run {run_id}")
                
                model_info = {
                    "run_id": run_id,
                    "source": "specific_run",
                    "metrics": dict(run.data.metrics),
                    "params": dict(run.data.params)
                }
            elif use_production:
                # Tentar carregar modelo em produção primeiro
                production_version = get_production_model_version()
                if production_version:
                    try:
                        model_version = client.get_model_version(MODEL_NAME, production_version)
                        run_id = model_version.run_id
                        
                        # Tentar carregar via pyfunc primeiro
                        try:
                            model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{production_version}")
                            model_path = Path(model._model_impl.context.artifacts["model"])
                        except:
                            # Fallback: baixar diretamente do run
                            model_path = mlflow.artifacts.download_artifacts(
                                run_id=run_id,
                                artifact_path="model"
                            )
                            if Path(model_path).is_dir():
                                pkl_files = list(Path(model_path).glob("*.pkl"))
                                if pkl_files:
                                    model_path = str(pkl_files[0])
                        
                        run = client.get_run(run_id)
                        model_info = {
                            "run_id": run_id,
                            "version": production_version,
                            "source": "production",
                            "metrics": dict(run.data.metrics),
                            "params": dict(run.data.params)
                        }
                    except Exception as prod_err:
                        print(f"⚠️  Erro ao carregar modelo em produção: {prod_err}")
                        print(f"   Tentando carregar melhor modelo por métrica...")
                        use_production = False  # Fallback para melhor modelo
                
                if not model_path:
                    # Se não encontrou em produção, buscar melhor por métrica
                    use_production = False
            
            if not model_path or (not use_production and not run_id):
                # Carregar melhor modelo por métrica
                best_run_id = get_best_model_run()
                if not best_run_id:
                    # Se não encontrar por métrica, pegar o último run registrado
                    from app.core.mlflow_config import EXPERIMENT_NAME
                    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
                    if experiment:
                        runs = client.search_runs(
                            experiment_ids=[experiment.experiment_id],
                            max_results=1,
                            order_by=["start_time DESC"]
                        )
                        if runs:
                            best_run_id = runs[0].info.run_id
                
                if best_run_id:
                    try:
                        # Tentar carregar via pyfunc
                        try:
                            model = mlflow.pyfunc.load_model(f"runs:/{best_run_id}/model")
                            model_path = Path(model._model_impl.context.artifacts["model"])
                        except:
                            # Fallback: baixar diretamente
                            model_path = mlflow.artifacts.download_artifacts(
                                run_id=best_run_id,
                                artifact_path="model"
                            )
                            if Path(model_path).is_dir():
                                pkl_files = list(Path(model_path).glob("*.pkl"))
                                if pkl_files:
                                    model_path = str(pkl_files[0])
                        
                        run = client.get_run(best_run_id)
                        model_info = {
                            "run_id": best_run_id,
                            "source": "best_metric",
                            "metrics": dict(run.data.metrics),
                            "params": dict(run.data.params)
                        }
                    except Exception as e:
                        raise FileNotFoundError(f"Erro ao carregar melhor modelo: {e}")
                else:
                    raise FileNotFoundError("Nenhum modelo encontrado no MLflow")
            
            # Se model_path for um Path object, converter para string
            if isinstance(model_path, Path):
                model_path = str(model_path)
            
            if not model_path or not Path(model_path).exists():
                raise FileNotFoundError(f"Artefato do modelo não encontrado: {model_path}")
            
            # Carregar modelo do arquivo
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                data = joblib.load(model_path)
            
            self.model = data['model']
            self.dataset = data['dataset']
            self.user_id_map = data['user_id_map']
            self.item_id_map = data['item_id_map']
            self.reverse_user_map = data['reverse_user_map']
            self.reverse_item_map = data['reverse_item_map']
            
            print(f"✅ Modelo carregado do MLflow: {model_info.get('source', 'unknown')}")
            if 'metrics' in model_info:
                precision = model_info['metrics'].get('test_precision_at_10', 'N/A')
                auc = model_info['metrics'].get('test_auc', 'N/A')
                try:
                    if precision != 'N/A' and precision is not None:
                        # Converter para float se necessário
                        if hasattr(precision, 'value'):
                            precision = float(precision.value)
                        else:
                            precision = float(precision)
                        precision_str = f"{precision:.4f}"
                    else:
                        precision_str = 'N/A'
                    
                    if auc != 'N/A' and auc is not None:
                        # Converter para float se necessário
                        if hasattr(auc, 'value'):
                            auc = float(auc.value)
                        else:
                            auc = float(auc)
                        auc_str = f"{auc:.4f}"
                    else:
                        auc_str = 'N/A'
                    
                    print(f"   Métricas: Precision@10={precision_str}, AUC={auc_str}")
                except (ValueError, TypeError) as e:
                    print(f"   Métricas: Precision@10={precision}, AUC={auc} (não foi possível formatar)")
            
            return model_info
            
        except Exception as e:
            import traceback
            error_msg = f"Erro ao carregar modelo do MLflow: {str(e)}"
            print(f"   Traceback: {traceback.format_exc()}")
            raise ValueError(error_msg)
    
    def is_model_loaded(self) -> bool:
        """Verifica se o modelo está carregado"""
        return self.model is not None and self.dataset is not None

