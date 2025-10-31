from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class UsuarioPreferenciaBase(BaseModel):
    """
    Schema base para Usuario-Preferencia
    """
    id_usuario: int
    id_preferencia: int
    peso: float = Field(default=1.0, ge=1.0, le=5.0)  # Peso entre 1 e 5


class UsuarioPreferenciaCreate(UsuarioPreferenciaBase):
    """
    Schema para criação de associação Usuario-Preferencia
    """
    pass


class UsuarioPreferenciaUpdate(BaseModel):
    """
    Schema para atualização de associação Usuario-Preferencia
    """
    peso: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class UsuarioPreferenciaResponse(UsuarioPreferenciaBase):
    """
    Schema de resposta para associação Usuario-Preferencia
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
