from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoriasEstabelecimentosBase(BaseModel):
    """
    Schema base para Categorias de Estabelecimentos
    """
    nome_categoria: str


class CategoriasEstabelecimentosCreate(CategoriasEstabelecimentosBase):
    """
    Schema para criação de Categoria de Estabelecimento
    """
    pass


class CategoriasEstabelecimentosUpdate(BaseModel):
    """
    Schema para atualização de Categoria de Estabelecimento
    """
    nome_categoria: Optional[str] = None


class CategoriasEstabelecimentosResponse(CategoriasEstabelecimentosBase):
    """
    Schema de resposta para Categoria de Estabelecimento
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
