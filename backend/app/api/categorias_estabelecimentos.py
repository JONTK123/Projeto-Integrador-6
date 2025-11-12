from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.categorias_estabelecimentos import (
    CategoriasEstabelecimentosCreate,
    CategoriasEstabelecimentosUpdate,
    CategoriasEstabelecimentosResponse
)
from app.models.categorias_estabelecimentos import CategoriasEstabelecimentos

router = APIRouter(prefix="/categorias-estabelecimentos", tags=["Categorias de Estabelecimentos"])


@router.post("/", response_model=CategoriasEstabelecimentosResponse, status_code=201)
def create_categoria(categoria: CategoriasEstabelecimentosCreate, db: Session = Depends(get_db)):
    """
    Criar nova categoria de estabelecimento
    
    Validações:
    - Nome da categoria deve ser único
    """
    # Verificar se categoria já existe
    existing = db.query(CategoriasEstabelecimentos).filter(
        CategoriasEstabelecimentos.nome_categoria == categoria.nome_categoria
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Categoria '{categoria.nome_categoria}' já existe"
        )
    
    nova_categoria = CategoriasEstabelecimentos(
        nome_categoria=categoria.nome_categoria
    )
    
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    
    return nova_categoria


@router.get("/", response_model=List[CategoriasEstabelecimentosResponse])
def list_categorias(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar todas as categorias de estabelecimentos com paginação
    """
    categorias = db.query(CategoriasEstabelecimentos).offset(skip).limit(limit).all()
    return categorias


@router.get("/{categoria_id}", response_model=CategoriasEstabelecimentosResponse)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Obter categoria por ID
    """
    categoria = db.query(CategoriasEstabelecimentos).filter(
        CategoriasEstabelecimentos.id == categoria_id
    ).first()
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail=f"Categoria {categoria_id} não encontrada"
        )
    return categoria


@router.put("/{categoria_id}", response_model=CategoriasEstabelecimentosResponse)
def update_categoria(
    categoria_id: int,
    categoria: CategoriasEstabelecimentosUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar categoria de estabelecimento
    
    Validações:
    - Nome da categoria deve ser único (se fornecido)
    """
    db_categoria = db.query(CategoriasEstabelecimentos).filter(
        CategoriasEstabelecimentos.id == categoria_id
    ).first()
    if not db_categoria:
        raise HTTPException(
            status_code=404,
            detail=f"Categoria {categoria_id} não encontrada"
        )
    
    # Verificar se nome já existe (se estiver sendo alterado)
    if categoria.nome_categoria and categoria.nome_categoria != db_categoria.nome_categoria:
        existing = db.query(CategoriasEstabelecimentos).filter(
            CategoriasEstabelecimentos.nome_categoria == categoria.nome_categoria
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Categoria '{categoria.nome_categoria}' já existe"
            )
    
    # Atualizar campos fornecidos
    update_data = categoria.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_categoria, field, value)
    
    # updated_at não existe na tabela do banco
    # db_categoria.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.delete("/{categoria_id}", status_code=204)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Deletar categoria de estabelecimento
    
    ⚠️ Atenção: Verificar se há estabelecimentos associados antes de deletar
    """
    categoria = db.query(CategoriasEstabelecimentos).filter(
        CategoriasEstabelecimentos.id == categoria_id
    ).first()
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail=f"Categoria {categoria_id} não encontrada"
        )
    
    # Verificar se há estabelecimentos associados
    from app.models.estabelecimentos import Estabelecimentos
    estabelecimentos_count = db.query(Estabelecimentos).filter(
        Estabelecimentos.id_categoria == categoria_id
    ).count()
    if estabelecimentos_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível deletar categoria. Existem {estabelecimentos_count} estabelecimento(s) associado(s)."
        )
    
    db.delete(categoria)
    db.commit()
    return None

