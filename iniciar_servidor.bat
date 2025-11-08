@echo off
REM Script para iniciar servidor no Windows
REM Uso: iniciar_servidor.bat
REM 
REM Este script detecta automaticamente o caminho do Conda e configura
REM o ambiente necessário para executar o sistema de recomendação

REM Obter diretório do script
cd /d "%~dp0"

REM Detectar caminho do Conda automaticamente
where conda >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('conda info --base 2^>nul') do set CONDA_BASE=%%i
    if defined CONDA_BASE (
        set "CONDA_PYTHON_PATH=%CONDA_BASE%\envs\lightfm_py311\python.exe"
        if exist "%CONDA_PYTHON_PATH%" (
            echo ✅ Conda detectado: %CONDA_PYTHON_PATH%
        ) else (
            echo ⚠️  Ambiente Conda 'lightfm_py311' não encontrado em %CONDA_PYTHON_PATH%
            echo    Criando ambiente...
            conda create -n lightfm_py311 python=3.11 -y
            conda run -n lightfm_py311 pip install lightfm numpy scipy scikit-learn fastapi sqlalchemy pydantic python-dotenv psycopg2-binary pandas joblib
            set "CONDA_PYTHON_PATH=%CONDA_BASE%\envs\lightfm_py311\python.exe"
        )
    ) else (
        echo ⚠️  Conda não encontrado. LightFM pode não funcionar.
    )
) else (
    echo ⚠️  Conda não está instalado. Instale Conda para usar LightFM.
)

REM Verificar se venv existe
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar se dependências estão instaladas
python -c "import fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Instalando dependências...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

REM Verificar arquivo .env
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado!
    echo    Crie um arquivo .env com DATABASE_URL e outras configurações.
    echo    Veja INSTALACAO.md para mais detalhes.
)

REM Iniciar servidor
echo.
echo 🚀 Iniciando servidor FastAPI...
if defined CONDA_PYTHON_PATH (
    echo 📋 LightFM configurado via: %CONDA_PYTHON_PATH%
) else (
    echo ⚠️  LightFM não configurado. Apenas Surprise estará disponível.
)
echo 🌐 API disponível em: http://localhost:8000
echo 📖 Documentação: http://localhost:8000/docs
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

