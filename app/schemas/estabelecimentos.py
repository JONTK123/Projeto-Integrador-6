from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class EstabelecimentosBase(BaseModel):
    """
    Schema base para Estabelecimentos
    """
    descricao: str
    endereco: str
    cidade: str
    horario_funcionamento: Optional[str] = None
    dono_nome: Optional[str] = None
    dono_email: Optional[EmailStr] = None
    id_categoria: Optional[int] = None


class EstabelecimentosCreate(EstabelecimentosBase):
    """
    Schema para criação de Estabelecimento
    """
    pass


class EstabelecimentosUpdate(BaseModel):
    """
    Schema para atualização de Estabelecimento
    """
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    horario_funcionamento: Optional[str] = None
    dono_nome: Optional[str] = None
    dono_email: Optional[EmailStr] = None
    id_categoria: Optional[int] = None


class EstabelecimentosResponse(EstabelecimentosBase):
    """
    Schema de resposta para Estabelecimento
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
