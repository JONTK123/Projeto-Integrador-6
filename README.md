# Sistema de Recomendação LightFM

Sistema de recomendação híbrido desenvolvido com FastAPI e LightFM para recomendar estabelecimentos personalizados para usuários universitários.

## 📋 Descrição

O sistema utiliza o algoritmo **LightFM** para gerar recomendações inteligentes, combinando:

- **Content-Based Filtering (CBF)**: Analisa as características dos estabelecimentos (categoria, Wi-Fi, ruído, preço, horário, localização) e as preferências do usuário
- **Collaborative Filtering (CF)**: Identifica padrões de comportamento entre diferentes usuários para descobrir estabelecimentos fora do perfil usual

## 🏗️ Arquitetura

### Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido para construção de APIs
- **PostgreSQL**: Banco de dados relacional para armazenamento de dados
- **SQLAlchemy**: ORM para interação com o banco de dados
- **Pydantic**: Validação de dados e schemas
- **LightFM**: Modelo de recomendação híbrido (a ser integrado)

### Estrutura do Projeto

```
Projeto-Integrador-6/
├── app/
│   ├── api/                    # Endpoints da API
│   │   ├── usuarios.py         # CRUD de usuários
│   │   ├── estabelecimentos.py # CRUD de estabelecimentos
│   │   ├── preferencias.py     # CRUD de preferências
│   │   └── recomendacoes.py    # Endpoints de recomendação
│   ├── core/                   # Configurações centrais
│   │   └── database.py         # Configuração do PostgreSQL
│   ├── models/                 # Modelos ORM (SQLAlchemy)
│   │   ├── categorias_estabelecimentos.py
│   │   ├── preferencias.py
│   │   ├── usuarios.py
│   │   ├── estabelecimentos.py
│   │   ├── usuario_preferencia.py
│   │   ├── estabelecimento_preferencia.py
│   │   ├── recomendacao_usuario.py
│   │   └── recomendacao_estabelecimento.py
│   ├── schemas/                # Schemas Pydantic
│   │   └── ...                 # Schemas para validação
│   └── main.py                 # Aplicação FastAPI principal
├── requirements.txt            # Dependências Python
├── .env.example               # Exemplo de configuração
└── README.md                  # Este arquivo
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- pip

### Passos de Instalação

1. Clone o repositório:
```bash
git clone https://github.com/JONTK123/Projeto-Integrador-6.git
cd Projeto-Integrador-6
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Configure o banco de dados PostgreSQL:
```sql
CREATE DATABASE lightfm_recommendations;
```

6. Execute a aplicação:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. Acesse a documentação interativa:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 Endpoints Principais

### Gerenciamento de Dados

- `POST /usuarios/` - Criar usuário
- `GET /usuarios/` - Listar usuários
- `GET /usuarios/{id}` - Obter usuário
- `PUT /usuarios/{id}` - Atualizar usuário
- `DELETE /usuarios/{id}` - Deletar usuário

- `POST /estabelecimentos/` - Criar estabelecimento
- `GET /estabelecimentos/` - Listar estabelecimentos
- Endpoints similares para preferências

### Sistema de Recomendação

- `GET /recomendacoes/usuario/{usuario_id}` - Obter recomendações personalizadas
  - Parâmetros: `top_n`, `tipo` (hybrid/cbf/cf)
  
- `GET /recomendacoes/estabelecimento/{id}/similares` - Estabelecimentos similares
  
- `POST /recomendacoes/interacao` - Registrar interação usuário-estabelecimento
  - Essencial para treinar o modelo com feedback implícito
  
- `POST /recomendacoes/treinar` - Retreinar modelo LightFM
  - Parâmetros: `usar_features`, `loss` (warp/bpr/logistic)

### Recursos Avançados

- `GET /recomendacoes/cold-start/usuario/{id}` - Recomendações para usuários novos
- `GET /recomendacoes/diversidade/usuario/{id}` - Recomendações diversificadas (evita bolha)
- `GET /recomendacoes/contexto/usuario/{id}` - Recomendações contextuais
  - Considera: hora, localização, distância, horários de funcionamento

## 🧠 Modelo LightFM

### Estratégias de Recomendação

#### Content-Based Filtering (CBF)
- Analisa características dos estabelecimentos: categoria, Wi-Fi, ruído, preço, horário, localização
- Útil para cold start de estabelecimentos novos
- "Você também pode gostar de..."

#### Collaborative Filtering (CF)
- Padrões de uso entre usuários (user-user)
- Co-visitação de estabelecimentos (item-item)
- "Pessoas como você gostaram de..."

#### Híbrido (Padrão)
- Combina CBF e CF no mesmo modelo
- Aprende embeddings de usuários, itens e features
- Melhor performance geral

### Metadados Suportados

Os estabelecimentos podem ter os seguintes metadados para melhor recomendação:

- **Localização**: latitude, longitude, bairro, distância ao campus
- **Estrutura**: tomadas, mesas, área externa, acessibilidade
- **Ambiente**: nível de ruído, lotação, capacidade
- **Serviços**: refeições, cafeteria, micro-ondas
- **Dietas**: vegano, vegetariano, sem glúten
- **Pagamento**: PIX, débito, crédito, vale-refeição
- **Conectividade**: velocidade Wi-Fi, estabilidade
- **Horários**: dias abertos, horários de pico

## 🔄 Fluxo de Uso

1. **Cadastro de Dados**
   - Cadastrar usuários e suas preferências
   - Cadastrar estabelecimentos com metadados completos
   - Cadastrar categorias e preferências

2. **Coleta de Interações**
   - Registrar visitas, cliques e favoritos
   - Feedback implícito para treinar o modelo

3. **Treinamento do Modelo**
   - Executar endpoint `/recomendacoes/treinar`
   - Modelo aprende padrões de CBF e CF

4. **Geração de Recomendações**
   - Usuários recebem recomendações personalizadas
   - Sistema considera contexto (hora, localização)

## 📊 Próximos Passos

- [ ] Implementar lógica de CRUD completa para todas as entidades
- [ ] Integrar modelo LightFM real
- [ ] Criar sistema de features para CBF
- [ ] Implementar matriz de interações para CF
- [ ] Adicionar sistema de métricas (NDCG, Recall@K)
- [ ] Implementar estratégias de cold start
- [ ] Adicionar sistema de diversidade (MMR)
- [ ] Criar dashboard de monitoramento

## 👥 Desenvolvido por

**ALGORITHMA 3 AI**  
Douglas Henrique Siqueira Abreu Tecnologia da Informação LTDA  
CNPJ: 56.420.666/0001-53

- Email: douglas.abreu@algorithma.com.br
- LinkedIn: [douglashsabreu](https://linkedin.com/in/douglashsabreu/)
- Telefone: +55 (19) 99212-5712

## 📄 Licença

Este projeto está em desenvolvimento como parte de um projeto R&D de sistema de recomendação.
