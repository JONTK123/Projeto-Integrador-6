# Frontend - Sistema de Recomendação

Interface moderna em React para o Sistema de Recomendação usando LightFM e Surprise.

## Tecnologias

- **React 18** - Biblioteca UI
- **Vite** - Build tool ultra-rápido
- **React Router v7** - Roteamento
- **TailwindCSS** - Estilização utilitária
- **Axios** - Cliente HTTP
- **TanStack Query** - Gerenciamento de estado do servidor
- **Lucide React** - Ícones modernos

## Instalação

```bash
# Instalar dependências
cd frontend
npm install

# Configurar variáveis de ambiente
cp .env .env.local
# Editar .env.local se necessário (padrão: http://localhost:8000)

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizáveis
│   │   └── Layout.jsx     # Layout principal com navegação
│   ├── pages/             # Páginas da aplicação
│   │   ├── Home.jsx       # Dashboard principal
│   │   ├── Usuarios.jsx   # CRUD de usuários
│   │   ├── Estabelecimentos.jsx
│   │   ├── Preferencias.jsx
│   │   ├── Recomendacoes.jsx  # Interface de recomendações
│   │   └── Treinamento.jsx    # Treinar modelos
│   ├── services/          # Serviços e API
│   │   └── api.js         # Cliente API com todos os endpoints
│   ├── lib/               # Utilitários
│   │   └── cn.js          # Função para classes Tailwind
│   ├── App.jsx            # Componente raiz
│   └── main.jsx           # Entry point
├── .env                   # Variáveis de ambiente
└── package.json
```

## Funcionalidades

### 1. Dashboard (Home)
- Status do sistema em tempo real
- Estatísticas de usuários, estabelecimentos e preferências
- Health check da API e modelos

### 2. Usuários
- Listar, criar, editar e deletar usuários
- Busca por nome/email
- Associação com universidades

### 3. Estabelecimentos
- CRUD completo com cards visuais
- Filtro por nome/cidade
- Categorização

### 4. Preferências
- Gerenciamento de preferências
- Tipos e categorias

### 5. Recomendações
- Gerar recomendações para qualquer usuário
- Escolher algoritmo (LightFM ou Surprise)
- Comparar resultados de ambos algoritmos lado a lado
- Visualização com scores

### 6. Treinamento
- Treinar modelos LightFM e Surprise
- Feedback visual de sucesso/erro
- Exibição de métricas

## Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Linting
npm run lint
```

## Comunicação com Backend

O frontend se comunica com o backend via REST API. Todos os endpoints estão configurados em `src/services/api.js`.

**Backend deve estar rodando em:** `http://localhost:8000`

Para alterar a URL da API, edite o arquivo `.env`:

```env
VITE_API_BASE_URL=http://seu-servidor:porta
```

## Desenvolvimento

### Adicionar Nova Página

1. Criar arquivo em `src/pages/NomeDaPagina.jsx`
2. Adicionar rota em `src/App.jsx`
3. Adicionar link de navegação em `src/components/Layout.jsx`

### Adicionar Novo Endpoint da API

Edite `src/services/api.js` e adicione a função:

```javascript
export const getNovoDado = (params) => api.get('/endpoint/', { params });
export const createNovoDado = (data) => api.post('/endpoint/', data);
```

## Estilização

O projeto usa **TailwindCSS** para estilização. Classes utilitárias são aplicadas diretamente nos componentes.

Cores principais:
- Blue: Usuários, primário
- Green: Estabelecimentos
- Red/Pink: Preferências
- Purple: Recomendações
- Yellow: LightFM

## Problemas Comuns

### CORS Error
Se encontrar erro de CORS, certifique-se que o backend está configurado para aceitar requisições do frontend:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API não responde
Verifique se o backend está rodando:
```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## Próximos Passos

- [ ] Adicionar autenticação JWT
- [ ] Implementar paginação real
- [ ] Adicionar gráficos com Chart.js
- [ ] Modo escuro
- [ ] Testes com Vitest
- [ ] PWA support

## Licença

Projeto acadêmico - Projeto Integrador 6

