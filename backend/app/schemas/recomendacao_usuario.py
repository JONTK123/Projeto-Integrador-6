from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional


class RecomendacaoUsuarioBase(BaseModel):
    """
    Schema base para Recomendações entre Usuários (user-user similarity)
    """
    id_usuario1: int
    id_usuario2: int
    score: float = Field(ge=0.0, le=1.0)  # Similaridade entre 0 e 1
    data_recomendacao: Optional[date] = None


class RecomendacaoUsuarioCreate(RecomendacaoUsuarioBase):
    """
    Schema para criação de Recomendação entre Usuários
    """
    pass


class RecomendacaoUsuarioUpdate(BaseModel):
    """
    Schema para atualização de Recomendação entre Usuários
    """
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class RecomendacaoUsuarioResponse(RecomendacaoUsuarioBase):
    """
    Schema de resposta para Recomendação entre Usuários
    """
    id: int
    # created_at e updated_at não existem na tabela do banco
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
