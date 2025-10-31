from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class EstabelecimentoPreferencia(Base):
    """
    Modelo ORM para relacionamento Estabelecimento-Preferencia
    Item features para o LightFM (características dos estabelecimentos)
    Usado para CBF - metadados essenciais
    """
    __tablename__ = "estabelecimento_preferencia"

    id = Column(Integer, primary_key=True, index=True)
    id_estabelecimento = Column(Integer, ForeignKey("estabelecimentos.id_estabelecimento"), nullable=False)
    id_preferencia = Column(Integer, ForeignKey("preferencias.id_preferencia"), nullable=False)
    peso = Column(Float, default=1.0)  # Intensidade da característica (1-5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
