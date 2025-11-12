from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime, date
from typing import Optional


class UsuariosBase(BaseModel):
    """
    Schema base para Usuários
    """
    nome: str
    email: EmailStr
    curso: Optional[str] = None
    idade: Optional[int] = None
    descricao: Optional[str] = None
    id_universidade: Optional[int] = None


class UsuariosCreate(UsuariosBase):
    """
    Schema para criação de Usuário
    """
    senha_hash: str  # Em produção, hash a senha antes de armazenar


class UsuariosUpdate(BaseModel):
    """
    Schema para atualização de Usuário
    """
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    curso: Optional[str] = None
    idade: Optional[int] = None
    descricao: Optional[str] = None
    id_universidade: Optional[int] = None
    senha_hash: Optional[str] = None


class UsuariosResponse(UsuariosBase):
    """
    Schema de resposta para Usuário
    """
    id: int
    data_cadastro: Optional[date] = None
    # created_at e updated_at não existem na tabela do banco
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
