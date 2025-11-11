# Estrutura do Projeto

```
Projeto-Integrador-6/                # Raiz do projeto
│
├── 📁 backend/                      # Código do backend
│   ├── app/                         # Aplicação FastAPI
│   ├── models/                      # Modelos ML treinados
│   ├── scripts/                     # Scripts auxiliares
│   └── test_models/                 # Testes de modelos
│
├── 📁 frontend/                     # Interface React
│   ├── src/                         # Código fonte
│   └── public/                      # Assets públicos
│
├── 📁 alembic/                      # Migrations do banco
│   └── versions/                    # Histórico de migrations
│
├── 📄 alembic.ini                   # Configuração Alembic
├── 📄 requirements.txt              # Dependências Python
├── 📄 iniciar_servidor.sh           # Script para iniciar (Linux/Mac)
├── 📄 iniciar_servidor.bat          # Script para iniciar (Windows)
├── 📄 .env.example                  # Exemplo de configuração
├── 📄 .gitignore                    # Arquivos ignorados pelo Git
└── 📄 README.md                     # Documentação principal
```

## Como Usar

### Iniciar Backend
```bash
# Na raiz do projeto
./iniciar_servidor.sh
```

### Iniciar Frontend
```bash
cd frontend
npm run dev
```

## Observações

- Os arquivos de configuração (alembic.ini, requirements.txt, .env) ficam na raiz
- O código Python (backend) fica em `backend/`
- O código React (frontend) fica em `frontend/`
- Scripts de inicialização ficam na raiz para facilitar o uso
