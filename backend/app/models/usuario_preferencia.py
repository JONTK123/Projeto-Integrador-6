from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class UsuarioPreferencia(Base):
    """
    Modelo ORM para relacionamento Usuario-Preferencia
    User features para o LightFM (preferências declaradas pelo usuário)
    Usado para CBF e cold start
    """
    __tablename__ = "usuario_preferencia"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_preferencia = Column(Integer, ForeignKey("preferencias.id_preferencia"), nullable=False)
    peso = Column(Float, default=1.0)  # Importância da preferência para o usuário (1-5)
    # created_at e updated_at não existem na tabela do banco
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
