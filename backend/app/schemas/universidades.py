from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UniversidadesBase(BaseModel):
    """
    Schema base para Universidades
    """
    nome: str
    cidade: str
    estado: str


class UniversidadesCreate(UniversidadesBase):
    """
    Schema para criação de Universidade
    """
    pass


class UniversidadesUpdate(BaseModel):
    """
    Schema para atualização de Universidade
    """
    nome: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None


class UniversidadesResponse(UniversidadesBase):
    """
    Schema de resposta para Universidade
    """
    id: int
    # created_at e updated_at não existem na tabela do banco
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
