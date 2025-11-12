"""
Serviço LightFM - Sistema de Recomendação Híbrido
Combina Content-Based Filtering (CBF) e Collaborative Filtering (CF)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.cross_validation import random_train_test_split
from lightfm.evaluation import precision_at_k, auc_score
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
        num_threads: int = 4
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
            
        Returns:
            Dict com métricas de avaliação
        """
        # Construir dataset
        result = self._build_dataset(db, use_features=use_features)
        
        if use_features:
            interactions, weights, user_features, item_features = result
        else:
            interactions, weights = result
            user_features, item_features = None, None
        
        # Dividir em treino e teste
        train, test = random_train_test_split(
            interactions,
            test_percentage=0.2,
            random_state=42
        )
        
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
        
        # Avaliar
        metrics = {}
        try:
            train_precision = precision_at_k(
                self.model,
                train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
            test_precision = precision_at_k(
                self.model,
                test,
                train_interactions=train,
                user_features=user_features,
                item_features=item_features,
                k=10,
                num_threads=num_threads
            ).mean()
            
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
            
            metrics = {
                "train_precision@10": float(train_precision),
                "test_precision@10": float(test_precision),
                "train_auc": float(train_auc),
                "test_auc": float(test_auc)
            }
        except ValueError as e:
            print(f"Aviso durante a avaliação: {e}")
            metrics = {"evaluation_warning": str(e)}

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
            data = joblib.load(model_path)
            self.model = data['model']
            self.dataset = data['dataset']
            self.user_id_map = data['user_id_map']
            self.item_id_map = data['item_id_map']
            self.reverse_user_map = data['reverse_user_map']
            self.reverse_item_map = data['reverse_item_map']
        except Exception as e:
            raise ValueError(f"Erro ao carregar modelo: {e}")
    
    def is_model_loaded(self) -> bool:
        """Verifica se o modelo está carregado"""
        return self.model is not None and self.dataset is not None

