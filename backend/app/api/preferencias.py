from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.preferencias import PreferenciasCreate, PreferenciasUpdate, PreferenciasResponse
from app.models.preferencias import Preferencias

router = APIRouter(prefix="/preferencias", tags=["Preferências"])


@router.post("/", response_model=PreferenciasResponse, status_code=201)
def create_preferencia(preferencia: PreferenciasCreate, db: Session = Depends(get_db)):
    """
    Criar nova preferência
    """
    nova_preferencia = Preferencias(
        nome_preferencia=preferencia.nome_preferencia,
        tipo_preferencia=preferencia.tipo_preferencia
    )
    
    db.add(nova_preferencia)
    db.commit()
    db.refresh(nova_preferencia)
    
    return nova_preferencia


@router.get("/", response_model=List[PreferenciasResponse])
def list_preferencias(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    tipo: str = Query(None, description="Filtrar por tipo de preferência"),
    db: Session = Depends(get_db)
):
    """
    Listar todas as preferências com paginação e filtro opcional por tipo
    """
    query = db.query(Preferencias)
    
    if tipo:
        query = query.filter(Preferencias.tipo_preferencia == tipo)
    
    preferencias = query.offset(skip).limit(limit).all()
    return preferencias


@router.get("/{preferencia_id}", response_model=PreferenciasResponse)
def get_preferencia(preferencia_id: int, db: Session = Depends(get_db)):
    """
    Obter preferência por ID
    """
    preferencia = db.query(Preferencias).filter(Preferencias.id == preferencia_id).first()
    if not preferencia:
        raise HTTPException(
            status_code=404,
            detail=f"Preferência {preferencia_id} não encontrada"
        )
    return preferencia


@router.put("/{preferencia_id}", response_model=PreferenciasResponse)
def update_preferencia(
    preferencia_id: int,
    preferencia: PreferenciasUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar preferência
    """
    db_preferencia = db.query(Preferencias).filter(Preferencias.id == preferencia_id).first()
    if not db_preferencia:
        raise HTTPException(
            status_code=404,
            detail=f"Preferência {preferencia_id} não encontrada"
        )
    
    # Atualizar campos fornecidos
    update_data = preferencia.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_preferencia, field, value)
    
    # updated_at não existe na tabela do banco
    # db_preferencia.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_preferencia)
    
    return db_preferencia


@router.delete("/{preferencia_id}", status_code=204)
def delete_preferencia(preferencia_id: int, db: Session = Depends(get_db)):
    """
    Deletar preferência
    """
    preferencia = db.query(Preferencias).filter(Preferencias.id == preferencia_id).first()
    if not preferencia:
        raise HTTPException(
            status_code=404,
            detail=f"Preferência {preferencia_id} não encontrada"
        )
    
    db.delete(preferencia)
    db.commit()
    return None
