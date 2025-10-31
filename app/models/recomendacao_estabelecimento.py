from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class RecomendacaoEstabelecimento(Base):
    """
    Modelo ORM para Recomendações de Estabelecimentos similares
    Usado para "estabelecimentos parecidos" (item-item similarity)
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    __tablename__ = "recomendacao_estabelecimento"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Adicionar campos específicos aqui conforme necessário para o modelo
    # Ex: estabelecimento_origem_id = Column(Integer, ForeignKey("estabelecimentos.id"))
    # Ex: estabelecimento_recomendado_id = Column(Integer, ForeignKey("estabelecimentos.id"))
    # Ex: similarity_score = Column(Float)  # Score de similaridade
