from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class RecomendacaoUsuario(Base):
    """
    Modelo ORM para Recomendações geradas para Usuários
    Armazena as recomendações geradas pelo modelo LightFM
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    __tablename__ = "recomendacao_usuario"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Adicionar campos específicos aqui conforme necessário para o modelo
    # Ex: usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # Ex: estabelecimento_id = Column(Integer, ForeignKey("estabelecimentos.id"))
    # Ex: score = Column(Float)  # Score de recomendação do LightFM
