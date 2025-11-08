from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.estabelecimentos import EstabelecimentosCreate, EstabelecimentosUpdate, EstabelecimentosResponse
from app.models.estabelecimentos import Estabelecimentos

router = APIRouter(prefix="/estabelecimentos", tags=["Estabelecimentos"])


@router.post("/", response_model=EstabelecimentosResponse, status_code=201)
def create_estabelecimento(estabelecimento: EstabelecimentosCreate, db: Session = Depends(get_db)):
    """
    Criar novo estabelecimento
    """
    # TODO: Implementar lógica de criação
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=List[EstabelecimentosResponse])
def list_estabelecimentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todos os estabelecimentos com paginação
    
    - **skip**: Número de registros para pular (padrão: 0)
    - **limit**: Número máximo de registros para retornar (padrão: 100, máximo: 1000)
    """
    # Validar limite máximo
    if limit > 1000:
        limit = 1000
    if limit < 1:
        limit = 1
    if skip < 0:
        skip = 0
    
    # Buscar estabelecimentos no banco de dados
    # Selecionar apenas colunas que existem (sem created_at e updated_at)
    stmt = select(
        Estabelecimentos.id,
        Estabelecimentos.descricao,
        Estabelecimentos.endereco,
        Estabelecimentos.cidade,
        Estabelecimentos.horario_funcionamento,
        Estabelecimentos.dono_nome,
        Estabelecimentos.dono_email,
        Estabelecimentos.id_categoria
    ).offset(skip).limit(limit)
    
    result = db.execute(stmt)
    rows = result.all()
    
    # Converter para objetos Estabelecimentos
    estabelecimentos = []
    for row in rows:
        estab = Estabelecimentos()
        estab.id = row.id
        estab.descricao = row.descricao
        estab.endereco = row.endereco
        estab.cidade = row.cidade
        estab.horario_funcionamento = row.horario_funcionamento
        estab.dono_nome = row.dono_nome
        estab.dono_email = row.dono_email
        estab.id_categoria = row.id_categoria
        # created_at e updated_at serão None (já definido como opcional no schema)
        estabelecimentos.append(estab)
    
    return estabelecimentos


@router.get("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def get_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Obter estabelecimento por ID
    """
    # TODO: Implementar lógica de busca
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{estabelecimento_id}", response_model=EstabelecimentosResponse)
def update_estabelecimento(estabelecimento_id: int, estabelecimento: EstabelecimentosUpdate, db: Session = Depends(get_db)):
    """
    Atualizar estabelecimento
    """
    # TODO: Implementar lógica de atualização
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{estabelecimento_id}", status_code=204)
def delete_estabelecimento(estabelecimento_id: int, db: Session = Depends(get_db)):
    """
    Deletar estabelecimento
    """
    # TODO: Implementar lógica de deleção
    raise HTTPException(status_code=501, detail="Not implemented")
