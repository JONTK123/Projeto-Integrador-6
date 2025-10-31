from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RecomendacaoUsuarioBase(BaseModel):
    """
    Schema base para Recomendações de Usuário
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class RecomendacaoUsuarioCreate(RecomendacaoUsuarioBase):
    """
    Schema para criação de Recomendação para Usuário
    """
    pass


class RecomendacaoUsuarioUpdate(RecomendacaoUsuarioBase):
    """
    Schema para atualização de Recomendação para Usuário
    """
    pass


class RecomendacaoUsuarioResponse(RecomendacaoUsuarioBase):
    """
    Schema de resposta para Recomendação de Usuário
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
