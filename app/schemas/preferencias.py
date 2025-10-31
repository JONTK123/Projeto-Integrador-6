from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PreferenciasBase(BaseModel):
    """
    Schema base para Preferências
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class PreferenciasCreate(PreferenciasBase):
    """
    Schema para criação de Preferência
    """
    pass


class PreferenciasUpdate(PreferenciasBase):
    """
    Schema para atualização de Preferência
    """
    pass


class PreferenciasResponse(PreferenciasBase):
    """
    Schema de resposta para Preferência
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
