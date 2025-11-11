from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    usuarios,
    estabelecimentos,
    preferencias,
    recomendacoes,
    universidades,
    categorias_estabelecimentos,
    usuario_preferencia,
    estabelecimento_preferencia,
    recomendacao_usuario
)

app = FastAPI(
    title="Sistema de Recomendação - LightFM & Surprise",
    description="""
    API para Sistema de Recomendação usando LightFM e Surprise.
    
    ## Algoritmos Disponíveis
    
    ### LightFM (Híbrido)
    Combina Content-Based Filtering (CBF) e Collaborative Filtering (CF) 
    para recomendar estabelecimentos personalizados para usuários universitários.
    
    * **CBF**: Baseado em características dos estabelecimentos e preferências do usuário
    * **CF**: Baseado em padrões de comportamento entre usuários
    * **Híbrido**: Combina ambas as estratégias para melhor performance
    * **Cold Start**: Resolve através de features/preferências
    
    ### Surprise (CF Puro)
    Biblioteca focada em algoritmos de Collaborative Filtering.
    
    * **Algoritmos**: SVD, KNN, Baseline, CoClustering
    * **Ideal para**: Comparação e baseline
    * **Uso**: Quando há apenas histórico de interações
    
    ## Funcionalidades
    
    * **Recomendações Personalizadas**: Para cada usuário
    * **Cold Start**: Suporte para usuários e estabelecimentos novos
    * **Contextual**: Recomendações baseadas em localização e tempo
    * **Diversidade**: Evita bolha de filtro
    * **Comparação**: Compare resultados de ambos os algoritmos
    """,
    version="1.0.0",
    contact={
        "name": "ALGORITHMA 3 AI",
        "email": "douglas.abreu@algorithma.com.br",
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router)
app.include_router(estabelecimentos.router)
app.include_router(preferencias.router)
app.include_router(universidades.router)
app.include_router(categorias_estabelecimentos.router)
app.include_router(usuario_preferencia.router)
app.include_router(estabelecimento_preferencia.router)
app.include_router(recomendacao_usuario.router)
app.include_router(recomendacoes.router)


@app.get("/", tags=["Health"])
def root():
    """
    Endpoint raiz - Health check
    """
    return {
        "status": "online",
        "message": "Sistema de Recomendação LightFM API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Verificar saúde da API, banco de dados e modelos
    """
    from app.core.database import SessionLocal, engine
    from pathlib import Path
    import os
    
    health_status = {
        "status": "healthy",
        "api": "online",
        "database": "unknown",
        "models": {
            "lightfm": "unknown",
            "surprise": "unknown"
        }
    }
    
    # Verificar conexão com banco de dados
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Verificar modelos
    models_dir = Path(__file__).parent.parent / "models"
    
    # LightFM
    lightfm_path = models_dir / "lightfm_model.pkl"
    if lightfm_path.exists():
        health_status["models"]["lightfm"] = "trained"
    else:
        health_status["models"]["lightfm"] = "not_trained"
    
    # Surprise
    surprise_path = models_dir / "surprise_model.pkl"
    if surprise_path.exists():
        health_status["models"]["surprise"] = "trained"
    else:
        health_status["models"]["surprise"] = "not_trained"
    
    return health_status
