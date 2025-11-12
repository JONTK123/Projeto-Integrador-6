from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class EstabelecimentoPreferenciaBase(BaseModel):
    """
    Schema base para Estabelecimento-Preferencia
    """
    id_estabelecimento: int
    id_preferencia: int
    peso: float = Field(default=1.0, ge=1.0, le=5.0)  # Intensidade entre 1 e 5


class EstabelecimentoPreferenciaCreate(EstabelecimentoPreferenciaBase):
    """
    Schema para criação de associação Estabelecimento-Preferencia
    """
    pass


class EstabelecimentoPreferenciaUpdate(BaseModel):
    """
    Schema para atualização de associação Estabelecimento-Preferencia
    """
    peso: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class EstabelecimentoPreferenciaResponse(EstabelecimentoPreferenciaBase):
    """
    Schema de resposta para associação Estabelecimento-Preferencia
    """
    id: int
    # created_at e updated_at não existem na tabela do banco
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
