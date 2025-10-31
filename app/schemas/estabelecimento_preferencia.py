from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class EstabelecimentoPreferenciaBase(BaseModel):
    """
    Schema base para Estabelecimento-Preferencia
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class EstabelecimentoPreferenciaCreate(EstabelecimentoPreferenciaBase):
    """
    Schema para criação de associação Estabelecimento-Preferencia
    """
    pass


class EstabelecimentoPreferenciaUpdate(EstabelecimentoPreferenciaBase):
    """
    Schema para atualização de associação Estabelecimento-Preferencia
    """
    pass


class EstabelecimentoPreferenciaResponse(EstabelecimentoPreferenciaBase):
    """
    Schema de resposta para associação Estabelecimento-Preferencia
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
