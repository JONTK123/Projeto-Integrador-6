# Guia de Migrações do Banco de Dados

Este guia explica como configurar e executar as migrações do banco de dados PostgreSQL para o Sistema de Recomendação LightFM.

## 📋 Pré-requisitos

- PostgreSQL instalado e rodando (local ou AWS RDS)
- Python 3.8+ com as dependências instaladas (`pip install -r requirements.txt`)

## 🔧 Configuração

### 1. Configurar a conexão com o banco de dados

Crie um arquivo `.env` na raiz do projeto (copie do `.env.example`):

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure a URL do banco de dados:

#### Para PostgreSQL Local:
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/lightfm_recommendations
```

#### Para PostgreSQL na AWS RDS:
```env
DATABASE_URL=postgresql://usuario:senha@seu-endpoint.rds.amazonaws.com:5432/lightfm_recommendations
```

**Exemplo AWS RDS:**
```env
DATABASE_URL=postgresql://admin:SuaSenha123@lightfm-db.c9akciq32.us-east-1.rds.amazonaws.com:5432/lightfm_recommendations
```

### 2. Criar o banco de dados

Se o banco ainda não existe, conecte ao PostgreSQL e crie:

```sql
CREATE DATABASE lightfm_recommendations;
```

## 🚀 Executar Migrações

### Ver status das migrações
```bash
alembic current
```

### Executar todas as migrações (upgrade head)
```bash
alembic upgrade head
```

Este comando irá:
1. **Criar todas as tabelas** (migração: 3f990a2494f0)
   - universidades
   - categorias_estabelecimentos
   - preferencias
   - usuarios
   - estabelecimentos
   - usuario_preferencia
   - estabelecimento_preferencia
   - recomendacao_usuario
   - recomendacao_estabelecimento

2. **Popular com dados sintéticos** (migração: b716a52872a6)
   - 9 universidades
   - 10 categorias de estabelecimentos
   - 21 preferências
   - 15 usuários
   - 18 estabelecimentos
   - 35 relações usuário-preferência
   - 39 relações estabelecimento-preferência
   - 8 recomendações entre usuários
   - 20 avaliações de estabelecimentos

### Ver histórico de migrações
```bash
alembic history
```

### Executar uma migração específica
```bash
alembic upgrade <revision_id>
```

Exemplo:
```bash
alembic upgrade 3f990a2494f0  # Apenas cria tabelas
alembic upgrade b716a52872a6  # Cria tabelas e popula dados
```

## ⬇️ Reverter Migrações (Downgrade)

### Reverter para a migração anterior
```bash
alembic downgrade -1
```

### Reverter todas as migrações
```bash
alembic downgrade base
```

### Reverter para uma migração específica
```bash
alembic downgrade <revision_id>
```

## 📝 Ordem das Migrações

1. **3f990a2494f0_create_initial_tables.py**
   - Cria todas as 9 tabelas do sistema
   - Define chaves primárias, estrangeiras e índices
   - Estabelece as relações entre tabelas

2. **b716a52872a6_seed_initial_data.py**
   - Popula as tabelas com dados sintéticos
   - Respeita a ordem de dependências (FK)
   - Dados prontos para treinar modelo LightFM

## 🔍 Verificar Dados Populados

Depois de executar as migrações, você pode verificar os dados:

```sql
-- Verificar quantidade de registros
SELECT 'universidades' as tabela, COUNT(*) as total FROM universidades
UNION ALL
SELECT 'usuarios', COUNT(*) FROM usuarios
UNION ALL
SELECT 'estabelecimentos', COUNT(*) FROM estabelecimentos
UNION ALL
SELECT 'preferencias', COUNT(*) FROM preferencias
UNION ALL
SELECT 'usuario_preferencia', COUNT(*) FROM usuario_preferencia
UNION ALL
SELECT 'estabelecimento_preferencia', COUNT(*) FROM estabelecimento_preferencia
UNION ALL
SELECT 'recomendacao_usuario', COUNT(*) FROM recomendacao_usuario
UNION ALL
SELECT 'recomendacao_estabelecimento', COUNT(*) FROM recomendacao_estabelecimento;
```

## 🛠️ Criar Novas Migrações

### Criar migração vazia
```bash
alembic revision -m "Descrição da migração"
```

### Criar migração com auto-detect (requer conexão com DB)
```bash
alembic revision --autogenerate -m "Descrição da migração"
```

## ⚠️ Troubleshooting

### Erro de conexão com PostgreSQL
```
sqlalchemy.exc.OperationalError: connection refused
```
**Solução:** Verifique se o PostgreSQL está rodando e se a URL no `.env` está correta.

### Erro de permissões
```
psycopg2.errors.InsufficientPrivilege
```
**Solução:** Verifique se o usuário do banco tem permissões para criar tabelas.

### Migração já executada
```
alembic.util.exc.CommandError: Target database is not up to date
```
**Solução:** Use `alembic current` para ver o status e `alembic upgrade head` para atualizar.

## 📊 Estrutura de Dados para LightFM

Os dados sintéticos foram projetados para o treinamento do modelo LightFM:

- **Content-Based Filtering (CBF):** 
  - Features de estabelecimentos: `estabelecimento_preferencia`
  - Features de usuários: `usuario_preferencia`

- **Collaborative Filtering (CF):**
  - Matriz de interações implícitas: `recomendacao_estabelecimento`
  - Similaridade entre usuários: `recomendacao_usuario`

- **Cold Start:**
  - Novos usuários: use `usuario_preferencia` para recomendações iniciais
  - Novos estabelecimentos: use `estabelecimento_preferencia` para CBF

## 🔄 Workflow Recomendado

1. Configure o `.env` com credenciais do PostgreSQL (AWS RDS)
2. Execute `alembic upgrade head` para criar tabelas e popular dados
3. Inicie a aplicação FastAPI: `uvicorn app.main:app --reload`
4. Acesse a documentação: http://localhost:8000/docs
5. Teste os endpoints de recomendação
6. Treine o modelo LightFM com os dados sintéticos
7. Ajuste as migrações conforme necessário

## 📚 Recursos Adicionais

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [PostgreSQL on AWS RDS](https://aws.amazon.com/rds/postgresql/)
- [LightFM Documentation](https://making.lyst.com/lightfm/docs/home.html)
