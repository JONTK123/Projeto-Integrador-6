from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class CategoriasEstabelecimentos(Base):
    """
    Modelo ORM para Categorias de Estabelecimentos
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    __tablename__ = "categorias_estabelecimentos"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Adicionar campos específicos aqui conforme necessário para o modelo
