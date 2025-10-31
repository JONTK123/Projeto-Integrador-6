from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class UsuarioPreferencia(Base):
    """
    Modelo ORM para relacionamento Usuario-Preferencia
    Tabela de associação para Collaborative Filtering
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    __tablename__ = "usuario_preferencia"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Adicionar campos específicos aqui conforme necessário para o modelo
    # Ex: usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # Ex: preferencia_id = Column(Integer, ForeignKey("preferencias.id"))
