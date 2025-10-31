from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoriasEstabelecimentosBase(BaseModel):
    """
    Schema base para Categorias de Estabelecimentos
    Esqueleto - campos serão definidos conforme necessidades do modelo LightFM
    """
    pass


class CategoriasEstabelecimentosCreate(CategoriasEstabelecimentosBase):
    """
    Schema para criação de Categoria de Estabelecimento
    """
    pass


class CategoriasEstabelecimentosUpdate(CategoriasEstabelecimentosBase):
    """
    Schema para atualização de Categoria de Estabelecimento
    """
    pass


class CategoriasEstabelecimentosResponse(CategoriasEstabelecimentosBase):
    """
    Schema de resposta para Categoria de Estabelecimento
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
