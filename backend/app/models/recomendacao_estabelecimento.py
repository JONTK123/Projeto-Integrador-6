from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class RecomendacaoEstabelecimento(Base):
    """
    Modelo ORM para Avaliações/Interações de Usuários com Estabelecimentos
    Matriz de interações implícitas para treinar o LightFM
    Feedback implícito: visitas, cliques, favoritos, avaliações
    """
    __tablename__ = "recomendacao_estabelecimento"

    id = Column(Integer, primary_key=True, index=True, name="id_recomendacao")
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_lugar = Column(Integer, ForeignKey("estabelecimentos.id_estabelecimento"), nullable=False)
    score = Column(Integer, nullable=False)  # Avaliação/Peso da interação (1-5)
    data_recomendacao = Column(Date, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
