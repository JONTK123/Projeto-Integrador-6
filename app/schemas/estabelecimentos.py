from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class EstabelecimentosBase(BaseModel):
    """
    Schema base para Estabelecimentos
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class EstabelecimentosCreate(EstabelecimentosBase):
    """
    Schema para criação de Estabelecimento
    """
    pass


class EstabelecimentosUpdate(EstabelecimentosBase):
    """
    Schema para atualização de Estabelecimento
    """
    pass


class EstabelecimentosResponse(EstabelecimentosBase):
    """
    Schema de resposta para Estabelecimento
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
