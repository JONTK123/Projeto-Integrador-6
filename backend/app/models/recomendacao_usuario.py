from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class RecomendacaoUsuario(Base):
    """
    Modelo ORM para Recomendações entre Usuários (user-user similarity)
    Identifica usuários similares para Collaborative Filtering
    "Pessoas como você também gostaram de..."
    """
    __tablename__ = "recomendacao_usuario"

    id = Column(Integer, primary_key=True, index=True, name="id_recomendacao")
    id_usuario1 = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_usuario2 = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    score = Column(Float, nullable=False)  # Similaridade entre usuários (0-1)
    data_recomendacao = Column(Date, default=datetime.utcnow)
    # created_at e updated_at não existem na tabela do banco
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
