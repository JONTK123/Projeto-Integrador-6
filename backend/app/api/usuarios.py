from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.usuarios import UsuariosCreate, UsuariosUpdate, UsuariosResponse
from app.models.usuarios import Usuarios
from app.models.universidades import Universidades

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuariosResponse, status_code=201)
def create_usuario(usuario: UsuariosCreate, db: Session = Depends(get_db)):
    """
    Criar novo usuário
    
    Validações:
    - Email deve ser único
    - Se id_universidade fornecido, deve existir
    """
    # Verificar se email já existe
    existing = db.query(Usuarios).filter(Usuarios.email == usuario.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Email {usuario.email} já está em uso"
        )
    
    # Validar universidade se fornecida
    if usuario.id_universidade:
        universidade = db.query(Universidades).filter(
            Universidades.id == usuario.id_universidade
        ).first()
        if not universidade:
            raise HTTPException(
                status_code=404,
                detail=f"Universidade {usuario.id_universidade} não encontrada"
            )
    
    # Criar novo usuário
    novo_usuario = Usuarios(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=usuario.senha_hash,
        curso=usuario.curso,
        idade=usuario.idade,
        descricao=usuario.descricao,
        id_universidade=usuario.id_universidade,
        data_cadastro=datetime.utcnow().date()
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario


@router.get("/", response_model=List[UsuariosResponse])
def list_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar todos os usuários com paginação
    """
    try:
        usuarios = db.query(Usuarios).offset(skip).limit(limit).all()
        return usuarios
    except Exception as e:
        import traceback
        print(f"Erro ao listar usuários: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@router.get("/{usuario_id}", response_model=UsuariosResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obter usuário por ID
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {usuario_id} não encontrado"
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuariosResponse)
def update_usuario(
    usuario_id: int,
    usuario: UsuariosUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar usuário
    
    Validações:
    - Email deve ser único (se fornecido)
    - Se id_universidade fornecido, deve existir
    """
    db_usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {usuario_id} não encontrado"
        )
    
    # Verificar se email já existe (se estiver sendo alterado)
    if usuario.email and usuario.email != db_usuario.email:
        existing = db.query(Usuarios).filter(Usuarios.email == usuario.email).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Email {usuario.email} já está em uso"
            )
    
    # Validar universidade se fornecida
    if usuario.id_universidade is not None:
        if usuario.id_universidade != db_usuario.id_universidade:
            universidade = db.query(Universidades).filter(
                Universidades.id == usuario.id_universidade
            ).first()
            if not universidade:
                raise HTTPException(
                    status_code=404,
                    detail=f"Universidade {usuario.id_universidade} não encontrada"
                )
    
    # Atualizar campos fornecidos
    update_data = usuario.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    # updated_at não existe na tabela do banco
    # db_usuario.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


@router.delete("/{usuario_id}", status_code=204)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Deletar usuário
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {usuario_id} não encontrado"
        )
    
    db.delete(usuario)
    db.commit()
    return None
