#!/bin/bash
# Script para iniciar servidor com LightFM funcionando
# Uso: ./iniciar_servidor.sh
# 
# Este script detecta automaticamente o caminho do Conda e configura
# o ambiente necessário para executar o sistema de recomendação
#
# ============================================================================
# CONFIGURAÇÃO MANUAL DO CONDA (se necessário):
# ============================================================================
# Se o script não detectar o Conda automaticamente, você pode configurá-lo
# manualmente executando os seguintes comandos:
#
# 1. Criar ambiente Conda com Python 3.11:
#    conda create -n lightfm_py311 python=3.11 -y
#    conda activate lightfm_py311
#
# 2. Instalar pacotes científicos via Conda (recomendado):
#    conda install -y numpy scipy scikit-learn pandas -c conda-forge
#
# 3. Instalar LightFM e dependências do projeto:
#    pip install lightfm fastapi sqlalchemy pydantic python-dotenv psycopg2-binary joblib
#
# 4. Desativar ambiente:
#    conda deactivate
#
# O script tentará criar o ambiente automaticamente se não existir, mas
# a instalação manual garante melhor controle sobre as versões dos pacotes.
# ============================================================================

# Obter diretório do script (raiz do projeto)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detectar caminho do Conda automaticamente
if command -v conda &> /dev/null; then
    CONDA_BASE=$(conda info --base 2>/dev/null)
    if [ -n "$CONDA_BASE" ]; then
        CONDA_PYTHON_PATH="$CONDA_BASE/envs/lightfm_py311/bin/python3.11"
        if [ -f "$CONDA_PYTHON_PATH" ]; then
            export CONDA_PYTHON_PATH
            echo "✅ Conda detectado: $CONDA_PYTHON_PATH"
        else
            echo "⚠️  Ambiente Conda 'lightfm_py311' não encontrado em $CONDA_PYTHON_PATH"
            echo "   Criando ambiente automaticamente..."
            echo "   (Para configuração manual, veja os comentários no início do script)"
            conda create -n lightfm_py311 python=3.11 -y
            # Instalar pacotes científicos via Conda (recomendado para melhor performance)
            conda install -n lightfm_py311 -y numpy scipy scikit-learn pandas -c conda-forge
            # Instalar LightFM e dependências do projeto via pip
            conda run -n lightfm_py311 pip install lightfm fastapi sqlalchemy pydantic python-dotenv psycopg2-binary joblib
            CONDA_PYTHON_PATH="$CONDA_BASE/envs/lightfm_py311/bin/python3.11"
            export CONDA_PYTHON_PATH
            echo "✅ Ambiente Conda 'lightfm_py311' criado com sucesso!"
        fi
    else
        echo "⚠️  Conda não encontrado. LightFM pode não funcionar."
        echo "   Para instalar Conda, visite: https://docs.conda.io/en/latest/miniconda.html"
        echo "   Após instalar, configure o ambiente seguindo as instruções no início deste script."
    fi
else
    echo "⚠️  Conda não está instalado. Instale Conda para usar LightFM."
    echo "   Para instalar Conda, visite: https://docs.conda.io/en/latest/miniconda.html"
    echo "   Após instalar, configure o ambiente seguindo as instruções no início deste script."
fi

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se dependências estão instaladas
if ! python -c "import fastapi" &> /dev/null; then
    echo "📦 Instalando dependências..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "   Crie um arquivo .env com DATABASE_URL e outras configurações."
    echo "   Veja INSTALACAO.md para mais detalhes."
fi

# Mudar para o diretório backend
cd backend

# Iniciar servidor
echo ""
echo "🚀 Iniciando servidor FastAPI..."
if [ -n "$CONDA_PYTHON_PATH" ]; then
    echo "📋 LightFM configurado via: $CONDA_PYTHON_PATH"
else
    echo "⚠️  LightFM não configurado. Apenas Surprise estará disponível."
fi
echo "🌐 API disponível em: http://localhost:8000"
echo "📖 Documentação: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

