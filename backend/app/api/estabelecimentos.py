from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.estabelecimentos import EstabelecimentosCreate, EstabelecimentosUpdate, EstabelecimentosResponse
from app.models.estabelecimentos import Estabelecimentos
from app.models.categorias_estabelecimentos import CategoriasEstabelecimentos

router = APIRouter(prefix="/estabelecimentos", tags=["Estabelecimentos"])


@router.post("/", response_model=EstabelecimentosResponse, status_code=201)
def create_estabelecimento(estabelecimento: EstabelecimentosCreate, db: Session = Depends(get_db)):
    """
    Criar novo estabelecimento
    
    Validações:
    - Se id_categoria fornecido, deve existir
    """
    # Validar categoria se fornecida
    if estabelecimento.id_categoria:
        categoria = db.query(CategoriasEstabelecimentos).filter(
            CategoriasEstabelecimentos.id == estabelecimento.id_categoria
        ).first()
        if not categoria:
            raise HTTPException(
                status_code=404,
                detail=f"Categoria {estabelecimento.id_categoria} não encontrada"
            )
    
    # Criar novo estabelecimento
    novo_estabelecimento = Estabelecimentos(
        descricao=estabelecimento.descricao,
        endereco=estabelecimento.endereco,
        cidade=estabelecimento.cidade,
        horario_funcionamento=estabelecimento.horario_funcionamento,
        dono_nome=estabelecimento.dono_nome,
        dono_email=estabelecimento.dono_email,
        id_categoria=estabelecimento.id_categoria
    )
    
    db.add(novo_estabelecimento)
    db.commit()
    db.refresh(novo_estabelecimento)
    
    return novo_estabelecimento


@router.get("/", response_model=List[EstabelecimentosResponse])
def list_estabelecimentos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar todos os estabelecimentos com paginação
    """
    estabelecimentos = db.query(Estabelecimentos).offset(skip).limit(limit).all()
    return estabelecimentos


@router.get("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def get_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Obter estabelecimento por ID
    """
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_id
    ).first()
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    return estabelecimento


@router.put("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def update_estabelecimento(
    estabelecimento_id: int,
    estabelecimento: EstabelecimentosUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar estabelecimento
    
    Validações:
    - Se id_categoria fornecido, deve existir
    """
    db_estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_id
    ).first()
    if not db_estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    # Validar categoria se fornecida
    if estabelecimento.id_categoria is not None:
        if estabelecimento.id_categoria != db_estabelecimento.id_categoria:
            categoria = db.query(CategoriasEstabelecimentos).filter(
                CategoriasEstabelecimentos.id == estabelecimento.id_categoria
            ).first()
            if not categoria:
                raise HTTPException(
                    status_code=404,
                    detail=f"Categoria {estabelecimento.id_categoria} não encontrada"
                )
    
    # Atualizar campos fornecidos
    update_data = estabelecimento.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_estabelecimento, field, value)
    
    # updated_at não existe na tabela do banco
    # db_estabelecimento.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_estabelecimento)
    
    return db_estabelecimento


@router.delete("/{estabelecimento_id}", status_code=204)
def delete_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Deletar estabelecimento
    """
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_id
    ).first()
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    db.delete(estabelecimento)
    db.commit()
    return None
