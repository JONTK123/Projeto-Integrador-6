from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.estabelecimento_preferencia import (
    EstabelecimentoPreferenciaCreate,
    EstabelecimentoPreferenciaUpdate,
    EstabelecimentoPreferenciaResponse
)
from app.models.estabelecimento_preferencia import EstabelecimentoPreferencia
from app.models.estabelecimentos import Estabelecimentos
from app.models.preferencias import Preferencias

router = APIRouter(prefix="/estabelecimento-preferencias", tags=["Estabelecimento-Preferências"])


@router.post("/", response_model=EstabelecimentoPreferenciaResponse, status_code=201)
def create_estabelecimento_preferencia(
    estabelecimento_preferencia: EstabelecimentoPreferenciaCreate,
    db: Session = Depends(get_db)
):
    """
    Criar associação entre estabelecimento e preferência
    
    Validações:
    - Estabelecimento deve existir
    - Preferência deve existir
    - Não pode haver duplicatas (mesmo estabelecimento + mesma preferência)
    """
    # Validar estabelecimento
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_preferencia.id_estabelecimento
    ).first()
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_preferencia.id_estabelecimento} não encontrado"
        )
    
    # Validar preferência
    preferencia = db.query(Preferencias).filter(
        Preferencias.id == estabelecimento_preferencia.id_preferencia
    ).first()
    if not preferencia:
        raise HTTPException(
            status_code=404,
            detail=f"Preferência {estabelecimento_preferencia.id_preferencia} não encontrada"
        )
    
    # Verificar se já existe associação
    existing = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id_estabelecimento == estabelecimento_preferencia.id_estabelecimento,
        EstabelecimentoPreferencia.id_preferencia == estabelecimento_preferencia.id_preferencia
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Associação entre estabelecimento {estabelecimento_preferencia.id_estabelecimento} e preferência {estabelecimento_preferencia.id_preferencia} já existe"
        )
    
    # Criar nova associação
    nova_associacao = EstabelecimentoPreferencia(
        id_estabelecimento=estabelecimento_preferencia.id_estabelecimento,
        id_preferencia=estabelecimento_preferencia.id_preferencia,
        peso=estabelecimento_preferencia.peso
    )
    
    db.add(nova_associacao)
    db.commit()
    db.refresh(nova_associacao)
    
    return nova_associacao


@router.get("/", response_model=List[EstabelecimentoPreferenciaResponse])
def list_estabelecimento_preferencias(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    estabelecimento_id: int = Query(None, description="Filtrar por ID do estabelecimento"),
    preferencia_id: int = Query(None, description="Filtrar por ID da preferência"),
    db: Session = Depends(get_db)
):
    """
    Listar associações estabelecimento-preferência com paginação e filtros opcionais
    """
    query = db.query(EstabelecimentoPreferencia)
    
    if estabelecimento_id:
        query = query.filter(EstabelecimentoPreferencia.id_estabelecimento == estabelecimento_id)
    if preferencia_id:
        query = query.filter(EstabelecimentoPreferencia.id_preferencia == preferencia_id)
    
    associacoes = query.offset(skip).limit(limit).all()
    return associacoes


@router.get("/{associacao_id}", response_model=EstabelecimentoPreferenciaResponse)
def get_estabelecimento_preferencia(associacao_id: int, db: Session = Depends(get_db)):
    """
    Obter associação estabelecimento-preferência por ID
    """
    associacao = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id == associacao_id
    ).first()
    if not associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    return associacao


@router.put("/{associacao_id}", response_model=EstabelecimentoPreferenciaResponse)
def update_estabelecimento_preferencia(
    associacao_id: int,
    estabelecimento_preferencia: EstabelecimentoPreferenciaUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar associação estabelecimento-preferência (apenas peso)
    """
    db_associacao = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id == associacao_id
    ).first()
    if not db_associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    
    # Atualizar apenas peso
    if estabelecimento_preferencia.peso is not None:
        db_associacao.peso = estabelecimento_preferencia.peso
    
    # updated_at não existe na tabela do banco
    # db_associacao.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_associacao)
    
    return db_associacao


@router.delete("/{associacao_id}", status_code=204)
def delete_estabelecimento_preferencia(associacao_id: int, db: Session = Depends(get_db)):
    """
    Deletar associação estabelecimento-preferência
    """
    associacao = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id == associacao_id
    ).first()
    if not associacao:
        raise HTTPException(
            status_code=404,
            detail=f"Associação {associacao_id} não encontrada"
        )
    
    db.delete(associacao)
    db.commit()
    return None

