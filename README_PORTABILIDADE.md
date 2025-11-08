# 🌍 Guia de Portabilidade - Linux, Windows e macOS

Este projeto foi desenvolvido para funcionar em **Linux, Windows e macOS**. Este guia explica como configurar e executar em cada sistema operacional.

## 📋 Pré-requisitos

### Todos os Sistemas
- Python 3.11 ou superior
- PostgreSQL (ou banco de dados configurado)
- Git

### Para LightFM (Opcional)
- Conda ou Miniconda instalado
- Ambiente Conda `lightfm_py311` criado

## 🚀 Iniciando o Servidor

### Linux / macOS
```bash
# Dar permissão de execução (primeira vez)
chmod +x iniciar_servidor.sh

# Executar
./iniciar_servidor.sh
```

### Windows
```cmd
# Executar
iniciar_servidor.bat
```

### Manual (Todos os Sistemas)
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env (veja abaixo)

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ⚙️ Configuração do Conda (LightFM)

### Opção 1: Detecção Automática (Recomendado)
O código detecta automaticamente o Conda em todos os sistemas. Funciona se:
- Conda está no PATH do sistema
- Ambiente `lightfm_py311` existe

### Opção 2: Variável de Ambiente (Para Grupos)
Configure a variável de ambiente `CONDA_PYTHON_PATH`:

#### Linux/macOS:
```bash
# Adicionar ao ~/.bashrc ou ~/.zshrc
export CONDA_PYTHON_PATH="/caminho/para/conda/envs/lightfm_py311/bin/python3.11"
```

#### Windows:
```cmd
# Via PowerShell (temporário)
$env:CONDA_PYTHON_PATH="C:\caminho\para\conda\envs\lightfm_py311\python.exe"

# Via Variáveis de Ambiente do Sistema (permanente)
# Painel de Controle > Sistema > Variáveis de Ambiente
```

### Criar Ambiente Conda
```bash
# Todos os sistemas (se conda está no PATH)
conda create -n lightfm_py311 python=3.11 -y
conda activate lightfm_py311
conda install -c conda-forge lightfm numpy scipy scikit-learn -y
pip install fastapi sqlalchemy pydantic python-dotenv psycopg2-binary pandas joblib
```

## 📁 Estrutura de Caminhos

O código usa `pathlib.Path` que é **cross-platform** e funciona automaticamente em todos os sistemas:

- **Linux/macOS**: `/caminho/para/arquivo`
- **Windows**: `C:\caminho\para\arquivo`

O código detecta automaticamente o sistema operacional e ajusta os caminhos.

## 🔧 Configuração do Banco de Dados (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
# Exemplo Linux/macOS
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_banco

# Exemplo Windows
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_banco
```

**Nota**: A URL do PostgreSQL é a mesma em todos os sistemas.

## 🐛 Solução de Problemas

### Conda não encontrado
1. Verifique se Conda está no PATH:
   ```bash
   # Linux/macOS
   which conda
   
   # Windows
   where conda
   ```

2. Se não estiver, adicione ao PATH ou use variável de ambiente `CONDA_PYTHON_PATH`

### LightFM não funciona
- O sistema funciona **sem LightFM** usando apenas Surprise
- Para usar LightFM, instale Conda e crie o ambiente `lightfm_py311`
- Se não conseguir instalar LightFM, use `algoritmo=surprise` nas rotas

### Problemas de Permissão (Linux)
Se o servidor rodar como root, pode ter problemas com Conda. Soluções:
1. Use `conda run` (já implementado)
2. Configure variável de ambiente `CONDA_PYTHON_PATH`
3. Execute o servidor como usuário normal

### Scripts não executam (Linux/macOS)
```bash
chmod +x iniciar_servidor.sh
```

### Scripts não executam (Windows)
- Windows executa `.bat` automaticamente
- Se não funcionar, execute via CMD ou PowerShell

## 📝 Desenvolvimento em Grupo

### Recomendações
1. **Use variável de ambiente** `CONDA_PYTHON_PATH` se cada membro tem Conda em locais diferentes
2. **Commit apenas código**, não ambientes virtuais (`venv/` no `.gitignore`)
3. **Documente caminhos específicos** no README do grupo
4. **Use Docker** (opcional) para garantir ambiente idêntico

### Gitignore
Certifique-se de que `.gitignore` contém:
```
venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
```

## ✅ Checklist de Portabilidade

- [x] Caminhos relativos usando `pathlib.Path`
- [x] Detecção automática do sistema operacional
- [x] Scripts para Linux/macOS (`.sh`) e Windows (`.bat`)
- [x] Detecção cross-platform do Conda
- [x] Suporte a variável de ambiente `CONDA_PYTHON_PATH`
- [x] Fallback para Surprise se LightFM não disponível
- [x] Documentação clara para cada sistema

## 🆘 Ajuda

Se encontrar problemas específicos de portabilidade:
1. Verifique os logs do servidor
2. Teste com `algoritmo=surprise` (não precisa de Conda)
3. Configure `CONDA_PYTHON_PATH` manualmente
4. Verifique se todas as dependências estão instaladas

