# 🎯 Sistema de Recomendação Híbrido com LightFM

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

Sistema de recomendação híbrido desenvolvido com **FastAPI** e **LightFM** para recomendar estabelecimentos personalizados para usuários universitários, combinando **Content-Based Filtering (CBF)** e **Collaborative Filtering (CF)**.

---

## 📋 Sumário

- [Descrição do Projeto](#-descrição-do-projeto)
- [Objetivo](#-objetivo)
- [Modelo de Machine Learning](#-modelo-de-machine-learning)
- [Arquitetura](#️-arquitetura)
- [Entidades do Banco de Dados](#-entidades-do-banco-de-dados)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Migrações do Banco de Dados](#-migrações-do-banco-de-dados)
- [Executar a Aplicação](#-executar-a-aplicação)
- [Endpoints da API](#-endpoints-da-api)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Testes](#-testes)
- [Deployment na AWS](#-deployment-na-aws)
- [Desenvolvimento](#-desenvolvimento)
- [Equipe](#-equipe)

---

## 📖 Descrição do Projeto

O sistema utiliza o algoritmo **LightFM** para gerar recomendações inteligentes de estabelecimentos (restaurantes, cafeterias, bibliotecas, etc.) para estudantes universitários, levando em consideração:

- **Preferências do usuário** (comida barata, ambiente silencioso, Wi-Fi rápido, etc.)
- **Características dos estabelecimentos** (categoria, horário, localização, serviços)
- **Comportamento de usuários similares** (padrões de visitas e avaliações)
- **Contexto atual** (hora do dia, localização, disponibilidade)

### 🎯 Objetivo

Desenvolver um sistema de recomendação inicial (versão simples) que possa:

1. **Recomendar estabelecimentos personalizados** para cada usuário
2. **Resolver o problema de cold start** (novos usuários/estabelecimentos)
3. **Descobrir padrões ocultos** através de Collaborative Filtering
4. **Fornecer explicações** sobre as recomendações (via features)
5. **Evitar bolha de filtro** através de diversidade nas recomendações

---

## 🧠 Modelo de Machine Learning

### LightFM - Hybrid Recommendation System

O **LightFM** é um modelo de fatoração de matrizes híbrido que combina o melhor de dois mundos:

#### 1. Content-Based Filtering (CBF)

**O que é?** Analisa as características (features) dos itens e usuários para fazer recomendações baseadas em similaridade.

**Como funciona no projeto:**
- **Features de Usuário**: Preferências declaradas (ex: "Silencioso para Estudo", "Wi-Fi Rápido")
- **Features de Estabelecimento**: Metadados (ex: "Comida Barata", "Café Especial", "Tomadas Acessíveis")
- **Recomendação**: "Você gosta de lugares silenciosos? Recomendamos a Biblioteca Central!"

**Vantagens:**
- ✅ Funciona para usuários/estabelecimentos novos (cold start)
- ✅ Explica por que algo foi recomendado
- ✅ Não precisa de histórico de interações

**Desvantagens:**
- ❌ Pode criar "bolha" (só recomenda o que você já gosta)
- ❌ Requer metadados bem definidos

#### 2. Collaborative Filtering (CF)

**O que é?** Analisa padrões de comportamento entre usuários para descobrir preferências implícitas.

**Como funciona no projeto:**
- **User-User**: "Usuários similares a você visitaram..."
- **Item-Item**: "Quem foi à Biblioteca também foi ao Café X"
- **Matriz de Interações**: Visitas, cliques, avaliações

**Vantagens:**
- ✅ Descobre coisas fora do seu perfil usual
- ✅ Aprende preferências implícitas
- ✅ Não precisa de metadados

**Desvantagens:**
- ❌ Precisa de histórico de interações
- ❌ Cold start problem (novos itens/usuários)

#### 3. Abordagem Híbrida (LightFM)

O LightFM combina ambas as técnicas em um único modelo:

```
Score(user, item) = <user_embedding + Σ(user_features), item_embedding + Σ(item_features)>
```

**Funções de Perda Suportadas:**
- **WARP** (Weighted Approximate-Rank Pairwise): Otimiza para ranking top-N
- **BPR** (Bayesian Personalized Ranking): Para feedback implícito
- **Logistic**: Para classificação binária

**Exemplo Real:**

```
Usuário: Ana Silva (USP, Eng. Computação)
├─ Features: ["Silencioso para Estudo", "Wi-Fi Rápido", "Comida Barata"]
├─ Histórico: Visitou Biblioteca USP (5★), Prato Feito do Zé (3★)
└─ Usuários Similares: Daniel (USP, Eng. Computação)

Recomendação: Grão & Prosa Cafeteria
├─ CBF Score: 0.85 (Wi-Fi Rápido ✓, Ambiente Tranquilo ✓)
├─ CF Score: 0.78 (Daniel visitou e deu 5★)
└─ Score Final: 0.82 (híbrido)
```

---

## 🏗️ Arquitetura

### Stack Tecnológico

| Componente | Tecnologia | Versão | Descrição |
|------------|-----------|--------|-----------|
| **Backend** | FastAPI | 0.104+ | Framework web assíncrono e moderno |
| **Banco de Dados** | PostgreSQL | 12+ | BD relacional (AWS RDS suportado) |
| **ORM** | SQLAlchemy | 2.0+ | Mapeamento objeto-relacional |
| **Validação** | Pydantic | 2.5+ | Validação de dados e schemas |
| **Migrações** | Alembic | 1.13+ | Controle de versão do banco |
| **ML Model** | LightFM | - | Modelo de recomendação híbrido |
| **Server** | Uvicorn | 0.24+ | Servidor ASGI |

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
│   │   ├── universidades.py
│   │   ├── categorias_estabelecimentos.py
│   │   ├── preferencias.py
│   │   ├── usuarios.py
│   │   ├── estabelecimentos.py
│   │   ├── usuario_preferencia.py
│   │   ├── estabelecimento_preferencia.py
│   │   ├── recomendacao_usuario.py
│   │   └── recomendacao_estabelecimento.py
│   │
│   ├── 📁 schemas/                  # ✅ Schemas Pydantic
│   │   └── [correspondentes aos models]
│   │
│   └── main.py                      # 🚀 App FastAPI principal
│
├── 📁 alembic/                      # Migrações do banco
│   ├── versions/
│   │   ├── 3f990a2494f0_create_initial_tables.py
│   │   └── b716a52872a6_seed_initial_data.py
│   └── env.py
│
├── 📁 scripts/                      # Scripts auxiliares
│   └── seed_data.sql                # Dados sintéticos
│
├── 📄 requirements.txt              # Dependências Python
├── 📄 alembic.ini                   # Config do Alembic
├── 📄 .env.example                  # Variáveis de ambiente
├── 📄 run.py                        # Script para rodar o servidor
├── 📄 README.md                     # 📖 Este arquivo
├── 📄 MIGRATION_GUIDE.md            # Guia de migrações
└── 📄 TESTS_CHECKLIST.md            # Checklist de testes

```

---

## 🗄️ Entidades do Banco de Dados

### Diagrama ER Simplificado

```
┌─────────────────┐
│  Universidades  │
└────────┬────────┘
         │
         │ 1:N
         ▼
    ┌─────────┐        N:M        ┌──────────────┐
    │ Usuarios│◄───────────────────┤ Preferencias │
    └────┬────┘                    └──────┬───────┘
         │                                │
         │ 1:N                            │ N:M
         ▼                                ▼
┌──────────────────────┐      ┌─────────────────────┐
│ Recomendacao_Usuario │      │ Estabelecimentos    │
└──────────────────────┘      └──────────┬──────────┘
                                         │
                                         │ 1:N
                                         ▼
                              ┌────────────────────────────┐
                              │ Recomendacao_Estabelecimento│
                              └────────────────────────────┘
```

### 1. **Universidades**
Instituições de ensino cadastradas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_universidade` | Integer (PK) | ID único |
| `nome` | String(255) | Nome da universidade |
| `cidade` | String(100) | Cidade |
| `estado` | String(2) | UF |

**Exemplo:** USP, Unicamp, UFRJ

---

### 2. **Categorias_Estabelecimentos**
Tipos de estabelecimentos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_categoria` | Integer (PK) | ID único |
| `nome_categoria` | String(100) | Nome da categoria |

**Exemplos:** Restaurante, Cafeteria, Biblioteca, Papelaria, Bar e Lazer

---

### 3. **Preferencias**
Features para CBF (metadados de preferências).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_preferencia` | Integer (PK) | ID único |
| `nome_preferencia` | String(100) | Nome da preferência |
| `tipo_preferencia` | String(50) | Categoria (Alimentação, Ambiente, Lazer, etc.) |

**Exemplos:**
- "Comida Barata" (Alimentação)
- "Wi-Fi Rápido" (Infraestrutura)
- "Silencioso para Estudo" (Ambiente)
- "Música ao Vivo" (Lazer)

---

### 4. **Usuarios**
Estudantes que usam o sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_usuario` | Integer (PK) | ID único |
| `nome` | String(255) | Nome completo |
| `email` | String(255) | Email (único) |
| `senha_hash` | String(255) | Senha hasheada |
| `curso` | String(100) | Curso que estuda |
| `idade` | Integer | Idade |
| `descricao` | Text | Descrição do perfil |
| `id_universidade` | Integer (FK) | Universidade |
| `data_cadastro` | Date | Data de cadastro |

---

### 5. **Estabelecimentos**
Locais que podem ser recomendados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_estabelecimento` | Integer (PK) | ID único |
| `descricao` | Text | Descrição do local |
| `endereco` | String(255) | Endereço completo |
| `cidade` | String(100) | Cidade |
| `horario_funcionamento` | String(100) | Ex: "09:00-20:00" |
| `dono_nome` | String(255) | Nome do dono |
| `dono_email` | String(255) | Email do dono |
| `id_categoria` | Integer (FK) | Categoria |

---

### 6. **Usuario_Preferencia** (Tabela de Associação)
User features para LightFM (preferências declaradas).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | ID único |
| `id_usuario` | Integer (FK) | Usuário |
| `id_preferencia` | Integer (FK) | Preferência |
| `peso` | Float (1-5) | Importância para o usuário |

**Uso no CBF:** "Ana prefere lugares com Wi-Fi (peso=5) e silenciosos (peso=4)"

---

### 7. **Estabelecimento_Preferencia** (Tabela de Associação)
Item features para LightFM (características dos estabelecimentos).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | ID único |
| `id_estabelecimento` | Integer (FK) | Estabelecimento |
| `id_preferencia` | Integer (FK) | Preferência |
| `peso` | Float (1-5) | Intensidade da característica |

**Uso no CBF:** "Biblioteca USP tem 'Silencioso para Estudo' (peso=5) e 'Wi-Fi Rápido' (peso=4)"

---

### 8. **Recomendacao_Usuario** (User-User Similarity)
Similaridade entre usuários para CF.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_recomendacao` | Integer (PK) | ID único |
| `id_usuario1` | Integer (FK) | Usuário origem |
| `id_usuario2` | Integer (FK) | Usuário similar |
| `score` | Float (0-1) | Similaridade |
| `data_recomendacao` | Date | Data do cálculo |

**Uso:** "Ana (101) é 90% similar a Daniel (104)" → recomendar o que Daniel gosta

---

### 9. **Recomendacao_Estabelecimento** (User-Item Interactions)
Matriz de interações implícitas para treinar o LightFM.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_recomendacao` | Integer (PK) | ID único |
| `id_usuario` | Integer (FK) | Usuário |
| `id_lugar` | Integer (FK) | Estabelecimento |
| `score` | Integer (1-5) | Avaliação/peso da interação |
| `data_recomendacao` | Date | Data da interação |

**Uso no CF:** Matriz usuário×item para Collaborative Filtering

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.8 ou superior**
- **PostgreSQL 12 ou superior** (local ou AWS RDS)
- **Git**
- **pip** (gerenciador de pacotes Python)

### 1. Clonar o Repositório

```bash
git clone https://github.com/JONTK123/Projeto-Integrador-6.git
cd Projeto-Integrador-6
```

### 2. Criar Ambiente Virtual

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências instaladas:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- sqlalchemy==2.0.23
- pydantic[email]==2.5.0
- python-dotenv==1.0.0
- psycopg2-binary==2.9.9
- alembic==1.13.0

---

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/lightfm_recommendations

# Para AWS RDS:
# DATABASE_URL=postgresql://admin:senha@seu-endpoint.rds.amazonaws.com:5432/lightfm_recommendations

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# LightFM Model Configuration
LIGHTFM_NUM_THREADS=4
LIGHTFM_LOSS=warp
LIGHTFM_LEARNING_RATE=0.05
LIGHTFM_NUM_EPOCHS=30
LIGHTFM_NUM_COMPONENTS=30
```

### 2. Criar Banco de Dados

**Conecte ao PostgreSQL:**
```bash
psql -U postgres
```

**Crie o banco:**
```sql
CREATE DATABASE lightfm_recommendations;
\q
```

---

## 📦 Migrações do Banco de Dados

O projeto usa **Alembic** para gerenciar migrações do banco de dados.

### Ver Status das Migrações

```bash
alembic current
```

### Executar Todas as Migrações

```bash
alembic upgrade head
```

Este comando irá:
1. ✅ Criar todas as 9 tabelas com relacionamentos
2. ✅ Popular com dados sintéticos (15 usuários, 18 estabelecimentos, etc.)

### Verificar Dados Populados

```bash
psql -d lightfm_recommendations -c "SELECT COUNT(*) FROM usuarios;"
psql -d lightfm_recommendations -c "SELECT COUNT(*) FROM estabelecimentos;"
```

### Reverter Migrações

```bash
# Reverter última migração
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

📖 **Para mais detalhes:** Leia o [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

---

## 🏃 Executar a Aplicação

### Método 1: Usando Uvicorn Diretamente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Método 2: Usando o Script Python

```bash
python run.py
```

### Método 3: Modo Produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Acessar a Aplicação

- **API Base:** http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs
- **Documentação ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

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

---

### 👤 Usuários (CRUD)

#### Criar Usuário
```http
POST /usuarios/
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha_hash": "hash_senha",
  "curso": "Ciência da Computação",
  "idade": 20,
  "id_universidade": 1
}
```

#### Listar Usuários
```http
GET /usuarios/?skip=0&limit=100
```

#### Obter Usuário
```http
GET /usuarios/101
```

#### Atualizar Usuário
```http
PUT /usuarios/101
Content-Type: application/json

{
  "curso": "Engenharia de Software"
}
```

#### Deletar Usuário
```http
DELETE /usuarios/101
```

---

### 🏪 Estabelecimentos (CRUD)

Endpoints similares aos de usuários:

```http
POST   /estabelecimentos/
GET    /estabelecimentos/
GET    /estabelecimentos/{id}
PUT    /estabelecimentos/{id}
DELETE /estabelecimentos/{id}
```

---

### 🎯 Sistema de Recomendação

#### 1. Recomendações Personalizadas

```http
GET /recomendacoes/usuario/101?top_n=10&tipo=hybrid
```

**Parâmetros:**
- `top_n`: Número de recomendações (padrão: 10)
- `tipo`: Tipo de filtragem
  - `hybrid`: CBF + CF (padrão)
  - `cbf`: Content-Based apenas
  - `cf`: Collaborative apenas

**Resposta:**
```json
{
  "usuario_id": 101,
  "tipo": "hybrid",
  "recomendacoes": [
    {
      "estabelecimento_id": 203,
      "score": 0.92,
      "razao": "Silencioso, Wi-Fi rápido, livros técnicos"
    },
    {
      "estabelecimento_id": 202,
      "score": 0.85,
      "razao": "Café especial, ambiente tranquilo"
    }
  ]
}
```

#### 2. Estabelecimentos Similares (Item-Item)

```http
GET /recomendacoes/estabelecimento/203/similares?top_n=5
```

**Uso:** "Quem visitou a Biblioteca USP também visitou..."

#### 3. Registrar Interação (Feedback Implícito)

```http
POST /recomendacoes/interacao
Content-Type: application/json

{
  "usuario_id": 101,
  "estabelecimento_id": 203,
  "tipo_interacao": "visita",
  "peso": 1.0
}
```

**Tipos de Interação:**
- `visita`: Usuário visitou o local
- `clique`: Clicou na recomendação
- `favorito`: Favoritou o local

#### 4. Treinar Modelo LightFM

```http
POST /recomendacoes/treinar
Content-Type: application/json

{
  "usar_features": true,
  "loss": "warp"
}
```

**Parâmetros:**
- `usar_features`: Usar metadados (CBF)
- `loss`: Função de perda
  - `warp`: WARP (recomendado para ranking)
  - `bpr`: Bayesian Personalized Ranking
  - `logistic`: Regressão logística

#### 5. Cold Start - Novo Usuário

```http
GET /recomendacoes/cold-start/usuario/115?top_n=5
```

Usa apenas CBF baseado nas preferências declaradas.

#### 6. Recomendações com Diversidade

```http
GET /recomendacoes/diversidade/usuario/101?top_n=10&explorar=0.1
```

Usa MMR (Maximal Marginal Relevance) para evitar bolha de filtro.

#### 7. Recomendações Contextuais

```http
GET /recomendacoes/contexto/usuario/101?hora_atual=14&latitude=-23.5505&longitude=-46.6333
```

Considera:
- Hora do dia (horários de funcionamento)
- Localização (distância)
- Dia da semana
- Horários de pico

---

## 💡 Exemplos de Uso

### Exemplo 1: Fluxo Completo de Recomendação

```bash
# 1. Criar novo usuário
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "senha_hash": "hash123",
    "curso": "Design",
    "idade": 19,
    "id_universidade": 2
  }'

# 2. Adicionar preferências do usuário (via banco ou endpoint)

# 3. Obter recomendações
curl http://localhost:8000/recomendacoes/usuario/101?top_n=5&tipo=hybrid

# 4. Registrar visita
curl -X POST http://localhost:8000/recomendacoes/interacao \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 101,
    "estabelecimento_id": 203,
    "tipo_interacao": "visita",
    "peso": 1.0
  }'

# 5. Treinar modelo com novos dados
curl -X POST http://localhost:8000/recomendacoes/treinar \
  -H "Content-Type: application/json" \
  -d '{
    "usar_features": true,
    "loss": "warp"
  }'
```

### Exemplo 2: Consultar Dados via SQL

```sql
-- Ver usuários e suas preferências
SELECT 
    u.nome,
    p.nome_preferencia,
    up.peso
FROM usuarios u
JOIN usuario_preferencia up ON u.id_usuario = up.id_usuario
JOIN preferencias p ON up.id_preferencia = p.id_preferencia
WHERE u.id_usuario = 101;

-- Ver estabelecimentos e suas features
SELECT 
    e.descricao,
    p.nome_preferencia,
    ep.peso
FROM estabelecimentos e
JOIN estabelecimento_preferencia ep ON e.id_estabelecimento = ep.id_estabelecimento
JOIN preferencias p ON ep.id_preferencia = p.id_preferencia
WHERE e.id_estabelecimento = 203;

-- Ver matriz de interações
SELECT 
    u.nome,
    e.descricao,
    re.score,
    re.data_recomendacao
FROM recomendacao_estabelecimento re
JOIN usuarios u ON re.id_usuario = u.id_usuario
JOIN estabelecimentos e ON re.id_lugar = e.id_estabelecimento
ORDER BY re.score DESC;
```

---

## 🧪 Testes

### Verificar que a API está funcionando

```bash
# Health check
curl http://localhost:8000/

# Documentação
curl http://localhost:8000/openapi.json
```

### Executar Checklist de Testes

```bash
# Ver checklist completo
cat TESTS_CHECKLIST.md
```

📖 **Detalhes:** Veja [TESTS_CHECKLIST.md](TESTS_CHECKLIST.md) para lista completa de testes.

---

## ☁️ Deployment na AWS

### Configurar PostgreSQL no AWS RDS

1. **Criar instância RDS PostgreSQL**
   - Engine: PostgreSQL 14+
   - Classe: db.t3.micro (para testes)
   - Armazenamento: 20 GB
   - Habilitar acesso público (para desenvolvimento)

2. **Configurar Security Group**
   - Adicionar regra de entrada: PostgreSQL (5432) da sua IP

3. **Obter endpoint de conexão**
   ```
   Exemplo: lightfm-db.c9akciq32.us-east-1.rds.amazonaws.com
   ```

4. **Atualizar `.env`**
   ```env
   DATABASE_URL=postgresql://admin:SuaSenha@lightfm-db.c9akciq32.us-east-1.rds.amazonaws.com:5432/lightfm_recommendations
   ```

5. **Executar migrações**
   ```bash
   alembic upgrade head
   ```

### Deploy da API na AWS EC2/ECS

**Opção 1: EC2**
```bash
# Instalar Python e dependências
sudo apt update
sudo apt install python3-pip python3-venv postgresql-client

# Clonar projeto e configurar
git clone https://github.com/JONTK123/Projeto-Integrador-6.git
cd Projeto-Integrador-6
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar .env com RDS endpoint

# Executar migrações
alembic upgrade head

# Rodar com Uvicorn (use supervisor ou systemd para produção)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Opção 2: Docker + ECS** (recomendado)
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🛠️ Desenvolvimento

### Estrutura de Commits

```bash
# Formato recomendado
tipo(escopo): descrição curta

# Exemplos:
feat(api): Add endpoint for contextual recommendations
fix(models): Fix foreign key relationship in Usuario model
docs(readme): Update installation instructions
refactor(lightfm): Improve feature engineering pipeline
```

### Adicionar Novas Features

```bash
# 1. Criar branch
git checkout -b feature/nova-funcionalidade

# 2. Fazer alterações

# 3. Criar migração (se necessário)
alembic revision -m "Add new column to table"

# 4. Testar
python -m pytest

# 5. Commit e push
git add .
git commit -m "feat: Add nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### Comandos Úteis

```bash
# Verificar sintaxe Python
python -m py_compile app/main.py

# Formatar código
pip install black
black app/

# Linting
pip install flake8
flake8 app/

# Type checking
pip install mypy
mypy app/

# Ver logs do Uvicorn
uvicorn app.main:app --log-level debug
```

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

### Sobre a ALGORITHMA 3 AI

Empresa especializada em desenvolvimento de software custom, consultoria em TI e soluções de inteligência artificial. Aplicamos ciência de dados e IA para transformar informação em decisões inteligentes.

---

## 📄 Licença

Este projeto está em desenvolvimento como parte de um projeto R&D de sistema de recomendação.

**© 2024 ALGORITHMA 3 AI. Todos os direitos reservados.**

---

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LightFM Documentation](https://making.lyst.com/lightfm/docs/home.html)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL AWS RDS](https://aws.amazon.com/rds/postgresql/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## ❓ FAQ

<details>
<summary><strong>Como adicionar um novo tipo de estabelecimento?</strong></summary>

```sql
INSERT INTO categorias_estabelecimentos (nome_categoria) 
VALUES ('Nova Categoria');
```
</details>

<details>
<summary><strong>Como adicionar uma nova preferência?</strong></summary>

```sql
INSERT INTO preferencias (nome_preferencia, tipo_preferencia) 
VALUES ('Nova Preferencia', 'Tipo');
```
</details>

<details>
<summary><strong>O banco pode estar em outro serviço além da AWS?</strong></summary>

Sim! O sistema funciona com qualquer PostgreSQL. Basta configurar o `DATABASE_URL` no `.env`.
</details>

<details>
<summary><strong>Como resetar o banco de dados?</strong></summary>

```bash
alembic downgrade base
alembic upgrade head
```
</details>

---

## 🚨 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

**Solução:** Execute do diretório raiz do projeto:
```bash
cd /caminho/para/Projeto-Integrador-6
uvicorn app.main:app --reload
```

### Erro: "connection refused" ao PostgreSQL

**Solução:** Verifique se o PostgreSQL está rodando:
```bash
sudo systemctl status postgresql  # Linux
brew services list  # Mac
```

### Erro: "Target database is not up to date"

**Solução:** Execute as migrações:
```bash
alembic upgrade head
```

---

**🎉 Projeto pronto para uso! Para dúvidas, entre em contato com a equipe.**

---

*README gerado com ❤️ pelo time ALGORITHMA 3 AI*
