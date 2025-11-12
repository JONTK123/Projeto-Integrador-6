from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.universidades import UniversidadesCreate, UniversidadesUpdate, UniversidadesResponse
from app.models.universidades import Universidades

router = APIRouter(prefix="/universidades", tags=["Universidades"])


@router.post("/", response_model=UniversidadesResponse, status_code=201)
def create_universidade(universidade: UniversidadesCreate, db: Session = Depends(get_db)):
    """
    Criar nova universidade
    """
    nova_universidade = Universidades(
        nome=universidade.nome,
        cidade=universidade.cidade,
        estado=universidade.estado
    )
    
    db.add(nova_universidade)
    db.commit()
    db.refresh(nova_universidade)
    
    return nova_universidade


@router.get("/", response_model=List[UniversidadesResponse])
def list_universidades(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    estado: str = Query(None, description="Filtrar por estado (UF)"),
    cidade: str = Query(None, description="Filtrar por cidade"),
    db: Session = Depends(get_db)
):
    """
    Listar todas as universidades com paginação e filtros opcionais
    """
    query = db.query(Universidades)
    
    if estado:
        query = query.filter(Universidades.estado == estado.upper())
    if cidade:
        query = query.filter(Universidades.cidade.ilike(f"%{cidade}%"))
    
    universidades = query.offset(skip).limit(limit).all()
    return universidades


@router.get("/{universidade_id}", response_model=UniversidadesResponse)
def get_universidade(universidade_id: int, db: Session = Depends(get_db)):
    """
    Obter universidade por ID
    """
    universidade = db.query(Universidades).filter(Universidades.id == universidade_id).first()
    if not universidade:
        raise HTTPException(
            status_code=404,
            detail=f"Universidade {universidade_id} não encontrada"
        )
    return universidade


@router.put("/{universidade_id}", response_model=UniversidadesResponse)
def update_universidade(
    universidade_id: int,
    universidade: UniversidadesUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar universidade
    """
    db_universidade = db.query(Universidades).filter(Universidades.id == universidade_id).first()
    if not db_universidade:
        raise HTTPException(
            status_code=404,
            detail=f"Universidade {universidade_id} não encontrada"
        )
    
    # Atualizar campos fornecidos
    update_data = universidade.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_universidade, field, value)
    
    # updated_at não existe na tabela do banco
    # db_universidade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_universidade)
    
    return db_universidade


@router.delete("/{universidade_id}", status_code=204)
def delete_universidade(universidade_id: int, db: Session = Depends(get_db)):
    """
    Deletar universidade
    
    ⚠️ Atenção: Verificar se há usuários associados antes de deletar
    """
    universidade = db.query(Universidades).filter(Universidades.id == universidade_id).first()
    if not universidade:
        raise HTTPException(
            status_code=404,
            detail=f"Universidade {universidade_id} não encontrada"
        )
    
    # Verificar se há usuários associados
    from app.models.usuarios import Usuarios
    usuarios_count = db.query(Usuarios).filter(Usuarios.id_universidade == universidade_id).count()
    if usuarios_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível deletar universidade. Existem {usuarios_count} usuário(s) associado(s)."
        )
    
    db.delete(universidade)
    db.commit()
    return None

