from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional


class RecomendacaoEstabelecimentoBase(BaseModel):
    """
    Schema base para Interações de Usuário com Estabelecimento
    Feedback implícito para treinar o LightFM
    """
    id_usuario: int
    id_lugar: int  # id_estabelecimento
    score: int = Field(ge=1, le=5)  # Avaliação/peso da interação (1-5)
    data_recomendacao: Optional[date] = None


class RecomendacaoEstabelecimentoCreate(RecomendacaoEstabelecimentoBase):
    """
    Schema para criação de Interação/Avaliação
    """
    pass


class RecomendacaoEstabelecimentoUpdate(BaseModel):
    """
    Schema para atualização de Interação/Avaliação
    """
    score: Optional[int] = Field(default=None, ge=1, le=5)


class RecomendacaoEstabelecimentoResponse(RecomendacaoEstabelecimentoBase):
    """
    Schema de resposta para Interação/Avaliação
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
