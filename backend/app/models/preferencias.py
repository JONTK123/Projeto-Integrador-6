from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Preferencias(Base):
    """
    Modelo ORM para Preferências
    Features para Content-Based Filtering no LightFM
    """
    __tablename__ = "preferencias"

    id = Column(Integer, primary_key=True, index=True, name="id_preferencia")
    nome_preferencia = Column(String(100), nullable=False)
    tipo_preferencia = Column(String(50), nullable=False)  # Ex: 'Alimentação', 'Ambiente', 'Lazer', etc.
    # created_at e updated_at não existem na tabela do banco
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
