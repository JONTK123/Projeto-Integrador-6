from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class EstabelecimentoPreferencia(Base):
    """
    Modelo ORM para relacionamento Estabelecimento-Preferencia
    Usado para Content-Based Filtering - características dos estabelecimentos
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    __tablename__ = "estabelecimento_preferencia"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Adicionar campos específicos aqui conforme necessário para o modelo
    # Ex: estabelecimento_id = Column(Integer, ForeignKey("estabelecimentos.id"))
    # Ex: preferencia_id = Column(Integer, ForeignKey("preferencias.id"))
