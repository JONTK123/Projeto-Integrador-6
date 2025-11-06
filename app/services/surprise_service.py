"""
Serviço Surprise - Sistema de Recomendação Collaborative Filtering
Biblioteca focada em algoritmos de CF puro
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from surprise import Dataset, Reader, SVD, KNNBasic, KNNWithMeans, KNNWithZScore, BaselineOnly, CoClustering
from surprise.model_selection import train_test_split, cross_validate
from surprise import accuracy
import joblib
import os
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.recomendacao_estabelecimento import RecomendacaoEstabelecimento


class SurpriseService:
    """
    Serviço para treinamento e predição usando Surprise
    
    Algoritmos disponíveis:
    - SVD: Singular Value Decomposition (Matrix Factorization)
    - KNNBasic: K-Nearest Neighbors básico
    - KNNWithMeans: KNN com média dos ratings
    - KNNWithZScore: KNN com normalização Z-score
    - BaselineOnly: Baseline (média global + bias de usuário/item)
    - CoClustering: Co-clustering
    
    Características:
    - Focado em Collaborative Filtering puro
    - Não suporta features (apenas ratings)
    - Excelente para comparação e baseline
    - Mais simples que LightFM para CF puro
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Inicializa o serviço Surprise
        
        Args:
            model_dir: Diretório para salvar/carregar modelos
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.trainset = None
        self.testset = None
        self.algorithm_name = None
        
    def _load_data_from_db(self, db: Session):
        """
        Carrega dados do banco de dados no formato Surprise
        
        Returns:
            Lista de tuplas (user_id, item_id, rating)
        """
        interactions = db.query(RecomendacaoEstabelecimento).all()
        
        if not interactions:
            return []
        
        data = []
        for interaction in interactions:
            data.append((
                str(interaction.id_usuario),
                str(interaction.id_lugar),
                float(interaction.score)
            ))
        
        # Verificar se há dados suficientes
        if len(data) < 5:
            raise ValueError(f"Dados insuficientes para treinamento. Necessário pelo menos 5 interações, encontrado {len(data)}")
        
        return data
    
    def _create_dataset(self, db: Session):
        """
        Cria dataset Surprise a partir do banco de dados
        
        Returns:
            Dataset Surprise
        """
        data = self._load_data_from_db(db)
        
        if not data:
            raise ValueError("Nenhuma interação encontrada no banco de dados")
        
        # Criar DataFrame do pandas
        df = pd.DataFrame(data, columns=['user_id', 'item_id', 'rating'])
        
        # Definir escala de ratings (1-5)
        reader = Reader(rating_scale=(1, 5))
        
        # Criar dataset a partir do DataFrame
        dataset = Dataset.load_from_df(df, reader)
        
        return dataset
    
    def train(
        self,
        db: Session,
        algorithm: str = "svd",
        test_size: float = 0.2,
        random_state: int = 42,
        **kwargs
    ) -> Dict[str, float]:
        """
        Treina o modelo Surprise
        
        Args:
            db: Sessão do banco de dados
            algorithm: Algoritmo a usar ('svd', 'knn_basic', 'knn_means', 'knn_zscore', 'baseline', 'coclustering')
            test_size: Proporção de dados para teste
            random_state: Seed para reprodutibilidade
            **kwargs: Parâmetros específicos do algoritmo
            
        Returns:
            Dict com métricas de avaliação
        """
        # Criar dataset
        dataset = self._create_dataset(db)
        
        # Selecionar algoritmo
        algorithm_map = {
            'svd': SVD,
            'knn_basic': KNNBasic,
            'knn_means': KNNWithMeans,
            'knn_zscore': KNNWithZScore,
            'baseline': BaselineOnly,
            'coclustering': CoClustering
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Algoritmo '{algorithm}' não suportado. Use: {list(algorithm_map.keys())}")
        
        algorithm_class = algorithm_map[algorithm]
        self.algorithm_name = algorithm
        
        # Parâmetros padrão por algoritmo
        default_params = {
            'svd': {
                'n_factors': kwargs.get('n_factors', 50),
                'n_epochs': kwargs.get('n_epochs', 20),
                'lr_all': kwargs.get('lr_all', 0.005),
                'reg_all': kwargs.get('reg_all', 0.02),
                'random_state': random_state
            },
            'knn_basic': {
                'k': kwargs.get('k', 40),
                'sim_options': kwargs.get('sim_options', {
                    'name': 'cosine',
                    'user_based': True
                }),
                'random_state': random_state
            },
            'knn_means': {
                'k': kwargs.get('k', 40),
                'sim_options': kwargs.get('sim_options', {
                    'name': 'cosine',
                    'user_based': True
                }),
                'random_state': random_state
            },
            'knn_zscore': {
                'k': kwargs.get('k', 40),
                'sim_options': kwargs.get('sim_options', {
                    'name': 'cosine',
                    'user_based': True
                }),
                'random_state': random_state
            },
            'baseline': {
                'method': kwargs.get('method', 'als'),
                'n_epochs': kwargs.get('n_epochs', 10),
                'reg_u': kwargs.get('reg_u', 15),
                'reg_i': kwargs.get('reg_i', 10),
                'random_state': random_state
            },
            'coclustering': {
                'n_cltr_u': kwargs.get('n_cltr_u', 3),
                'n_cltr_i': kwargs.get('n_cltr_i', 3),
                'n_epochs': kwargs.get('n_epochs', 20),
                'random_state': random_state
            }
        }
        
        params = default_params[algorithm]
        params.update({k: v for k, v in kwargs.items() if k not in params})
        
        self.model = algorithm_class(**params)
        
        # Dividir em treino e teste
        self.trainset, self.testset = train_test_split(
            dataset,
            test_size=test_size,
            random_state=random_state
        )
        
        # Treinar
        self.model.fit(self.trainset)
        
        # Avaliar
        predictions = self.model.test(self.testset)
        
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        
        # Calcular precision@k e recall@k manualmente
        # (Surprise não tem built-in, então simplificamos)
        top_n = self._get_top_n(predictions, n=10)
        
        metrics = {
            "rmse": float(rmse),
            "mae": float(mae),
            "algorithm": algorithm
        }
        
        return metrics
    
    def _get_top_n(self, predictions, n=10):
        """
        Retorna top N recomendações para cada usuário
        """
        top_n = {}
        
        for uid, iid, true_r, est, _ in predictions:
            if uid not in top_n:
                top_n[uid] = []
            top_n[uid].append((iid, est))
        
        # Ordenar e pegar top N
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        
        return top_n
    
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
            
        Returns:
            Lista de tuplas (item_id, score) ordenada por score
        """
        if self.model is None or self.trainset is None:
            raise ValueError("Modelo não treinado. Execute train() primeiro.")
        
        user_id_str = str(user_id)
        
        # Verificar se usuário existe no trainset
        try:
            inner_user_id = self.trainset.to_inner_uid(user_id_str)
        except ValueError:
            # Cold start - usuário novo
            if db is not None:
                return self._cold_start_predict(user_id, num_items, db)
            else:
                raise ValueError(f"Usuário {user_id} não encontrado no modelo")
        
        # Determinar itens para avaliar
        if item_ids is None:
            # Avaliar todos os itens no trainset
            all_items = [self.trainset.to_raw_iid(iid) for iid in self.trainset.all_items()]
            item_ids = [int(iid) for iid in all_items]
        else:
            # Filtrar apenas itens que existem no trainset
            valid_item_ids = []
            for iid in item_ids:
                try:
                    self.trainset.to_inner_iid(str(iid))
                    valid_item_ids.append(iid)
                except ValueError:
                    continue
            item_ids = valid_item_ids
        
        # Prever scores
        predictions = []
        for item_id in item_ids:
            try:
                pred = self.model.predict(user_id_str, str(item_id))
                predictions.append((item_id, pred.est))
            except Exception:
                continue
        
        # Ordenar por score e retornar top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:num_items]
    
    def _cold_start_predict(
        self,
        user_id: int,
        num_items: int,
        db: Session
    ) -> List[Tuple[int, float]]:
        """
        Predição para cold start (usuário novo sem interações)
        Retorna itens mais populares (média de ratings)
        """
        popular_items = db.query(
            RecomendacaoEstabelecimento.id_lugar,
            db.func.avg(RecomendacaoEstabelecimento.score).label('avg_score'),
            db.func.count(RecomendacaoEstabelecimento.id_lugar).label('count')
        ).group_by(
            RecomendacaoEstabelecimento.id_lugar
        ).having(
            db.func.count(RecomendacaoEstabelecimento.id_lugar) >= 3  # Mínimo de ratings
        ).order_by(
            db.func.avg(RecomendacaoEstabelecimento.score).desc()
        ).limit(num_items).all()
        
        return [(item.id_lugar, float(item.avg_score)) for item in popular_items]
    
    def get_similar_items(
        self,
        item_id: int,
        num_items: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Encontra itens similares (item-item similarity)
        Funciona apenas para algoritmos KNN
        """
        if self.model is None or self.trainset is None:
            raise ValueError("Modelo não treinado")
        
        if not hasattr(self.model, 'get_neighbors'):
            raise ValueError("Algoritmo não suporta similaridade item-item. Use KNN.")
        
        item_id_str = str(item_id)
        
        try:
            inner_item_id = self.trainset.to_inner_iid(item_id_str)
        except ValueError:
            raise ValueError(f"Item {item_id} não encontrado no modelo")
        
        # Obter vizinhos mais próximos
        neighbors = self.model.get_neighbors(inner_item_id, k=num_items)
        
        # Converter de volta para IDs do banco
        results = [
            (int(self.trainset.to_raw_iid(nid)), 1.0)  # Similaridade simplificada
            for nid in neighbors
        ]
        
        return results
    
    def cross_validate(
        self,
        db: Session,
        algorithm: str = "svd",
        cv: int = 5,
        **kwargs
    ) -> Dict[str, float]:
        """
        Realiza validação cruzada
        
        Args:
            db: Sessão do banco de dados
            algorithm: Algoritmo a usar
            cv: Número de folds
            **kwargs: Parâmetros do algoritmo
            
        Returns:
            Dict com métricas médias de validação cruzada
        """
        dataset = self._create_dataset(db)
        
        algorithm_map = {
            'svd': SVD,
            'knn_basic': KNNBasic,
            'knn_means': KNNWithMeans,
            'knn_zscore': KNNWithZScore,
            'baseline': BaselineOnly,
            'coclustering': CoClustering
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Algoritmo '{algorithm}' não suportado")
        
        algorithm_class = algorithm_map[algorithm]
        model = algorithm_class(**kwargs)
        
        cv_results = cross_validate(
            model,
            dataset,
            measures=['RMSE', 'MAE'],
            cv=cv,
            verbose=False
        )
        
        return {
            'test_rmse_mean': float(cv_results['test_rmse'].mean()),
            'test_rmse_std': float(cv_results['test_rmse'].std()),
            'test_mae_mean': float(cv_results['test_mae'].mean()),
            'test_mae_std': float(cv_results['test_mae'].std())
        }
    
    def save_model(self, filename: str = "surprise_model.pkl"):
        """Salva o modelo treinado"""
        if self.model is None:
            raise ValueError("Nenhum modelo para salvar")
        
        model_path = self.model_dir / filename
        joblib.dump({
            'model': self.model,
            'trainset': self.trainset,
            'testset': self.testset,
            'algorithm': self.algorithm_name
        }, model_path)
    
    def load_model(self, filename: str = "surprise_model.pkl"):
        """Carrega um modelo salvo"""
        model_path = self.model_dir / filename
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        data = joblib.load(model_path)
        self.model = data['model']
        self.trainset = data['trainset']
        self.testset = data.get('testset')
        self.algorithm_name = data.get('algorithm')

