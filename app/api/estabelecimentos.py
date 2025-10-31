from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.estabelecimentos import EstabelecimentosCreate, EstabelecimentosUpdate, EstabelecimentosResponse

router = APIRouter(prefix="/estabelecimentos", tags=["Estabelecimentos"])


@router.post("/", response_model=EstabelecimentosResponse, status_code=201)
def create_estabelecimento(estabelecimento: EstabelecimentosCreate, db: Session = Depends(get_db)):
    """
    Criar novo estabelecimento
    """
    # TODO: Implementar lógica de criação
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=List[EstabelecimentosResponse])
def list_estabelecimentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todos os estabelecimentos
    """
    # TODO: Implementar lógica de listagem
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def get_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Obter estabelecimento por ID
    """
    # TODO: Implementar lógica de busca
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def update_estabelecimento(estabelecimento_id: int, estabelecimento: EstabelecimentosUpdate, db: Session = Depends(get_db)):
    """
    Atualizar estabelecimento
    """
    # TODO: Implementar lógica de atualização
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{estabelecimento_id}", status_code=204)
def delete_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Deletar estabelecimento
    """
    # TODO: Implementar lógica de deleção
    raise HTTPException(status_code=501, detail="Not implemented")
