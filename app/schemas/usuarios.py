from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UsuariosBase(BaseModel):
    """
    Schema base para Usuários
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class UsuariosCreate(UsuariosBase):
    """
    Schema para criação de Usuário
    """
    pass


class UsuariosUpdate(UsuariosBase):
    """
    Schema para atualização de Usuário
    """
    pass


class UsuariosResponse(UsuariosBase):
    """
    Schema de resposta para Usuário
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
