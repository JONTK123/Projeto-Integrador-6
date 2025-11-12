from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.recomendacao_usuario import (
    RecomendacaoUsuarioCreate,
    RecomendacaoUsuarioUpdate,
    RecomendacaoUsuarioResponse
)
from app.models.recomendacao_usuario import RecomendacaoUsuario
from app.models.usuarios import Usuarios

router = APIRouter(prefix="/recomendacoes-usuario", tags=["Recomendações entre Usuários"])


@router.post("/", response_model=RecomendacaoUsuarioResponse, status_code=201)
def create_recomendacao_usuario(
    recomendacao: RecomendacaoUsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Criar recomendação de similaridade entre usuários
    
    Validações:
    - Ambos os usuários devem existir
    - id_usuario1 deve ser diferente de id_usuario2
    - Não pode haver duplicatas (mesmo par de usuários)
    """
    # Validar que são usuários diferentes
    if recomendacao.id_usuario1 == recomendacao.id_usuario2:
        raise HTTPException(
            status_code=400,
            detail="id_usuario1 e id_usuario2 devem ser diferentes"
        )
    
    # Validar usuário 1
    usuario1 = db.query(Usuarios).filter(Usuarios.id == recomendacao.id_usuario1).first()
    if not usuario1:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {recomendacao.id_usuario1} não encontrado"
        )
    
    # Validar usuário 2
    usuario2 = db.query(Usuarios).filter(Usuarios.id == recomendacao.id_usuario2).first()
    if not usuario2:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {recomendacao.id_usuario2} não encontrado"
        )
    
    # Verificar se já existe recomendação (em qualquer ordem)
    existing = db.query(RecomendacaoUsuario).filter(
        (
            (RecomendacaoUsuario.id_usuario1 == recomendacao.id_usuario1) &
            (RecomendacaoUsuario.id_usuario2 == recomendacao.id_usuario2)
        ) | (
            (RecomendacaoUsuario.id_usuario1 == recomendacao.id_usuario2) &
            (RecomendacaoUsuario.id_usuario2 == recomendacao.id_usuario1)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Recomendação entre usuários {recomendacao.id_usuario1} e {recomendacao.id_usuario2} já existe"
        )
    
    # Criar nova recomendação
    nova_recomendacao = RecomendacaoUsuario(
        id_usuario1=recomendacao.id_usuario1,
        id_usuario2=recomendacao.id_usuario2,
        score=recomendacao.score,
        data_recomendacao=recomendacao.data_recomendacao or datetime.utcnow().date()
    )
    
    db.add(nova_recomendacao)
    db.commit()
    db.refresh(nova_recomendacao)
    
    return nova_recomendacao


@router.get("/", response_model=List[RecomendacaoUsuarioResponse])
def list_recomendacoes_usuario(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    usuario_id: int = Query(None, description="Filtrar por ID do usuário (busca em usuario1 ou usuario2)"),
    min_score: float = Query(None, ge=0.0, le=1.0, description="Score mínimo de similaridade"),
    db: Session = Depends(get_db)
):
    """
    Listar recomendações entre usuários com paginação e filtros opcionais
    """
    query = db.query(RecomendacaoUsuario)
    
    if usuario_id:
        query = query.filter(
            (RecomendacaoUsuario.id_usuario1 == usuario_id) |
            (RecomendacaoUsuario.id_usuario2 == usuario_id)
        )
    if min_score is not None:
        query = query.filter(RecomendacaoUsuario.score >= min_score)
    
    # Ordenar por score decrescente
    query = query.order_by(RecomendacaoUsuario.score.desc())
    
    recomendacoes = query.offset(skip).limit(limit).all()
    return recomendacoes


@router.get("/{recomendacao_id}", response_model=RecomendacaoUsuarioResponse)
def get_recomendacao_usuario(recomendacao_id: int, db: Session = Depends(get_db)):
    """
    Obter recomendação entre usuários por ID
    """
    recomendacao = db.query(RecomendacaoUsuario).filter(
        RecomendacaoUsuario.id == recomendacao_id
    ).first()
    if not recomendacao:
        raise HTTPException(
            status_code=404,
            detail=f"Recomendação {recomendacao_id} não encontrada"
        )
    return recomendacao


@router.put("/{recomendacao_id}", response_model=RecomendacaoUsuarioResponse)
def update_recomendacao_usuario(
    recomendacao_id: int,
    recomendacao: RecomendacaoUsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar recomendação entre usuários (apenas score)
    """
    db_recomendacao = db.query(RecomendacaoUsuario).filter(
        RecomendacaoUsuario.id == recomendacao_id
    ).first()
    if not db_recomendacao:
        raise HTTPException(
            status_code=404,
            detail=f"Recomendação {recomendacao_id} não encontrada"
        )
    
    # Atualizar apenas score
    if recomendacao.score is not None:
        db_recomendacao.score = recomendacao.score
    
    # updated_at não existe na tabela do banco
    # db_recomendacao.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_recomendacao)
    
    return db_recomendacao


@router.delete("/{recomendacao_id}", status_code=204)
def delete_recomendacao_usuario(recomendacao_id: int, db: Session = Depends(get_db)):
    """
    Deletar recomendação entre usuários
    """
    recomendacao = db.query(RecomendacaoUsuario).filter(
        RecomendacaoUsuario.id == recomendacao_id
    ).first()
    if not recomendacao:
        raise HTTPException(
            status_code=404,
            detail=f"Recomendação {recomendacao_id} não encontrada"
        )
    
    db.delete(recomendacao)
    db.commit()
    return None

