from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RecomendacaoEstabelecimentoBase(BaseModel):
    """
    Schema base para Recomendações de Estabelecimento (item-item)
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class RecomendacaoEstabelecimentoCreate(RecomendacaoEstabelecimentoBase):
    """
    Schema para criação de Recomendação de Estabelecimento
    """
    pass


class RecomendacaoEstabelecimentoUpdate(RecomendacaoEstabelecimentoBase):
    """
    Schema para atualização de Recomendação de Estabelecimento
    """
    pass


class RecomendacaoEstabelecimentoResponse(RecomendacaoEstabelecimentoBase):
    """
    Schema de resposta para Recomendação de Estabelecimento
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
