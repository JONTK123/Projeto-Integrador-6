# 🎯 Sistema de Recomendação Híbrido - LightFM & Surprise

[![Python](https://img.shields.io/badge/Python-3.11%2F3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

Sistema de recomendação híbrido desenvolvido com **FastAPI**, **LightFM** e **Surprise** para recomendar estabelecimentos personalizados para usuários universitários, combinando **Content-Based Filtering (CBF)** e **Collaborative Filtering (CF)**.

### 🚀 Início Rápido

```bash
# 1. Iniciar servidor
bash iniciar_servidor.sh

# 2. Treinar Surprise (funciona via API)
curl -X POST "http://localhost:8000/recomendacoes/treinar" \
  -H "Content-Type: application/json" \
  -d '{"algoritmo": "surprise", "algorithm": "svd"}'

# 3. Testar tudo
python scripts/teste_completo_usuario.py
```

### ⚡ Estado Atual

- ✅ **Surprise**: 100% funcional via API (VENV)
- ⚠️ **LightFM**: Funciona manualmente via Conda, requer ajustes para API quando servidor roda como root
- ✅ **Scripts**: Todos funcionais e documentados
- ✅ **API**: Todas as rotas implementadas e testadas

**📖 Veja seção [Estado Atual](#-treinamento-dos-modelos) para detalhes completos e soluções para LightFM.**

---

## 📋 Sumário

- [Descrição do Projeto](#-descrição-do-projeto)
- [Algoritmos Implementados](#-algoritmos-implementados)
- [Arquitetura](#️-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Treinamento dos Modelos](#-treinamento-dos-modelos)
- [Como Usar o Sistema](#-como-usar-o-sistema)
- [Endpoints da API](#-endpoints-da-api)
- [Testes](#-testes)
- [Status do Projeto](#-status-do-projeto)

---

## 📖 Descrição do Projeto

O sistema utiliza dois algoritmos de recomendação para gerar recomendações inteligentes de estabelecimentos (restaurantes, cafeterias, bibliotecas, etc.) para estudantes universitários:

- **LightFM**: Algoritmo híbrido que combina CBF e CF
- **Surprise**: Biblioteca focada em Collaborative Filtering puro

### 🎯 Objetivo

Desenvolver um sistema de recomendação completo que possa:

1. **Recomendar estabelecimentos personalizados** para cada usuário
2. **Resolver o problema de cold start** (novos usuários/estabelecimentos)
3. **Descobrir padrões ocultos** através de Collaborative Filtering
4. **Fornecer explicações** sobre as recomendações
5. **Evitar bolha de filtro** através de diversidade nas recomendações
6. **Suportar múltiplos algoritmos** para comparação

---

## 🧠 Algoritmos Implementados

### 1. LightFM - Hybrid Recommendation System

O **LightFM** é um modelo de fatorização de matrizes híbrido que combina:

#### Content-Based Filtering (CBF)
- **Features de Usuário**: Preferências declaradas (ex: "Silencioso para Estudo", "Wi-Fi Rápido")
- **Features de Estabelecimento**: Metadados (ex: "Comida Barata", "Café Especial")
- **Vantagens**: Funciona para cold start, explica recomendações

#### Collaborative Filtering (CF)
- **User-User**: "Usuários similares a você visitaram..."
- **Item-Item**: "Quem foi à Biblioteca também foi ao Café X"
- **Vantagens**: Descobre preferências implícitas, não precisa de metadados

#### Funções de Perda Suportadas
- **WARP** (Weighted Approximate-Rank Pairwise): Otimiza para ranking top-N
- **BPR** (Bayesian Personalized Ranking): Para feedback implícito
- **Logistic**: Para classificação binária

**⚠️ Nota**: LightFM requer Python 3.11 ou inferior. O projeto usa Conda para gerenciar o ambiente do LightFM.

### 2. Surprise - Collaborative Filtering Library

O **Surprise** é uma biblioteca focada em algoritmos de Collaborative Filtering puro:

#### Algoritmos Disponíveis
- **SVD**: Singular Value Decomposition (Matrix Factorization)
- **KNNBasic**: K-Nearest Neighbors básico
- **KNNWithMeans**: KNN com média dos ratings
- **KNNWithZScore**: KNN com normalização Z-score
- **BaselineOnly**: Baseline (média global + bias)
- **CoClustering**: Co-clustering

**Vantagens**: Mais simples, ideal para comparação e baseline, funciona com Python 3.12

---

## 🏗️ Arquitetura

### Stack Tecnológico

| Componente | Tecnologia | Versão | Descrição |
|------------|-----------|--------|-----------|
| **Backend** | FastAPI | 0.104+ | Framework web assíncrono |
| **Banco de Dados** | PostgreSQL | 12+ | BD relacional (AWS RDS) |
| **ORM** | SQLAlchemy | 2.0+ | Mapeamento objeto-relacional |
| **Validação** | Pydantic | 2.5+ | Validação de dados |
| **Migrações** | Alembic | 1.13+ | Controle de versão do banco |
| **ML Models** | LightFM + Surprise | - | Modelos de recomendação |
| **Server** | Uvicorn | 0.24+ | Servidor ASGI |
| **Ambiente LightFM** | Conda | - | Python 3.11 para LightFM |

### Estrutura de Diretórios

```
Projeto-Integrador-6/
│
├── 📁 app/                          # Código da aplicação
│   ├── 📁 api/                      # Rotas da API
│   │   ├── usuarios.py              # CRUD de usuários
│   │   ├── estabelecimentos.py      # CRUD de estabelecimentos
│   │   ├── preferencias.py          # CRUD de preferências
│   │   └── recomendacoes.py         # 🎯 Sistema de recomendação
│   │
│   ├── 📁 core/                     # Configurações centrais
│   │   └── database.py              # Conexão PostgreSQL
│   │
│   ├── 📁 models/                   # 🗄️ Modelos ORM (SQLAlchemy)
│   │   ├── usuarios.py
│   │   ├── estabelecimentos.py
│   │   ├── preferencias.py
│   │   ├── usuario_preferencia.py
│   │   ├── estabelecimento_preferencia.py
│   │   └── recomendacao_estabelecimento.py
│   │
│   ├── 📁 services/                 # 🧠 Serviços de ML
│   │   ├── lightfm_service.py       # Serviço LightFM
│   │   └── surprise_service.py      # Serviço Surprise
│   │
│   └── main.py                      # 🚀 App FastAPI principal
│
├── 📁 scripts/                      # Scripts auxiliares
│   ├── criar_banco.py               # Criar banco de dados
│   ├── seed_data.sql                # Dados iniciais (usado nas migrações)
│   ├── teste_completo_usuario.py      # Script completo de teste via API
│   ├── lightfm_train.py               # Script para treinar LightFM via Conda
│   └── lightfm_predict.py             # Script para predições LightFM via Conda
│
├── 📁 models/                       # Modelos treinados (gitignored)
│   ├── lightfm_model.pkl
│   └── surprise_model.pkl
│
├── 📄 requirements.txt              # Dependências Python
├── 📄 alembic.ini                   # Configuração Alembic
└── 📄 README.md                     # 📖 Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.12** (para ambiente principal)
- **Conda** ou **Miniconda** (para LightFM com Python 3.11)
- **PostgreSQL 12+** (local ou AWS RDS)
- **Git**

### Instalação Rápida

Para uma instalação completa e automatizada, veja **[INSTALACAO.md](INSTALACAO.md)**.

### Instalação Manual

#### 1. Clonar o Repositório

```bash
git clone https://github.com/JONTK123/Projeto-Integrador-6.git
cd Projeto-Integrador-6
```

#### 2. Criar Ambiente Virtual (Python 3.12)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

#### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar LightFM (Conda)

```bash
# Criar ambiente Conda com Python 3.11
conda create -n lightfm_py311 python=3.11 -y
conda activate lightfm_py311

# Instalar pacotes científicos via Conda (recomendado)
conda install -y numpy scipy scikit-learn pandas -c conda-forge

# Instalar LightFM e dependências do projeto
pip install lightfm fastapi sqlalchemy pydantic python-dotenv psycopg2-binary joblib

# Desativar ambiente
conda deactivate
```

**💡 Dica**: O script `iniciar_servidor.sh` detecta automaticamente o Conda e configura tudo!

---

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@host:5432/recommendation_system

# Para AWS RDS:
# DATABASE_URL=postgresql://admin:senha@seu-endpoint.rds.amazonaws.com:5432/recommendation_system

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 2. Criar Banco de Dados

```bash
# Usando script Python
python scripts/criar_banco.py

# Ou manualmente via psql
psql -h host -U usuario -d postgres -c "CREATE DATABASE recommendation_system;"
```

### 3. Executar Migrações

```bash
alembic upgrade head
```

Este comando irá:
- ✅ Criar todas as tabelas necessárias
- ✅ Popular com dados iniciais (usuários, estabelecimentos, preferências)

---

## 🎓 Treinamento dos Modelos

### ⚠️ Estado Atual dos Algoritmos

#### ✅ Surprise - Funcionando Perfeitamente via VENV

O **Surprise** está **100% funcional** e integrado via API:
- ✅ Treinamento via API: `POST /recomendacoes/treinar`
- ✅ Predições via API: `GET /recomendacoes/usuario/{id}?algoritmo=surprise`
- ✅ Todas funcionalidades disponíveis (cold start, similares, diversidade, contexto)
- ✅ Funciona diretamente no ambiente VENV (Python 3.12)
- ✅ Sem necessidade de configuração adicional

**Como usar:**
```bash
# 1. Iniciar servidor
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Treinar modelo via API
curl -X POST "http://localhost:8000/recomendacoes/treinar" \
  -H "Content-Type: application/json" \
  -d '{
    "algoritmo": "surprise",
    "algorithm": "svd",
    "n_factors": 50,
    "n_epochs": 20
  }'

# 3. Obter recomendações
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=10"
```

#### ⚠️ LightFM - Requer Integração Correta nas Rotas

O **LightFM** está parcialmente implementado:
- ✅ Scripts de treinamento e predição criados (`lightfm_train.py`, `lightfm_predict.py`)
- ✅ Endpoint de treinamento implementado (`POST /recomendacoes/treinar`)
- ✅ Endpoint de predição implementado (`GET /recomendacoes/usuario/{id}?algoritmo=lightfm`)
- ⚠️ **Problema**: Quando o servidor roda como root, não consegue executar o Python do Conda
- ⚠️ **Status**: Funciona quando executado manualmente via Conda, mas não via API quando servidor roda como root

**Como usar manualmente (funciona):**
```bash
# Treinar LightFM manualmente via Conda
conda run -n lightfm_py311 python scripts/lightfm_train.py '{"loss":"warp","usar_features":true,"num_epochs":30,"learning_rate":0.05,"num_components":30}'

# Fazer predição manualmente
conda run -n lightfm_py311 python scripts/lightfm_predict.py 101 10
```

**Problema identificado:**
- Quando o servidor FastAPI roda como root (ou em contexto diferente), o `subprocess.run()` não consegue executar o Python do Conda (`/home/thiago/GitHub/miniforge3/envs/lightfm_py311/bin/python3.11`)
- O arquivo existe e é acessível, mas há problemas de permissão/contexto ao executar

### 🔧 Sugestões para Resolver o Problema do LightFM

#### Opção 1: Executar Servidor como Usuário Normal (Recomendado)
```bash
# Em vez de rodar como root, executar como usuário thiago
su - thiago
cd /home/thiago/GitHub/Projeto-Integrador-6
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Opção 2: Usar `conda run` em vez de caminho direto
Modificar `app/api/recomendacoes.py` para usar `conda run`:
```python
# Em vez de:
[conda_python, str(script_path), ...]

# Usar:
["conda", "run", "-n", "lightfm_py311", "python", str(script_path), ...]
```
**Nota**: Já implementado, mas pode não funcionar se `conda` não estiver no PATH do servidor.

#### Opção 3: Criar Wrapper Script com Permissões Especiais
Criar um script wrapper que seja executável por qualquer usuário:
```bash
#!/bin/bash
# scripts/lightfm_wrapper.sh
export PATH="/home/thiago/GitHub/miniforge3/bin:$PATH"
conda run -n lightfm_py311 python "$@"
```

#### Opção 4: Usar Variável de Ambiente para Caminho do Conda
Configurar variável de ambiente no sistema:
```bash
export CONDA_PYTHON_PATH="/home/thiago/GitHub/miniforge3/envs/lightfm_py311/bin/python3.11"
```
E usar no código: `os.environ.get("CONDA_PYTHON_PATH", default_path)`

#### Opção 5: Executar LightFM em Processo Separado (Microserviço)
Criar um serviço separado que roda LightFM e se comunica via HTTP/Redis:
- Servidor principal (FastAPI) → Envia requisições
- Servidor LightFM (separado) → Processa e retorna resultados

### Script de Treinamento Completo (Recomendado)

Use o script completo que testa tudo via API:
```bash
# Executar teste completo (funciona com Surprise, LightFM pode falhar se servidor roda como root)
python scripts/teste_completo_usuario.py
```

Este script:
- ✅ Verifica/inicia servidor automaticamente
- ✅ Treina Surprise via API (funciona)
- ⚠️ Tenta treinar LightFM via API (pode falhar se servidor roda como root)
- ✅ Simula usuário com 20+ interações
- ✅ Testa todas funcionalidades
- ✅ Compara resultados entre algoritmos

---

## 👤 Como Usar o Sistema

### 🎯 Guia Passo a Passo para Usuário Final

#### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse a documentação interativa em: **http://localhost:8000/docs**

#### 2. Primeira Visita - Obter Recomendações Iniciais

Quando um usuário acessa o sistema pela primeira vez (sem histórico):

```bash
# Obter recomendações para usuário novo
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"
```

**Resposta:**
```json
{
  "usuario_id": 101,
  "algoritmo": "surprise",
  "recomendacoes": [
    {
      "estabelecimento_id": 203,
      "score": 4.145,
      "razao": "Score: 4.145 - Biblioteca Central da USP"
    },
    ...
  ]
}
```

#### 3. Registrar Interações

Quando o usuário visita ou interage com um estabelecimento:

```bash
# Registrar visita
curl -X POST "http://localhost:8000/recomendacoes/interacao" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 101,
    "estabelecimento_id": 203,
    "tipo_interacao": "visita",
    "score": 5
  }'

# Registrar favorito
curl -X POST "http://localhost:8000/recomendacoes/interacao" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 101,
    "estabelecimento_id": 204,
    "tipo_interacao": "favorito",
    "score": 4
  }'
```

**Tipos de interação disponíveis:**
- `visita`: Usuário visitou o local
- `favorito`: Usuário favoritou o local
- `clique`: Usuário clicou na recomendação

#### 4. Obter Recomendações Personalizadas

Após registrar interações, o sistema aprende e melhora as recomendações:

```bash
# Recomendações baseadas no histórico
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"
```

#### 5. Descobrir Lugares Similares

"Pessoas que visitaram X também visitaram Y":

```bash
curl "http://localhost:8000/recomendacoes/estabelecimento/203/similares?algoritmo=surprise&top_n=5"
```

#### 6. Explorar Lugares Diversos

Para evitar bolha de filtro e descobrir novos lugares:

```bash
curl "http://localhost:8000/recomendacoes/diversidade/usuario/101?top_n=5&explorar=0.3&algoritmo=surprise"
```

**Parâmetro `explorar`**: 
- `0.0` = Apenas recomendações baseadas no histórico
- `1.0` = Apenas lugares aleatórios
- `0.3` = 30% exploração, 70% histórico (recomendado)

#### 7. Recomendações Contextuais

Recomendações baseadas em hora, dia da semana e localização:

```bash
curl "http://localhost:8000/recomendacoes/contexto/usuario/101?top_n=5&hora_atual=14&dia_semana=1&algoritmo=surprise"
```

**Parâmetros:**
- `hora_atual`: Hora do dia (0-23)
- `dia_semana`: Dia da semana (0=segunda, 6=domingo)
- `latitude`: Latitude do usuário (opcional)
- `longitude`: Longitude do usuário (opcional)

#### 8. Comparar Algoritmos

Comparar recomendações de LightFM e Surprise:

```bash
curl "http://localhost:8000/recomendacoes/comparar/101?top_n=5"
```

---

## 📡 Endpoints da API

### 🏥 Health Check

```http
GET /
GET /health
```

**Resposta:**
```json
{
  "status": "online",
  "message": "Sistema de Recomendação LightFM API",
  "version": "1.0.0"
}
```

### 🎯 Sistema de Recomendação

#### 1. Recomendações Personalizadas

```http
GET /recomendacoes/usuario/{usuario_id}?algoritmo=surprise&top_n=10
```

**Parâmetros:**
- `algoritmo`: `surprise` ou `lightfm`
- `top_n`: Número de recomendações (padrão: 10)
- `tipo`: `hybrid`, `cbf` ou `cf` (apenas LightFM)

**Exemplo de Resposta:**
```json
{
  "usuario_id": 101,
  "algoritmo": "surprise",
  "recomendacoes": [
    {
      "estabelecimento_id": 203,
      "score": 4.145,
      "razao": "Score: 4.145 - Biblioteca Central da USP"
    }
  ]
}
```

#### 2. Estabelecimentos Similares

```http
GET /recomendacoes/estabelecimento/{estabelecimento_id}/similares?algoritmo=surprise&top_n=5
```

**Uso:** "Pessoas que visitaram X também visitaram Y"

#### 3. Registrar Interação

```http
POST /recomendacoes/interacao
Content-Type: application/json

{
  "usuario_id": 101,
  "estabelecimento_id": 203,
  "tipo_interacao": "visita",
  "score": 4
}
```

**Tipos de Interação:**
- `visita`: Usuário visitou o local (peso: 5)
- `favorito`: Usuário favoritou (peso: 4)
- `clique`: Usuário clicou (peso: 3)

#### 4. Treinar Modelo

```http
POST /recomendacoes/treinar
Content-Type: application/json

{
  "algoritmo": "surprise",
  "algorithm": "svd",
  "n_factors": 50,
  "n_epochs": 20
}
```

**Parâmetros para Surprise:**
- `algorithm`: `svd`, `knn_basic`, `knn_with_means`, `baseline_only`, `co_clustering`
- `n_factors`: Número de fatores (padrão: 50)
- `n_epochs`: Número de épocas (padrão: 20)

**Parâmetros para LightFM:**
- `loss`: `warp`, `bpr`, `logistic`
- `usar_features`: `true` ou `false`
- `num_epochs`: Número de épocas (padrão: 30)

#### 5. Cold Start - Usuário Novo

```http
GET /recomendacoes/cold-start/usuario/{usuario_id}?algoritmo=surprise&top_n=5
```

Usa apenas itens populares quando o usuário não tem histórico.

#### 6. Cold Start - Estabelecimento Novo

```http
GET /recomendacoes/cold-start/estabelecimento/{estabelecimento_id}
```

Verifica se o estabelecimento tem dados suficientes para recomendações.

#### 7. Recomendações Diversas

```http
GET /recomendacoes/diversidade/usuario/{usuario_id}?top_n=5&explorar=0.3&algoritmo=surprise
```

**Parâmetro `explorar`**: Taxa de exploração (0-1)
- `0.0` = Apenas histórico
- `1.0` = Apenas aleatório
- `0.3` = Balanceado (recomendado)

#### 8. Recomendações Contextuais

```http
GET /recomendacoes/contexto/usuario/{usuario_id}?top_n=5&hora_atual=14&dia_semana=1&algoritmo=surprise
```

Considera:
- Horário de funcionamento
- Distância do usuário
- Dia da semana
- Horários de pico

#### 9. Comparar Algoritmos

```http
GET /recomendacoes/comparar/{usuario_id}?top_n=10
```

Compara recomendações de LightFM e Surprise lado a lado.

---

## 💡 Exemplos de Uso Prático

### Exemplo 1: Fluxo Completo de Usuário

```bash
# 1. Usuário novo recebe recomendações iniciais
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"

# 2. Usuário visita um lugar recomendado
curl -X POST "http://localhost:8000/recomendacoes/interacao" \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 101, "estabelecimento_id": 203, "tipo_interacao": "visita", "score": 5}'

# 3. Usuário recebe novas recomendações (agora personalizadas)
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"

# 4. Usuário quer ver lugares similares
curl "http://localhost:8000/recomendacoes/estabelecimento/203/similares?algoritmo=surprise&top_n=5"

# 5. Usuário quer explorar lugares diversos
curl "http://localhost:8000/recomendacoes/diversidade/usuario/101?top_n=5&explorar=0.3&algoritmo=surprise"
```

### Exemplo 2: Usando Python

```python
import requests

BASE_URL = "http://localhost:8000"
usuario_id = 101

# Obter recomendações
response = requests.get(
    f"{BASE_URL}/recomendacoes/usuario/{usuario_id}",
    params={"algoritmo": "surprise", "top_n": 5}
)

recomendacoes = response.json()
print(f"Recomendações para usuário {usuario_id}:")
for rec in recomendacoes['recomendacoes']:
    print(f"  - Estabelecimento {rec['estabelecimento_id']}: {rec['score']:.2f}")

# Registrar interação
requests.post(
    f"{BASE_URL}/recomendacoes/interacao",
    json={
        "usuario_id": usuario_id,
    "estabelecimento_id": 203,
    "tipo_interacao": "visita",
        "score": 5
    }
)
```

### Exemplo 3: Usando JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000';
const usuarioId = 101;

// Obter recomendações
fetch(`${BASE_URL}/recomendacoes/usuario/${usuarioId}?algoritmo=surprise&top_n=5`)
  .then(response => response.json())
  .then(data => {
    console.log('Recomendações:', data.recomendacoes);
  });

// Registrar interação
fetch(`${BASE_URL}/recomendacoes/interacao`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    usuario_id: usuarioId,
    estabelecimento_id: 203,
    tipo_interacao: 'visita',
    score: 5
  })
});
```

---

## 🧪 Testes

### Teste Completo do Sistema

```bash
# Teste técnico completo (todas as rotas e modelos)
python scripts/teste_completo_usuario.py

# Teste como usuário final (fluxo completo de uso)
python scripts/teste_completo_usuario.py

# Teste completo (treinamento + rotas)
python scripts/teste_completo_usuario.py
```

### Testar Rotas Individualmente

```bash
# Health check
curl http://localhost:8000/

# Recomendações
curl "http://localhost:8000/recomendacoes/usuario/101?algoritmo=surprise&top_n=5"

# Estabelecimentos similares
curl "http://localhost:8000/recomendacoes/estabelecimento/201/similares?algoritmo=surprise&top_n=5"

# Registrar interação
curl -X POST "http://localhost:8000/recomendacoes/interacao" \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 101, "estabelecimento_id": 203, "tipo_interacao": "visita", "score": 4}'
```

### Documentação Interativa

Acesse **http://localhost:8000/docs** para:
- ✅ Ver todos os endpoints
- ✅ Testar rotas diretamente no navegador
- ✅ Ver exemplos de requisições e respostas
- ✅ Entender parâmetros e schemas

---

## 🚀 Executar a Aplicação

### Iniciar Servidor

```bash
# Ativar ambiente
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Acessar a Aplicação

- **API Base**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

---

## 📊 Status do Projeto

### ✅ **PROJETO FUNCIONAL COM SURPRISE - LIGHTFM REQUER AJUSTES**

#### Estado Atual (Novembro 2024)

**✅ Surprise - 100% Funcional**
- ✅ Treinamento via API funcionando perfeitamente
- ✅ Todas as rotas de recomendação funcionando
- ✅ Integrado no ambiente VENV (Python 3.12)
- ✅ Pronto para uso em produção

**⚠️ LightFM - Parcialmente Funcional**
- ✅ Scripts de treinamento e predição criados
- ✅ Endpoints implementados na API
- ⚠️ Problema de execução quando servidor roda como root
- ✅ Funciona quando executado manualmente via Conda
- 🔧 Requer ajustes de permissão/contexto para funcionar via API

#### Scripts Importantes

| Script | Descrição | Status |
|--------|-----------|--------|
| `teste_completo_usuario.py` | Teste completo via API (Surprise + LightFM) | ✅ Funcional |
| `lightfm_train.py` | Treinamento LightFM via Conda | ✅ Funcional (manual) |
| `lightfm_predict.py` | Predições LightFM via Conda | ✅ Funcional (manual) |
| `iniciar_servidor.sh` | Inicia servidor com configuração automática | ✅ Funcional |

#### Rotas Funcionando

1. ✅ Recomendações personalizadas (Surprise)
2. ✅ Estabelecimentos similares (Surprise)
3. ✅ Registrar interações
4. ✅ Treinar modelos (Surprise via API, LightFM manual)
5. ✅ Cold start usuário (Surprise)
6. ✅ Cold start estabelecimento
7. ✅ Recomendações diversas (Surprise)
8. ✅ Recomendações contextuais (Surprise)
9. ✅ Comparar algoritmos
10. ✅ Health check

#### Métricas dos Modelos

**Surprise (SVD)**:
- RMSE: ~1.0-1.3
- MAE: ~0.7-1.0
- Status: ✅ Treinado e funcionando via API

**LightFM**:
- Precision@10: ~0.14-0.17
- AUC: ~0.70-0.74
- Status: ⚠️ Treinado, mas requer execução manual via Conda

---

## 📦 Dependências Principais

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
pydantic[email]
python-dotenv
psycopg2-binary
alembic
scikit-surprise
numpy<2
scipy
joblib
pandas
requests
email-validator
```

**Nota**: LightFM é instalado separadamente no ambiente Conda.

---

## 🔧 Comandos Úteis

### Como Rodar o Sistema

#### 1. Iniciar Servidor

**Opção A: Usando script automatizado (Recomendado)**
```bash
cd /home/thiago/GitHub/Projeto-Integrador-6
bash iniciar_servidor.sh
```

**Opção B: Manualmente**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**⚠️ Importante**: Para LightFM funcionar via API, execute o servidor como usuário normal (não root):
```bash
su - thiago  # Se estiver como root
cd /home/thiago/GitHub/Projeto-Integrador-6
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Treinar Modelos

**Surprise (via API - Funciona):**
```bash
curl -X POST "http://localhost:8000/recomendacoes/treinar" \
  -H "Content-Type: application/json" \
  -d '{"algoritmo": "surprise", "algorithm": "svd", "n_factors": 50, "n_epochs": 20}'
```

**LightFM (manual via Conda - Funciona):**
```bash
conda run -n lightfm_py311 python scripts/lightfm_train.py '{"loss":"warp","usar_features":true,"num_epochs":30,"learning_rate":0.05,"num_components":30}'
```

#### 3. Executar Testes Completos

```bash
# Teste completo via API (Surprise funciona, LightFM pode falhar se servidor roda como root)
python scripts/teste_completo_usuario.py
```

#### 4. Acessar Documentação

Abra no navegador: **http://localhost:8000/docs**

### Verificar Modelos Treinados

```bash
ls -lh models/*.pkl
```

### Ver Logs do Servidor

```bash
# Logs aparecem no terminal onde o servidor está rodando
# Para modo produção, use:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
```

---

## 📚 Guia de Uso Detalhado

### Para Desenvolvedores

1. **Configurar ambiente**: Siga a seção [Instalação](#-instalação)
2. **Configurar banco**: Siga a seção [Configuração](#️-configuração)
3. **Treinar modelos**: Siga a seção [Treinamento dos Modelos](#-treinamento-dos-modelos)
4. **Testar API**: Use os scripts em `scripts/` ou acesse `/docs`

### Para Usuários Finais

1. **Acessar sistema**: Abra http://localhost:8000/docs
2. **Obter recomendações**: Use o endpoint `/recomendacoes/usuario/{id}`
3. **Registrar interações**: Use o endpoint `/recomendacoes/interacao`
4. **Explorar funcionalidades**: Veja todos os endpoints em `/docs`

### Para Testadores

**Teste completo**: `python scripts/teste_completo_usuario.py`

Este script executa todos os testes via API:
- Treina modelos Surprise e LightFM
- Simula usuário com 20+ interações
- Testa todas as funcionalidades (cold start, recomendações, similares, diversidade, contexto)
- Compara resultados entre algoritmos

---

## 👥 Equipe

### Desenvolvido por

**ALGORITHMA 3 AI**  
Douglas Henrique Siqueira Abreu Tecnologia da Informação LTDA  
CNPJ: 56.420.666/0001-53

📧 Email: douglas.abreu@algorithma.com.br  
💼 LinkedIn: [douglashsabreu](https://linkedin.com/in/douglashsabreu/)  
📱 Telefone: +55 (19) 99212-5712  
📍 Localização: Av. Paulista, São Paulo - SP

---

## 📄 Licença

Este projeto está em desenvolvimento como parte de um projeto R&D de sistema de recomendação.

**© 2024 ALGORITHMA 3 AI. Todos os direitos reservados.**

---

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LightFM Documentation](https://making.lyst.com/lightfm/docs/home.html)
- [Surprise Documentation](https://surpriselib.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## ❓ FAQ

<details>
<summary><strong>Como adicionar um novo usuário?</strong></summary>

Use o endpoint `POST /usuarios/` ou adicione diretamente no banco de dados.

```bash
curl -X POST "http://localhost:8000/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Novo Usuário",
    "email": "novo@email.com",
    "senha_hash": "hash123",
    "curso": "Ciência da Computação",
    "idade": 20,
    "id_universidade": 1
  }'
```
</details>

<details>
<summary><strong>Como adicionar um novo estabelecimento?</strong></summary>

Use o endpoint `POST /estabelecimentos/` ou adicione diretamente no banco.

```bash
curl -X POST "http://localhost:8000/estabelecimentos/" \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Novo Estabelecimento",
    "endereco": "Rua Exemplo, 123",
    "cidade": "São Paulo",
    "horario_funcionamento": "09:00-18:00",
    "id_categoria": 1
  }'
```
</details>

<details>
<summary><strong>Qual algoritmo usar: LightFM ou Surprise?</strong></summary>

- **Surprise**: Mais simples, funciona com Python 3.12, ideal para CF puro
- **LightFM**: Híbrido (CBF + CF), resolve cold start, requer Python 3.11

Recomendação: Use Surprise para começar rápido, LightFM para recursos avançados.
</details>

<details>
<summary><strong>Como melhorar as recomendações?</strong></summary>

1. **Mais dados**: Adicione mais interações de usuários
2. **Treinar novamente**: Execute treinamento após adicionar dados
3. **Ajustar parâmetros**: Experimente diferentes valores de `n_factors`, `n_epochs`
4. **Usar features**: Configure preferências de usuários e estabelecimentos
</details>

<details>
<summary><strong>O sistema funciona sem histórico de interações?</strong></summary>

Sim! Use o endpoint `/recomendacoes/cold-start/usuario/{id}` que retorna itens populares quando não há histórico.
</details>

---

**🎉 Projeto pronto para uso! Para dúvidas, entre em contato com a equipe.**

---

*README atualizado em: 2025-11-06*
