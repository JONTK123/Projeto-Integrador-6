from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UsuarioPreferenciaBase(BaseModel):
    """
    Schema base para Usuario-Preferencia
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class UsuarioPreferenciaCreate(UsuarioPreferenciaBase):
    """
    Schema para criação de associação Usuario-Preferencia
    """
    pass


class UsuarioPreferenciaUpdate(UsuarioPreferenciaBase):
    """
    Schema para atualização de associação Usuario-Preferencia
    """
    pass


class UsuarioPreferenciaResponse(UsuarioPreferenciaBase):
    """
    Schema de resposta para associação Usuario-Preferencia
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
