from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PreferenciasBase(BaseModel):
    """
    Schema base para Preferências
    """
    nome_preferencia: str
    tipo_preferencia: str  # 'Alimentação', 'Ambiente', 'Lazer', 'Material', etc.


class PreferenciasCreate(PreferenciasBase):
    """
    Schema para criação de Preferência
    """
    pass


class PreferenciasUpdate(BaseModel):
    """
    Schema para atualização de Preferência
    """
    nome_preferencia: Optional[str] = None
    tipo_preferencia: Optional[str] = None


class PreferenciasResponse(PreferenciasBase):
    """
    Schema de resposta para Preferência
    """
    id: int
    # created_at e updated_at não existem na tabela do banco
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
