from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.usuario_preferencia import (
    UsuarioPreferenciaCreate,
    UsuarioPreferenciaUpdate,
    UsuarioPreferenciaResponse
)
from app.models.usuario_preferencia import UsuarioPreferencia
from app.models.usuarios import Usuarios
from app.models.preferencias import Preferencias

router = APIRouter(prefix="/usuario-preferencias", tags=["Usuário-Preferências"])


@router.post("/", response_model=UsuarioPreferenciaResponse, status_code=201)
def create_usuario_preferencia(
    usuario_preferencia: UsuarioPreferenciaCreate,
    db: Session = Depends(get_db)
):
    """
    Criar associação entre usuário e preferência
    
    Validações:
    - Usuário deve existir
    - Preferência deve existir
    - Não pode haver duplicatas (mesmo usuário + mesma preferência)
    """
    # Validar usuário
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_preferencia.id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {usuario_preferencia.id_usuario} não encontrado"
        )
    
    # Validar preferência
    preferencia = db.query(Preferencias).filter(
        Preferencias.id == usuario_preferencia.id_preferencia
    ).first()
    if not preferencia:
        raise HTTPException(
            status_code=404,
            detail=f"Preferência {usuario_preferencia.id_preferencia} não encontrada"
        )
    
    # Verificar se já existe associação
    existing = db.query(UsuarioPreferencia).filter(
        UsuarioPreferencia.id_usuario == usuario_preferencia.id_usuario,
        UsuarioPreferencia.id_preferencia == usuario_preferencia.id_preferencia
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Associação entre usuário {usuario_preferencia.id_usuario} e preferência {usuario_preferencia.id_preferencia} já existe"
        )
    
    # Criar nova associação
    nova_associacao = UsuarioPreferencia(
        id_usuario=usuario_preferencia.id_usuario,
        id_preferencia=usuario_preferencia.id_preferencia,
        peso=usuario_preferencia.peso
    )
    
    db.add(nova_associacao)
    db.commit()
    db.refresh(nova_associacao)
    
    return nova_associacao


@router.get("/", response_model=List[UsuarioPreferenciaResponse])
def list_usuario_preferencias(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    usuario_id: int = Query(None, description="Filtrar por ID do usuário"),
    preferencia_id: int = Query(None, description="Filtrar por ID da preferência"),
    db: Session = Depends(get_db)
):
    """
    Listar associações usuário-preferência com paginação e filtros opcionais
    """
    query = db.query(UsuarioPreferencia)
    
    if usuario_id:
        query = query.filter(UsuarioPreferencia.id_usuario == usuario_id)
    if preferencia_id:
        query = query.filter(UsuarioPreferencia.id_preferencia == preferencia_id)
    
    associacoes = query.offset(skip).limit(limit).all()
    return associacoes


@router.get("/{associacao_id}", response_model=UsuarioPreferenciaResponse)
def get_usuario_preferencia(associacao_id: int, db: Session = Depends(get_db)):
    """
    Obter associação usuário-preferência por ID
    """
    associacao = db.query(UsuarioPreferencia).filter(
        UsuarioPreferencia.id == associacao_id
    ).first()
    if not associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    return associacao


@router.put("/{associacao_id}", response_model=UsuarioPreferenciaResponse)
def update_usuario_preferencia(
    associacao_id: int,
    usuario_preferencia: UsuarioPreferenciaUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar associação usuário-preferência (apenas peso)
    """
    db_associacao = db.query(UsuarioPreferencia).filter(
        UsuarioPreferencia.id == associacao_id
    ).first()
    if not db_associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    
    # Atualizar apenas peso
    if usuario_preferencia.peso is not None:
        db_associacao.peso = usuario_preferencia.peso
    
    db_associacao.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_associacao)
    
    return db_associacao


@router.delete("/{associacao_id}", status_code=204)
def delete_usuario_preferencia(associacao_id: int, db: Session = Depends(get_db)):
    """
    Deletar associação usuário-preferência
    """
    associacao = db.query(UsuarioPreferencia).filter(
        UsuarioPreferencia.id == associacao_id
    ).first()
    if not associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    
    db.delete(associacao)
    db.commit()
    return None

