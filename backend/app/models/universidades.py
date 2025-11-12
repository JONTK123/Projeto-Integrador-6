from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Universidades(Base):
    """
    Modelo ORM para Universidades
    """
    __tablename__ = "universidades"

    id = Column(Integer, primary_key=True, index=True, name="id_universidade")
    nome = Column(String(255), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    # created_at e updated_at não existem na tabela do banco
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
