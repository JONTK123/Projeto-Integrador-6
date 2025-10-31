from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Estabelecimentos(Base):
    """
    Modelo ORM para Estabelecimentos
    Item features para Content-Based Filtering no LightFM
    """
    __tablename__ = "estabelecimentos"

    id = Column(Integer, primary_key=True, index=True, name="id_estabelecimento")
    descricao = Column(Text, nullable=False)
    endereco = Column(String(255), nullable=False)
    cidade = Column(String(100), nullable=False)
    horario_funcionamento = Column(String(100))
    dono_nome = Column(String(255))
    dono_email = Column(String(255))
    id_categoria = Column(Integer, ForeignKey("categorias_estabelecimentos.id_categoria"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
