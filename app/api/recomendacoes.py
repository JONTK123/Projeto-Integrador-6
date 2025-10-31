from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações LightFM"])


class RecomendacaoItem(BaseModel):
    """Schema para item de recomendação"""
    estabelecimento_id: int
    score: float
    razao: Optional[str] = None


class RecomendacaoResponse(BaseModel):
    """Schema de resposta de recomendações"""
    usuario_id: int
    recomendacoes: List[RecomendacaoItem]
    tipo: str  # 'hybrid', 'cbf', 'cf'


@router.get("/usuario/{usuario_id}", response_model=RecomendacaoResponse)
def get_recomendacoes_usuario(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações a retornar"),
    tipo: str = Query("hybrid", description="Tipo de recomendação: 'hybrid', 'cbf', 'cf'"),
    db: Session = Depends(get_db)
):
    """
    Obter recomendações personalizadas para um usuário
    
    - **usuario_id**: ID do usuário
    - **top_n**: Quantidade de recomendações (padrão: 10)
    - **tipo**: Tipo de filtragem
        - 'hybrid': Combinação de CBF e CF (padrão do LightFM)
        - 'cbf': Content-Based Filtering (baseado em características)
        - 'cf': Collaborative Filtering (baseado em comportamento de usuários similares)
    """
    # TODO: Implementar lógica do modelo LightFM
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/estabelecimento/{estabelecimento_id}/similares")
def get_estabelecimentos_similares(
    estabelecimento_id: int,
    top_n: int = Query(10, description="Número de estabelecimentos similares"),
    db: Session = Depends(get_db)
):
    """
    Obter estabelecimentos similares (item-item similarity)
    
    Útil para "Pessoas que visitaram X também visitaram Y"
    """
    # TODO: Implementar lógica de similaridade item-item
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/interacao")
def registrar_interacao(
    usuario_id: int,
    estabelecimento_id: int,
    tipo_interacao: str = Query(..., description="Tipo: 'visita', 'clique', 'favorito'"),
    peso: float = Query(1.0, description="Peso da interação (0-1)"),
    db: Session = Depends(get_db)
):
    """
    Registrar interação implícita do usuário com estabelecimento
    
    Essencial para treinar o modelo LightFM com feedback implícito
    """
    # TODO: Implementar registro de interação
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/treinar")
def treinar_modelo(
    usar_features: bool = Query(True, description="Usar features para CBF"),
    loss: str = Query("warp", description="Função de perda: 'warp', 'bpr', 'logistic'"),
    db: Session = Depends(get_db)
):
    """
    Retreinar o modelo LightFM com dados atualizados
    
    - **usar_features**: Se True, usa metadados para CBF
    - **loss**: Função de perda
        - 'warp': WARP (recomendado para ranking)
        - 'bpr': Bayesian Personalized Ranking
        - 'logistic': Regressão logística
    """
    # TODO: Implementar treinamento do modelo
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/cold-start/usuario/{usuario_id}")
def cold_start_usuario(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    db: Session = Depends(get_db)
):
    """
    Recomendações para usuário novo (cold start)
    
    Usa apenas CBF baseado nas preferências declaradas inicialmente
    """
    # TODO: Implementar estratégia de cold start para usuários
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/cold-start/estabelecimento/{estabelecimento_id}")
def cold_start_estabelecimento(
    estabelecimento_id: int,
    db: Session = Depends(get_db)
):
    """
    Verificar se estabelecimento novo está pronto para ser recomendado
    
    Retorna quais metadados estão faltando para melhor performance
    """
    # TODO: Implementar validação de metadados
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/diversidade/usuario/{usuario_id}")
def get_recomendacoes_diversas(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    explorar: float = Query(0.1, description="Taxa de exploração (epsilon-greedy)"),
    db: Session = Depends(get_db)
):
    """
    Recomendações com diversidade (evita bolha de filtro)
    
    Usa MMR (Maximal Marginal Relevance) para balancear relevância e diversidade
    """
    # TODO: Implementar estratégia de diversidade
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/contexto/usuario/{usuario_id}")
def get_recomendacoes_contextuais(
    usuario_id: int,
    hora_atual: Optional[int] = Query(None, description="Hora do dia (0-23)"),
    dia_semana: Optional[int] = Query(None, description="Dia da semana (0-6)"),
    latitude: Optional[float] = Query(None, description="Latitude do usuário"),
    longitude: Optional[float] = Query(None, description="Longitude do usuário"),
    top_n: int = Query(10, description="Número de recomendações"),
    db: Session = Depends(get_db)
):
    """
    Recomendações contextuais baseadas em localização e tempo
    
    Considera:
    - Horário de funcionamento
    - Distância do usuário
    - Horários de pico
    - Padrões por dia da semana
    """
    # TODO: Implementar recomendações contextuais
    raise HTTPException(status_code=501, detail="Not implemented")
