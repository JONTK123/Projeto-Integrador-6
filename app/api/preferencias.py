from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.preferencias import PreferenciasCreate, PreferenciasUpdate, PreferenciasResponse

router = APIRouter(prefix="/preferencias", tags=["Preferências"])


@router.post("/", response_model=PreferenciasResponse, status_code=201)
def create_preferencia(preferencia: PreferenciasCreate, db: Session = Depends(get_db)):
    """
    Criar nova preferência
    """
    # TODO: Implementar lógica de criação
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=List[PreferenciasResponse])
def list_preferencias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todas as preferências
    """
    # TODO: Implementar lógica de listagem
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{preferencia_id}", response_model=PreferenciasResponse)
def get_preferencia(preferencia_id: int, db: Session = Depends(get_db)):
    """
    Obter preferência por ID
    """
    # TODO: Implementar lógica de busca
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{preferencia_id}", response_model=PreferenciasResponse)
def update_preferencia(preferencia_id: int, preferencia: PreferenciasUpdate, db: Session = Depends(get_db)):
    """
    Atualizar preferência
    """
    # TODO: Implementar lógica de atualização
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{preferencia_id}", status_code=204)
def delete_preferencia(preferencia_id: int, db: Session = Depends(get_db)):
    """
    Deletar preferência
    """
    # TODO: Implementar lógica de deleção
    raise HTTPException(status_code=501, detail="Not implemented")
