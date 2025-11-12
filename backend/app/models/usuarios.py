from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Usuarios(Base):
    """
    Modelo ORM para Usuários
    User features para Collaborative Filtering no LightFM
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, name="id_usuario")
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    curso = Column(String(100))
    idade = Column(Integer)
    descricao = Column(Text)
    id_universidade = Column(Integer, ForeignKey("universidades.id_universidade"))
    data_cadastro = Column(Date, default=datetime.utcnow)
    # created_at e updated_at não existem na tabela do banco
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
