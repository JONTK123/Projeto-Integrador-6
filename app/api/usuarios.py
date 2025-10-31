from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.usuarios import UsuariosCreate, UsuariosUpdate, UsuariosResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuariosResponse, status_code=201)
def create_usuario(usuario: UsuariosCreate, db: Session = Depends(get_db)):
    """
    Criar novo usuário
    """
    # TODO: Implementar lógica de criação
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=List[UsuariosResponse])
def list_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todos os usuários
    """
    # TODO: Implementar lógica de listagem
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{usuario_id}", response_model=UsuariosResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obter usuário por ID
    """
    # TODO: Implementar lógica de busca
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{usuario_id}", response_model=UsuariosResponse)
def update_usuario(usuario_id: int, usuario: UsuariosUpdate, db: Session = Depends(get_db)):
    """
    Atualizar usuário
    """
    # TODO: Implementar lógica de atualização
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{usuario_id}", status_code=204)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Deletar usuário
    """
    # TODO: Implementar lógica de deleção
    raise HTTPException(status_code=501, detail="Not implemented")
