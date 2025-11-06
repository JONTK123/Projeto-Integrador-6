from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from pydantic import BaseModel
try:
    from app.services.lightfm_service import LightFMService
    LIGHTFM_AVAILABLE = True
except ImportError:
    LIGHTFM_AVAILABLE = False
    LightFMService = None

from app.services.surprise_service import SurpriseService
from app.models.recomendacao_estabelecimento import RecomendacaoEstabelecimento
from app.models.usuarios import Usuarios
from app.models.estabelecimentos import Estabelecimentos
from datetime import datetime

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])

# Instâncias globais dos serviços (singleton)
lightfm_service = LightFMService() if LIGHTFM_AVAILABLE else None
surprise_service = SurpriseService()


class RecomendacaoItem(BaseModel):
    """Schema para item de recomendação"""
    estabelecimento_id: int
    score: float
    razao: Optional[str] = None


class RecomendacaoResponse(BaseModel):
    """Schema de resposta de recomendações"""
    usuario_id: int
    recomendacoes: List[RecomendacaoItem]
    tipo: str  # 'hybrid', 'cbf', 'cf'
    algoritmo: str  # 'lightfm' ou 'surprise'


class InteracaoRequest(BaseModel):
    """Schema para registro de interação"""
    usuario_id: int
    estabelecimento_id: int
    tipo_interacao: str  # 'visita', 'clique', 'favorito'
    peso: float = 1.0


class TreinarRequest(BaseModel):
    """Schema para treinamento de modelo"""
    algoritmo: str = "lightfm"  # 'lightfm' ou 'surprise'
    usar_features: bool = True
    loss: str = "warp"  # Para LightFM: 'warp', 'bpr', 'logistic'
    algorithm: str = "svd"  # Para Surprise: 'svd', 'knn_basic', etc.
    num_epochs: Optional[int] = None
    learning_rate: Optional[float] = None
    num_components: Optional[int] = None


@router.get("/usuario/{usuario_id}", response_model=RecomendacaoResponse)
def get_recomendacoes_usuario(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações a retornar"),
    tipo: str = Query("hybrid", description="Tipo de recomendação: 'hybrid', 'cbf', 'cf'"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Obter recomendações personalizadas para um usuário
    
    - **usuario_id**: ID do usuário
    - **top_n**: Quantidade de recomendações (padrão: 10)
    - **tipo**: Tipo de filtragem (apenas para LightFM)
        - 'hybrid': Combinação de CBF e CF (padrão do LightFM)
        - 'cbf': Content-Based Filtering (baseado em características)
        - 'cf': Collaborative Filtering (baseado em comportamento de usuários similares)
    - **algoritmo**: 'lightfm' (híbrido) ou 'surprise' (CF puro)
    """
    # Verificar se usuário existe
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        if algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE:
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível. Instale: pip install lightfm"
                )
            # Usar LightFM
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
            algo_name = "lightfm"
        elif algoritmo.lower() == "surprise":
            # Usar Surprise
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
            algo_name = "surprise"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{algoritmo}' não suportado. Use 'lightfm' ou 'surprise'"
            )
        
        # Buscar informações dos estabelecimentos
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = db.query(Estabelecimentos).filter(
                Estabelecimentos.id == estabelecimento_id
            ).first()
            
            razao = None
            if estabelecimento:
                razao = f"Score: {score:.3f} - {estabelecimento.descricao[:50]}"
            
            recomendacoes.append(RecomendacaoItem(
                estabelecimento_id=estabelecimento_id,
                score=score,
                razao=razao
            ))
        
        return RecomendacaoResponse(
            usuario_id=usuario_id,
            recomendacoes=recomendacoes,
            tipo=tipo,
            algoritmo=algo_name
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")


@router.get("/estabelecimento/{estabelecimento_id}/similares")
def get_estabelecimentos_similares(
    estabelecimento_id: int,
    top_n: int = Query(10, description="Número de estabelecimentos similares"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Obter estabelecimentos similares (item-item similarity)
    
    Útil para "Pessoas que visitaram X também visitaram Y"
    """
    # Verificar se estabelecimento existe
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_id
    ).first()
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    try:
        if algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE or lightfm_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível. Instale: pip install lightfm"
                )
            similar_items = lightfm_service.get_similar_items(
                item_id=estabelecimento_id,
                num_items=top_n
            )
        elif algoritmo.lower() == "surprise":
            try:
                similar_items = surprise_service.get_similar_items(
                    item_id=estabelecimento_id,
                    num_items=top_n
                )
            except (ValueError, AttributeError) as e:
                # Se não suporta similaridade, retornar itens populares
                from sqlalchemy import func
                popular = db.query(
                    RecomendacaoEstabelecimento.id_lugar,
                    func.avg(RecomendacaoEstabelecimento.score).label('avg_score')
                ).group_by(RecomendacaoEstabelecimento.id_lugar).order_by(
                    func.avg(RecomendacaoEstabelecimento.score).desc()
                ).limit(top_n).all()
                similar_items = [(item.id_lugar, float(item.avg_score)) for item in popular]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{algoritmo}' não suportado"
            )
        
        return {
            "estabelecimento_id": estabelecimento_id,
            "algoritmo": algoritmo,
            "similares": [
                {
                    "estabelecimento_id": item_id,
                    "similaridade": score
                }
                for item_id, score in similar_items
            ]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/interacao")
def registrar_interacao(
    interacao: InteracaoRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar interação implícita do usuário com estabelecimento
    
    Essencial para treinar os modelos com feedback implícito
    """
    # Verificar se usuário e estabelecimento existem
    usuario = db.query(Usuarios).filter(Usuarios.id == interacao.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {interacao.usuario_id} não encontrado"
        )
    
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == interacao.estabelecimento_id
    ).first()
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {interacao.estabelecimento_id} não encontrado"
        )
    
    # Mapear tipo de interação para score
    score_map = {
        "visita": 5,
        "favorito": 4,
        "clique": 3
    }
    
    score = int(score_map.get(interacao.tipo_interacao.lower(), 3) * interacao.peso)
    score = max(1, min(5, score))  # Garantir entre 1-5
    
    # Verificar se já existe interação
    existing = db.query(RecomendacaoEstabelecimento).filter(
        RecomendacaoEstabelecimento.id_usuario == interacao.usuario_id,
        RecomendacaoEstabelecimento.id_lugar == interacao.estabelecimento_id
    ).first()
    
    if existing:
        # Atualizar score existente
        existing.score = score
        existing.updated_at = datetime.utcnow()
    else:
        # Criar nova interação
        nova_interacao = RecomendacaoEstabelecimento(
            id_usuario=interacao.usuario_id,
            id_lugar=interacao.estabelecimento_id,
            score=score,
            data_recomendacao=datetime.utcnow().date()
        )
        db.add(nova_interacao)
    
    db.commit()
    
    return {
        "message": "Interação registrada com sucesso",
        "usuario_id": interacao.usuario_id,
        "estabelecimento_id": interacao.estabelecimento_id,
        "tipo": interacao.tipo_interacao,
        "score": score
    }


@router.post("/treinar")
def treinar_modelo(
    request: TreinarRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Treinar modelo LightFM ou Surprise com dados atualizados
    
    - **algoritmo**: 'lightfm' ou 'surprise'
    - **usar_features**: (LightFM) Se True, usa metadados para CBF
    - **loss**: (LightFM) Função de perda ('warp', 'bpr', 'logistic')
    - **algorithm**: (Surprise) Algoritmo ('svd', 'knn_basic', 'knn_means', etc.)
    """
    try:
        if request.algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE or lightfm_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível. Instale: pip install lightfm"
                )
            # Treinar LightFM
            metrics = lightfm_service.train(
                db=db,
                loss=request.loss,
                use_features=request.usar_features,
                num_epochs=request.num_epochs or 30,
                learning_rate=request.learning_rate or 0.05,
                num_components=request.num_components or 30
            )
            
            # Salvar modelo
            lightfm_service.save_model()
            
            return {
                "message": "Modelo LightFM treinado com sucesso",
                "algoritmo": "lightfm",
                "metricas": metrics
            }
        
        elif request.algoritmo.lower() == "surprise":
            # Treinar Surprise
            # Filtrar parâmetros, removendo os que não são do Surprise
            kwargs = {k: v for k, v in request.dict().items() 
                     if k not in ['algoritmo', 'usar_features', 'loss', 'algorithm'] and v is not None}
            
            metrics = surprise_service.train(
                db=db,
                algorithm=request.algorithm,
                **kwargs
            )
            
            # Salvar modelo
            surprise_service.save_model()
            
            return {
                "message": "Modelo Surprise treinado com sucesso",
                "algoritmo": "surprise",
                "algorithm": request.algorithm,
                "metricas": metrics
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{request.algoritmo}' não suportado. Use 'lightfm' ou 'surprise'"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao treinar modelo: {str(e)}")


@router.get("/cold-start/usuario/{usuario_id}")
def cold_start_usuario(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações para usuário novo (cold start)
    
    - LightFM: Usa apenas CBF baseado nas preferências declaradas
    - Surprise: Retorna itens mais populares
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        if algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE or lightfm_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível. Instale: pip install lightfm"
                )
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = db.query(Estabelecimentos).filter(
                Estabelecimentos.id == estabelecimento_id
            ).first()
            
            recomendacoes.append({
                "estabelecimento_id": estabelecimento_id,
                "score": score,
                "descricao": estabelecimento.descricao if estabelecimento else None
            })
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "cold_start",
            "recomendacoes": recomendacoes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cold-start/estabelecimento/{estabelecimento_id}")
def cold_start_estabelecimento(
    estabelecimento_id: int,
    db: Session = Depends(get_db)
):
    """
    Verificar se estabelecimento novo está pronto para ser recomendado
    
    Retorna quais metadados estão faltando para melhor performance
    """
    estabelecimento = db.query(Estabelecimentos).filter(
        Estabelecimentos.id == estabelecimento_id
    ).first()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    # Verificar features/preferências
    from app.models.estabelecimento_preferencia import EstabelecimentoPreferencia
    
    features = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id_estabelecimento == estabelecimento_id
    ).all()
    
    # Verificar interações
    interacoes = db.query(RecomendacaoEstabelecimento).filter(
        RecomendacaoEstabelecimento.id_lugar == estabelecimento_id
    ).count()
    
    status = "pronto" if len(features) >= 3 and interacoes >= 5 else "precisa_melhorar"
    
    return {
        "estabelecimento_id": estabelecimento_id,
        "status": status,
        "features_count": len(features),
        "interacoes_count": interacoes,
        "recomendacoes": {
            "min_features": 3,
            "min_interacoes": 5,
            "tem_features_suficientes": len(features) >= 3,
            "tem_interacoes_suficientes": interacoes >= 5
        }
    }


@router.get("/diversidade/usuario/{usuario_id}")
def get_recomendacoes_diversas(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    explorar: float = Query(0.1, description="Taxa de exploração (0-1)"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações com diversidade (evita bolha de filtro)
    
    Usa estratégia epsilon-greedy para balancear relevância e diversidade
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    import random
    
    try:
        # Obter recomendações normais
        if algoritmo.lower() == "lightfm":
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,  # Pegar mais para diversificar
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        # Aplicar diversidade: explorar com probabilidade 'explorar'
        if random.random() < explorar:
            # Modo exploração: pegar itens aleatórios
            all_items = db.query(Estabelecimentos.id).all()
            random_items = random.sample([item[0] for item in all_items], min(top_n, len(all_items)))
            predictions = [(item_id, 0.5) for item_id in random_items]
        else:
            # Modo exploração: usar top N
            predictions = predictions[:top_n]
        
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = db.query(Estabelecimentos).filter(
                Estabelecimentos.id == estabelecimento_id
            ).first()
            
            recomendacoes.append({
                "estabelecimento_id": estabelecimento_id,
                "score": score,
                "descricao": estabelecimento.descricao if estabelecimento else None
            })
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "diversidade",
            "explorar": explorar,
            "recomendacoes": recomendacoes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contexto/usuario/{usuario_id}")
def get_recomendacoes_contextuais(
    usuario_id: int,
    hora_atual: Optional[int] = Query(None, description="Hora do dia (0-23)"),
    dia_semana: Optional[int] = Query(None, description="Dia da semana (0-6)"),
    latitude: Optional[float] = Query(None, description="Latitude do usuário"),
    longitude: Optional[float] = Query(None, description="Longitude do usuário"),
    top_n: int = Query(10, description="Número de recomendações"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações contextuais baseadas em localização e tempo
    
    Considera:
    - Horário de funcionamento
    - Distância do usuário
    - Horários de pico
    - Padrões por dia da semana
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        # Obter recomendações base
        if algoritmo.lower() == "lightfm":
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        # Filtrar por contexto
        from app.models.estabelecimentos import Estabelecimentos
        
        recomendacoes_contextuais = []
        for estabelecimento_id, score in predictions:
            estabelecimento = db.query(Estabelecimentos).filter(
                Estabelecimentos.id == estabelecimento_id
            ).first()
            
            if not estabelecimento:
                continue
            
            # Verificar horário de funcionamento
            if hora_atual is not None and estabelecimento.horario_funcionamento:
                # Simplificado: verificar se está dentro do horário
                # Em produção, fazer parsing completo do horário
                pass
            
            # Ajustar score baseado em contexto
            context_score = score
            
            # Se tem localização, poderia calcular distância aqui
            # Por enquanto, apenas retornar com score ajustado
            
            recomendacoes_contextuais.append({
                "estabelecimento_id": estabelecimento_id,
                "score": context_score,
                "score_original": score,
                "descricao": estabelecimento.descricao,
                "horario_funcionamento": estabelecimento.horario_funcionamento
            })
        
        # Ordenar por score contextual e pegar top N
        recomendacoes_contextuais.sort(key=lambda x: x["score"], reverse=True)
        recomendacoes_contextuais = recomendacoes_contextuais[:top_n]
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "contextual",
            "contexto": {
                "hora_atual": hora_atual,
                "dia_semana": dia_semana,
                "latitude": latitude,
                "longitude": longitude
            },
            "recomendacoes": recomendacoes_contextuais
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparar/{usuario_id}")
def comparar_algoritmos(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    db: Session = Depends(get_db)
):
    """
    Compara recomendações de LightFM e Surprise para o mesmo usuário
    """
    usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        # LightFM
        if LIGHTFM_AVAILABLE and lightfm_service is not None:
            lightfm_predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        else:
            lightfm_predictions = []
        
        # Surprise
        surprise_predictions = surprise_service.predict(
            user_id=usuario_id,
            num_items=top_n,
            db=db
        )
        
        # Comparar
        lightfm_ids = {item_id for item_id, _ in lightfm_predictions}
        surprise_ids = {item_id for item_id, _ in surprise_predictions}
        
        intersection = lightfm_ids.intersection(surprise_ids)
        
        return {
            "usuario_id": usuario_id,
            "comparacao": {
                "lightfm": {
                    "recomendacoes": [
                        {"estabelecimento_id": item_id, "score": score}
                        for item_id, score in lightfm_predictions
                    ],
                    "total": len(lightfm_predictions)
                },
                "surprise": {
                    "recomendacoes": [
                        {"estabelecimento_id": item_id, "score": score}
                        for item_id, score in surprise_predictions
                    ],
                    "total": len(surprise_predictions)
                },
                "intersecao": {
                    "itens_comuns": list(intersection),
                    "total_comum": len(intersection),
                    "percentual_comum": len(intersection) / max(len(lightfm_ids), 1) * 100
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
