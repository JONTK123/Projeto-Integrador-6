from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import usuarios, estabelecimentos, preferencias, recomendacoes

app = FastAPI(
    title="Sistema de Recomendação LightFM",
    description="""
    API para Sistema de Recomendação Híbrido usando LightFM.
    
    Combina Content-Based Filtering (CBF) e Collaborative Filtering (CF) 
    para recomendar estabelecimentos personalizados para usuários universitários.
    
    ## Funcionalidades
    
    * **CBF**: Baseado em características dos estabelecimentos e preferências do usuário
    * **CF**: Baseado em padrões de comportamento entre usuários
    * **Híbrido**: Combina ambas as estratégias para melhor performance
    * **Cold Start**: Suporte para usuários e estabelecimentos novos
    * **Contextual**: Recomendações baseadas em localização e tempo
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
    Verificar saúde da API
    """
    return {
        "status": "healthy",
        "database": "not_configured",  # TODO: verificar conexão com DB
        "modelo": "not_trained"  # TODO: verificar status do modelo
    }
