from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class CategoriasEstabelecimentos(Base):
    """
    Modelo ORM para Categorias de Estabelecimentos
    """
    __tablename__ = "categorias_estabelecimentos"

    id = Column(Integer, primary_key=True, index=True, name="id_categoria")
    nome_categoria = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
