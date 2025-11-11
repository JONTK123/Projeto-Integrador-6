# 🚀 Quick Start

## Pré-requisitos
- Python 3.12
- Conda (para LightFM)
- PostgreSQL
- Node.js (para frontend)

## Início Rápido

### 1. Clonar e Configurar

```bash
git clone https://github.com/JONTK123/Projeto-Integrador-6.git
cd Projeto-Integrador-6

# Criar ambiente virtual
python3 -m venv backend/venv
source backend/venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais
```

### 2. Configurar Banco de Dados

```bash
# Executar migrations
alembic upgrade head
```

### 3. Iniciar Backend

```bash
# Opção A: Script automatizado (recomendado)
./iniciar_servidor.sh

# Opção B: Manual
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse: http://localhost:8000/docs

### 4. Treinar Modelos

```bash
# Surprise (funciona via API)
curl -X POST "http://localhost:8000/recomendacoes/treinar" \
  -H "Content-Type: application/json" \
  -d '{"algoritmo": "surprise", "algorithm": "svd"}'

# LightFM (manual via Conda)
conda run -n lightfm_py311 python backend/scripts/lightfm_train.py '{"loss":"warp","usar_features":true}'
```

### 5. Testar Sistema

```bash
# Teste completo
python backend/scripts/teste_completo_usuario.py

# Ou testar manualmente:
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"
```

### 6. Iniciar Frontend (Opcional)

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

## Estrutura

```
Projeto-Integrador-6/
├── backend/          # API FastAPI + ML
├── frontend/         # Interface React
├── alembic/          # Migrations
├── alembic.ini       # Config do Alembic
├── requirements.txt  # Dependências Python
└── iniciar_servidor.sh  # Script de início
```

## Endpoints Principais

- `GET /` - Health check
- `GET /recomendacoes/usuario/{id}` - Recomendações
- `POST /recomendacoes/interacao` - Registrar interação
- `POST /recomendacoes/treinar` - Treinar modelo

Documentação completa: http://localhost:8000/docs

## Problemas Comuns

**Erro de banco de dados**
- Verifique credenciais no `.env`
- Certifique-se que PostgreSQL está rodando

**LightFM não funciona via API**
- Execute servidor como usuário normal (não root)
- Ou use treinamento manual via Conda

**Frontend não conecta**
- Verifique se backend está rodando
- Confirme URL em `frontend/.env`
