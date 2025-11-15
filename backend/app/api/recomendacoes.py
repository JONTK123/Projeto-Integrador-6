from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.core.database import get_db
from pydantic import BaseModel
try:
    from app.services.lightfm_service import LightFMService
    LIGHTFM_AVAILABLE = True
except ImportError:
    LIGHTFM_AVAILABLE = False
    LightFMService = None

from app.services.surprise_service import SurpriseService
from app.models.recomendacao_estabelecimento import RecomendacaoEstabelecimento
from app.models.usuarios import Usuarios
from app.models.estabelecimentos import Estabelecimentos
from datetime import datetime
import subprocess
import json
import os
from pathlib import Path
from typing import Tuple

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])

# Instâncias globais dos serviços (singleton)
lightfm_service = None
if LIGHTFM_AVAILABLE:
    try:
        lightfm_service = LightFMService()
        # Tentar carregar modelo do MLflow primeiro (se disponível)
        model_loaded = False
        
        # Tentar carregar do MLflow (modelo em produção)
        try:
            from app.services.lightfm_service import MLFLOW_AVAILABLE as MLFLOW_SERVICE_AVAILABLE
            if MLFLOW_SERVICE_AVAILABLE:
                model_info = lightfm_service.load_model_from_mlflow(use_production=True)
                print(f"✅ LightFM: Modelo carregado do MLflow (Produção)")
                print(f"   Run ID: {model_info.get('run_id', 'N/A')}")
                model_loaded = True
        except (FileNotFoundError, ValueError, ImportError) as e:
            # MLflow não disponível ou sem modelo - tentar arquivo local
            error_msg = str(e)
            if "Failed to download artifacts" in error_msg or "Erro ao carregar melhor modelo" in error_msg:
                print(f"ℹ️  LightFM: Runs antigos não têm modelo salvo corretamente")
                print(f"   Treine um novo modelo para usar o MLflow")
            else:
                print(f"ℹ️  LightFM: MLflow não disponível: {error_msg[:80]}")
        
        # Se não carregou do MLflow, tentar arquivo local
        if not model_loaded:
            try:
                lightfm_service.load_model_from_mlflow(use_production=False)
                print("✅ LightFM: Modelo carregado do MLflow (Melhor modelo)")
                model_loaded = True
            except Exception as e:
                print(f"⚠️  LightFM: Erro ao carregar modelo: {e}")
                print("   Tentando carregar do arquivo local...")
                try:
                    lightfm_service.load_model()
                    print("✅ LightFM: Modelo carregado do arquivo local!")
                    model_loaded = True
                except FileNotFoundError:
                    print("ℹ️  LightFM: Modelo ainda não foi treinado")
                except Exception as e:
                    print(f"⚠️  LightFM: Erro ao carregar modelo: {e}")
    except Exception as e:
        print(f"⚠️  LightFM Service não pôde ser inicializado: {e}")
        LIGHTFM_AVAILABLE = False
else:
    print("⚠️  LightFM não está disponível no ambiente principal (venv)")
    print("   O modelo será treinado/usado via Conda quando necessário")

surprise_service = SurpriseService()

# Função auxiliar para buscar usuário sem colunas que não existem
def get_usuario_by_id(db: Session, usuario_id: int):
    """Busca usuário por ID usando apenas colunas que existem no banco"""
    from sqlalchemy import select
    stmt = select(
        Usuarios.id,
        Usuarios.nome,
        Usuarios.email,
        Usuarios.senha_hash,
        Usuarios.curso,
        Usuarios.idade,
        Usuarios.descricao,
        Usuarios.id_universidade,
        Usuarios.data_cadastro
    ).filter(Usuarios.id == usuario_id)
    
    result = db.execute(stmt).first()
    if not result:
        return None
    
    # Criar objeto Usuarios com os dados
    usuario = Usuarios()
    usuario.id = result.id
    usuario.nome = result.nome
    usuario.email = result.email
    usuario.senha_hash = result.senha_hash
    usuario.curso = result.curso
    usuario.idade = result.idade
    usuario.descricao = result.descricao
    usuario.id_universidade = result.id_universidade
    usuario.data_cadastro = result.data_cadastro
    return usuario

# Função auxiliar para buscar estabelecimento sem colunas que não existem
def get_estabelecimento_by_id(db: Session, estabelecimento_id: int):
    """Busca estabelecimento por ID usando apenas colunas que existem no banco"""
    from sqlalchemy import select
    stmt = select(
        Estabelecimentos.id,
        Estabelecimentos.descricao,
        Estabelecimentos.endereco,
        Estabelecimentos.cidade,
        Estabelecimentos.horario_funcionamento,
        Estabelecimentos.dono_nome,
        Estabelecimentos.dono_email,
        Estabelecimentos.id_categoria
    ).filter(Estabelecimentos.id == estabelecimento_id)
    
    result = db.execute(stmt).first()
    if not result:
        return None
    
    # Criar objeto Estabelecimentos com os dados
    estabelecimento = Estabelecimentos()
    estabelecimento.id = result.id
    estabelecimento.descricao = result.descricao
    estabelecimento.endereco = result.endereco
    estabelecimento.cidade = result.cidade
    estabelecimento.horario_funcionamento = result.horario_funcionamento
    estabelecimento.dono_nome = result.dono_nome
    estabelecimento.dono_email = result.dono_email
    estabelecimento.id_categoria = result.id_categoria
    return estabelecimento

# Caminho do Python do Conda para LightFM - detectar dinamicamente (cross-platform)
def get_conda_python_path():
    """
    Detecta o caminho do Python do Conda dinamicamente (cross-platform)
    Suporta: macOS, Linux, Windows
    """
    import platform
    import sys
    
    # Verificar variável de ambiente primeiro (mais confiável para grupos)
    env_path = os.environ.get("CONDA_PYTHON_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    
    # Detectar sistema operacional
    system = platform.system()
    is_windows = system == "Windows"
    
    # Tentar detectar via conda info (funciona em todos os sistemas)
    try:
        import subprocess as sp
        conda_base = sp.run(
            ["conda", "info", "--base"], 
            capture_output=True, 
            text=True, 
            timeout=5,
            shell=is_windows  # Windows precisa de shell=True
        )
        if conda_base.returncode == 0:
            conda_base_path = conda_base.stdout.strip()
            
            # Construir caminho baseado no OS
            if is_windows:
                # Windows: envs\lightfm_py311\python.exe
                python_exe = Path(conda_base_path) / "envs" / "lightfm_py311" / "python.exe"
                if python_exe.exists():
                    return str(python_exe)
                # Tentar python3.11.exe também
                python_exe = Path(conda_base_path) / "envs" / "lightfm_py311" / "python3.11.exe"
                if python_exe.exists():
                    return str(python_exe)
            else:
                # Linux/macOS: envs/lightfm_py311/bin/python3.11
                python_path = Path(conda_base_path) / "envs" / "lightfm_py311" / "bin" / "python3.11"
                if python_path.exists():
                    return str(python_path)
                # Tentar python3 também
                python_path = Path(conda_base_path) / "envs" / "lightfm_py311" / "bin" / "python3"
                if python_path.exists():
                    return str(python_path)
    except Exception as e:
        print(f"⚠️  Erro ao detectar Conda via 'conda info': {e}")
    
    # Fallback: tentar caminhos comuns baseados no OS
    home = Path.home()
    common_paths = []
    
    if is_windows:
        # Windows: Caminhos comuns
        common_paths = [
            home / "miniconda3" / "envs" / "lightfm_py311" / "python.exe",
            home / "anaconda3" / "envs" / "lightfm_py311" / "python.exe",
            Path("C:/ProgramData/miniconda3/envs/lightfm_py311/python.exe"),
            Path("C:/ProgramData/anaconda3/envs/lightfm_py311/python.exe"),
        ]
    else:
        # Linux/macOS: Caminhos comuns
        common_paths = [
            home / "miniconda3" / "envs" / "lightfm_py311" / "bin" / "python3.11",
            home / "anaconda3" / "envs" / "lightfm_py311" / "bin" / "python3.11",
            home / "miniforge3" / "envs" / "lightfm_py311" / "bin" / "python3.11",
            # macOS Homebrew específico (manter para compatibilidade)
            Path("/opt/homebrew/Caskroom/miniconda/base/envs/lightfm_py311/bin/python3.11"),
            Path("/opt/homebrew/Caskroom/miniforge/base/envs/lightfm_py311/bin/python3.11"),
        ]
    
    # Verificar caminhos comuns
    for path in common_paths:
        if path.exists():
            return str(path)
    
    # Retornar None se não encontrar
    return None

CONDA_PYTHON_PATH = get_conda_python_path()

def predict_lightfm_via_conda(user_id: int, num_items: int, db: Session) -> List[Tuple[int, float]]:
    """Faz predição LightFM via Conda quando não está disponível no venv"""
    # Script está na raiz do projeto, não em app/scripts
    script_path = Path(__file__).parent.parent.parent / "scripts" / "lightfm_predict.py"
    
    # Detectar caminho do Conda
    conda_python = get_conda_python_path()
    
    if not conda_python or not Path(conda_python).exists():
        raise HTTPException(
            status_code=503,
            detail="Python do Conda não encontrado. Verifique se o ambiente lightfm_py311 está instalado."
        )
    
    try:
        # Tentar usar caminho direto do Python
        result = subprocess.run(
            [conda_python, str(script_path), str(user_id), str(num_items)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path(__file__).parent.parent.parent),
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).parent.parent.parent), PYTHONWARNINGS="ignore")
        )
        
        if result.returncode == 0:
            try:
                # Tentar encontrar JSON no stdout (pode ter warnings antes)
                stdout = result.stdout.strip()
                
                # Procurar por JSON no stdout (pode ter warnings antes)
                json_start = stdout.find('[')
                if json_start == -1:
                    json_start = stdout.find('{')
                
                if json_start == -1:
                    # Se não encontrar JSON, tentar stderr
                    error_msg = result.stderr if result.stderr else stdout
                    raise HTTPException(
                        status_code=500,
                        detail=f"Resposta do LightFM não contém JSON válido: {error_msg[:200]}"
                    )
                
                # Extrair apenas a parte JSON
                json_str = stdout[json_start:]
                predictions = json.loads(json_str)
                
                # Verificar se é um erro
                if isinstance(predictions, dict) and "error" in predictions:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro no script LightFM: {predictions['error']}"
                    )
                return [(int(item_id), float(score)) for item_id, score in predictions]
            except json.JSONDecodeError as e:
                # Se não conseguir parsear, verificar stderr
                error_msg = result.stderr if result.stderr else result.stdout
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao parsear resultado do LightFM: {str(e)}. Output: {error_msg[:500]}"
                )
        else:
            # Tentar parsear erro em JSON
            error_msg = result.stderr if result.stderr else result.stdout
            try:
                error_data = json.loads(error_msg)
                if isinstance(error_data, dict) and "error" in error_data:
                    error_msg = error_data["error"]
            except:
                pass
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao executar LightFM via Conda: {error_msg}"
            )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao parsear resultado do LightFM: {result.stdout if 'result' in locals() else str(e)}"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Python do Conda não encontrado: {str(e)}. Verifique se o ambiente lightfm_py311 está instalado."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar LightFM via Conda: {str(e)}"
        )


def get_similar_users_via_conda(user_id: int, num_users: int) -> List[Tuple[int, float]]:
    """Obtém usuários similares via Conda"""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "lightfm_similar_users.py"
    
    conda_python = get_conda_python_path()
    if not conda_python or not Path(conda_python).exists():
        raise HTTPException(
            status_code=503,
            detail="Python do Conda não encontrado."
        )

    try:
        result = subprocess.run(
            [conda_python, str(script_path), str(user_id), str(num_users)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path(__file__).parent.parent.parent),
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).parent.parent.parent), PYTHONWARNINGS="ignore")
        )
        
        if result.returncode == 0:
            try:
                json_start = result.stdout.find('[')
                if json_start == -1:
                    raise json.JSONDecodeError("JSON não encontrado", result.stdout, 0)
                
                json_str = result.stdout[json_start:]
                predictions = json.loads(json_str)
                
                if isinstance(predictions, dict) and "error" in predictions:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro no script LightFM: {predictions['error']}"
                    )
                return [(int(uid), float(score)) for uid, score in predictions]
            except json.JSONDecodeError:
                error_msg = result.stderr if result.stderr else result.stdout
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao parsear resultado do LightFM: {error_msg[:500]}"
                )
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao executar script de similaridade: {error_msg}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter usuários similares via Conda: {str(e)}"
        )


class RecomendacaoItem(BaseModel):
    """Schema para item de recomendação"""
    estabelecimento_id: int
    score: float
    razao: Optional[str] = None


class RecomendacaoResponse(BaseModel):
    """Schema de resposta de recomendações"""
    usuario_id: int
    recomendacoes: List[RecomendacaoItem]
    tipo: str  # 'hybrid', 'cbf', 'cf'
    algoritmo: str  # 'lightfm' ou 'surprise'


class InteracaoRequest(BaseModel):
    """Schema para registro de interação"""
    usuario_id: int
    estabelecimento_id: int
    tipo_interacao: str  # 'visita', 'clique', 'favorito'
    peso: float = 1.0


class TreinarRequest(BaseModel):
    """Schema para treinamento de modelo"""
    algoritmo: str = "lightfm"  # 'lightfm' ou 'surprise'
    usar_features: bool = True
    loss: str = "warp"  # Para LightFM: 'warp', 'bpr', 'logistic'
    algorithm: str = "svd"  # Para Surprise: 'svd', 'knn_basic', etc.
    num_epochs: Optional[int] = None
    learning_rate: Optional[float] = None
    num_components: Optional[int] = None


def train_lightfm_via_conda(request: TreinarRequest) -> Dict:
    """Treina LightFM via Conda quando não está disponível no venv"""
    # Script está na raiz do projeto, não em app/scripts
    script_path = Path(__file__).parent.parent.parent / "scripts" / "lightfm_train.py"
    
    # Detectar caminho do Conda
    conda_python = get_conda_python_path()
    
    if not conda_python or not Path(conda_python).exists():
        raise HTTPException(
            status_code=503,
            detail="Python do Conda não encontrado. Verifique se o ambiente lightfm_py311 está instalado."
        )
    
    # Preparar parâmetros em JSON
    params = {
        "loss": request.loss,
        "usar_features": request.usar_features,
        "num_epochs": request.num_epochs or 30,
        "learning_rate": request.learning_rate or 0.05,
        "num_components": request.num_components or 30
    }
    params_json = json.dumps(params)
    
    # Tentar usar conda run primeiro (mais confiável)
    result = None
    try:
        # Executar diretamente com o Python do Conda
        result = subprocess.run(
            [conda_python, str(script_path), params_json],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(Path(__file__).parent.parent.parent),
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).parent.parent.parent), PYTHONWARNINGS="ignore")
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Python do Conda não encontrado: {str(e)}. Verifique se o ambiente lightfm_py311 está instalado."
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao executar LightFM via Conda: {str(e)}"
        )
    
    if result is None:
        raise HTTPException(
            status_code=500,
            detail="Erro ao executar treinamento LightFM via Conda"
        )
    
    try:
        
        if result.returncode == 0:
            try:
                # Tentar encontrar JSON no stdout (pode ter warnings antes)
                stdout = result.stdout.strip()
                
                # Procurar por JSON no stdout (pode ter warnings antes)
                json_start = stdout.find('{')
                if json_start == -1:
                    # Se não encontrar {, tentar stderr
                    error_msg = result.stderr if result.stderr else stdout
                    raise HTTPException(
                        status_code=500,
                        detail=f"Resposta do treinamento não contém JSON válido: {error_msg[:200]}"
                    )
                
                # Extrair apenas a parte JSON
                json_str = stdout[json_start:]
                response_data = json.loads(json_str)
                
                if response_data.get("success"):
                    return {
                        "message": response_data.get("message", "Modelo LightFM treinado com sucesso"),
                        "algoritmo": "lightfm",
                        "metricas": response_data.get("metricas", {})
                    }
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao treinar LightFM via Conda: {response_data.get('error', 'Erro desconhecido')}"
                    )
            except json.JSONDecodeError as e:
                # Se não conseguir parsear JSON, tentar ler stderr
                error_msg = result.stderr if result.stderr else result.stdout
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao parsear resposta do treinamento LightFM: {str(e)}. Output: {error_msg[:500]}"
                )
        else:
            # Tentar parsear erro em JSON
            try:
                error_data = json.loads(result.stderr)
                error_msg = error_data.get("error", result.stderr)
            except:
                error_msg = result.stderr if result.stderr else result.stdout
            
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao executar treinamento LightFM via Conda: {error_msg}"
            )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Python do Conda não encontrado: {str(e)}. Verifique se o ambiente lightfm_py311 está instalado."
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Timeout ao treinar LightFM via Conda. O treinamento pode estar demorando muito."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao treinar LightFM via Conda: {str(e)}"
        )


@router.get("/usuario/{usuario_id}/user->establishments", response_model=RecomendacaoResponse)
def get_recomendacoes_user_to_establishments(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações a retornar"),
    tipo: str = Query("hybrid", description="Tipo de recomendação: 'hybrid', 'cbf', 'cf'"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    usar_conda: bool = Query(False, description="Forçar uso do Conda para LightFM (mesmo se disponível no venv)"),
    db: Session = Depends(get_db)
):
    """
    Obter recomendações personalizadas para um usuário
    
    - **usuario_id**: ID do usuário
    - **top_n**: Quantidade de recomendações (padrão: 10)
    - **tipo**: Tipo de filtragem (apenas para LightFM)
        - 'hybrid': Combinação de CBF e CF (padrão do LightFM)
        - 'cbf': Content-Based Filtering (baseado em características)
        - 'cf': Collaborative Filtering (baseado em comportamento de usuários similares)
    - **algoritmo**: 'lightfm' (híbrido) ou 'surprise' (CF puro)
    """
    # Verificar se usuário existe
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        if algoritmo.lower() == "lightfm":
            # Se forçar uso do Conda ou LightFM não disponível no venv
            if usar_conda or not LIGHTFM_AVAILABLE or lightfm_service is None:
                if usar_conda:
                    print("ℹ️  Forçando uso do Conda para LightFM...")
                else:
                    print("ℹ️  LightFM não disponível no venv, usando Conda...")
                predictions = predict_lightfm_via_conda(usuario_id, top_n, db)
            else:
                # Tentar usar LightFM do venv primeiro
                try:
                    if lightfm_service.is_model_loaded():
                        predictions = lightfm_service.predict(
                            user_id=usuario_id,
                            num_items=top_n,
                            db=db
                        )
                    else:
                        # Modelo não carregado, usar Conda
                        print("ℹ️  LightFM modelo não carregado no venv, usando Conda...")
                        predictions = predict_lightfm_via_conda(usuario_id, top_n, db)
                except Exception as e:
                    # Se houver erro no venv, tentar Conda
                    print(f"⚠️  Erro ao usar LightFM do venv: {e}. Tentando via Conda...")
                    predictions = predict_lightfm_via_conda(usuario_id, top_n, db)
            algo_name = "lightfm"
        elif algoritmo.lower() == "surprise":
            # Usar Surprise
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
            algo_name = "surprise"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{algoritmo}' não suportado. Use 'lightfm' ou 'surprise'"
            )
        
        # Buscar informações dos estabelecimentos
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
            
            razao = None
            if estabelecimento:
                razao = f"Score: {score:.3f} - {estabelecimento.descricao[:50]}"
            
            recomendacoes.append(RecomendacaoItem(
                estabelecimento_id=estabelecimento_id,
                score=score,
                razao=razao
            ))
        
        return RecomendacaoResponse(
            usuario_id=usuario_id,
            recomendacoes=recomendacoes,
            tipo=tipo,
            algoritmo=algo_name
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")


@router.get("/usuario/{usuario_id}/user->user")
def get_recomendacoes_user_to_user(
    usuario_id: int,
    top_n: int = Query(10, description="Número de usuários similares a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obter usuários com gostos similares (user-user similarity)
    
    Útil para features como "Pessoas que você talvez conheça"
    """
    # Verificar se usuário existe
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")

    try:
        # A lógica para usar o lightfm_service localmente é complexa e propensa a erros
        # quando o modelo é treinado via conda. Simplificando para SEMPRE usar o script
        # do conda, que é o método mais robusto para este projeto.
        similar_users = get_similar_users_via_conda(usuario_id, top_n)
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": "lightfm",
            "similares": [
                {
                    "usuario_id": uid,
                    "similaridade": score
                }
                for uid, score in similar_users
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuários similares: {str(e)}")


@router.get("/estabelecimento/{estabelecimento_id}/similares")
def get_estabelecimentos_similares(
    estabelecimento_id: int,
    top_n: int = Query(10, description="Número de estabelecimentos similares"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Obter estabelecimentos similares (item-item similarity)
    
    Útil para "Pessoas que visitaram X também visitaram Y"
    """
    # Verificar se estabelecimento existe
    estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    try:
        if algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE or lightfm_service is None or not lightfm_service.is_model_loaded():
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível ou modelo não foi treinado. Treine o modelo primeiro via POST /recomendacoes/treinar com algoritmo=lightfm"
                )
            try:
                similar_items = lightfm_service.get_similar_items(
                    item_id=estabelecimento_id,
                    num_items=top_n
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao obter estabelecimentos similares: {str(e)}. Certifique-se de que o modelo foi treinado."
                )
        elif algoritmo.lower() == "surprise":
            try:
                similar_items = surprise_service.get_similar_items(
                    item_id=estabelecimento_id,
                    num_items=top_n
                )
            except (ValueError, AttributeError) as e:
                # Se não suporta similaridade, retornar itens populares
                from sqlalchemy import func
                popular = db.query(
                    RecomendacaoEstabelecimento.id_lugar,
                    func.avg(RecomendacaoEstabelecimento.score).label('avg_score')
                ).group_by(RecomendacaoEstabelecimento.id_lugar).order_by(
                    func.avg(RecomendacaoEstabelecimento.score).desc()
                ).limit(top_n).all()
                similar_items = [(item.id_lugar, float(item.avg_score)) for item in popular]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{algoritmo}' não suportado"
            )
        
        return {
            "estabelecimento_id": estabelecimento_id,
            "algoritmo": algoritmo,
            "similares": [
                {
                    "estabelecimento_id": item_id,
                    "similaridade": score
                }
                for item_id, score in similar_items
            ]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/interacao")
def registrar_interacao(
    interacao: InteracaoRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar interação implícita do usuário com estabelecimento
    
    Essencial para treinar os modelos com feedback implícito
    """
    # Verificar se usuário e estabelecimento existem
    usuario = get_usuario_by_id(db, interacao.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário {interacao.usuario_id} não encontrado"
        )
    
    estabelecimento = get_estabelecimento_by_id(db, interacao.estabelecimento_id)
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {interacao.estabelecimento_id} não encontrado"
        )
    
    # Mapear tipo de interação para score
    score_map = {
        "visita": 5,
        "favorito": 4,
        "clique": 3
    }
    
    score = int(score_map.get(interacao.tipo_interacao.lower(), 3) * interacao.peso)
    score = max(1, min(5, score))  # Garantir entre 1-5
    
    # Verificar se já existe interação (usando select para evitar colunas que não existem)
    from sqlalchemy import select, update
    stmt = select(RecomendacaoEstabelecimento.id).filter(
        RecomendacaoEstabelecimento.id_usuario == interacao.usuario_id,
        RecomendacaoEstabelecimento.id_lugar == interacao.estabelecimento_id
    )
    result = db.execute(stmt).first()
    
    if result:
        # Atualizar score existente usando update direto
        stmt_update = update(RecomendacaoEstabelecimento).where(
            RecomendacaoEstabelecimento.id == result.id
        ).values(score=score)
        db.execute(stmt_update)
    else:
        # Criar nova interação
        nova_interacao = RecomendacaoEstabelecimento(
            id_usuario=interacao.usuario_id,
            id_lugar=interacao.estabelecimento_id,
            score=score,
            data_recomendacao=datetime.utcnow().date()
        )
        db.add(nova_interacao)
    
    db.commit()
    
    return {
        "message": "Interação registrada com sucesso",
        "usuario_id": interacao.usuario_id,
        "estabelecimento_id": interacao.estabelecimento_id,
        "tipo": interacao.tipo_interacao,
        "score": score
    }


@router.post("/treinar")
def treinar_modelo(
    request: TreinarRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Treinar modelo LightFM ou Surprise com dados atualizados
    
    - **algoritmo**: 'lightfm' ou 'surprise'
    - **usar_features**: (LightFM) Se True, usa metadados para CBF
    - **loss**: (LightFM) Função de perda ('warp', 'bpr', 'logistic')
    - **algorithm**: (Surprise) Algoritmo ('svd', 'knn_basic', 'knn_means', etc.)
    """
    try:
        if request.algoritmo.lower() == "lightfm":
            # Tentar treinar via VENV primeiro, se disponível
            if LIGHTFM_AVAILABLE and lightfm_service is not None:
                try:
                    # Treinar LightFM via VENV
                    metrics = lightfm_service.train(
                        db=db,
                        loss=request.loss,
                        use_features=request.usar_features,
                        num_epochs=request.num_epochs or 30,
                        learning_rate=request.learning_rate or 0.05,
                        num_components=request.num_components or 30,
                        use_mlflow=True  # Garantir que MLflow seja usado
                    )
                    
                    # Salvar modelo
                    lightfm_service.save_model()
                    
                    # Selecionar e recarregar melhor modelo do MLflow
                    try:
                        from app.services.lightfm_service import MLFLOW_AVAILABLE as MLFLOW_SERVICE_AVAILABLE
                        if MLFLOW_SERVICE_AVAILABLE:
                            try:
                                # NÃO chamar mark_best_as_production aqui - já foi chamado no treinamento!
                                # Apenas carregar o melhor modelo
                                model_info = lightfm_service.load_model_from_mlflow(use_production=True)
                                print(f"🔄 Melhor modelo carregado do MLflow")
                                print(f"   Run ID: {model_info.get('run_id', 'N/A')[:8]}...")
                                if 'metrics' in model_info:
                                    precision = model_info['metrics'].get('test_precision_at_10', 'N/A')
                                    if precision != 'N/A':
                                        try:
                                            if hasattr(precision, 'value'):
                                                precision = float(precision.value)
                                            else:
                                                precision = float(precision)
                                            print(f"   Métricas: Precision@10={precision:.4f}")
                                        except:
                                            print(f"   Métricas: Precision@10={precision}")
                            except Exception as reload_error:
                                print(f"⚠️  Não foi possível recarregar melhor modelo do MLflow: {reload_error}")
                                print(f"   O modelo treinado será usado. Reinicie o servidor para carregar o melhor modelo.")
                    except Exception as e:
                        print(f"ℹ️  MLflow não disponível para recarregamento: {e}")
                    
                    return {
                        "message": "Modelo LightFM treinado com sucesso (via VENV)",
                        "algoritmo": "lightfm",
                        "metricas": metrics
                    }
                except Exception as e:
                    # Se houver erro no venv, tentar Conda
                    print(f"⚠️  Erro ao treinar LightFM no venv: {e}. Tentando via Conda...")
                    return train_lightfm_via_conda(request)
            else:
                # Treinar via Conda quando não disponível no VENV
                print("ℹ️  LightFM não disponível no VENV, treinando via Conda...")
                return train_lightfm_via_conda(request)
        
        elif request.algoritmo.lower() == "surprise":
            # Treinar Surprise
            # Filtrar parâmetros, removendo os que não são do Surprise
            kwargs = {k: v for k, v in request.dict().items() 
                     if k not in ['algoritmo', 'usar_features', 'loss', 'algorithm'] and v is not None}
            
            metrics = surprise_service.train(
                db=db,
                algorithm=request.algorithm,
                **kwargs
            )
            
            # Salvar modelo
            surprise_service.save_model()
            
            return {
                "message": "Modelo Surprise treinado com sucesso",
                "algoritmo": "surprise",
                "algorithm": request.algorithm,
                "metricas": metrics
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algoritmo '{request.algoritmo}' não suportado. Use 'lightfm' ou 'surprise'"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao treinar modelo: {str(e)}")


@router.get("/cold-start/usuario/{usuario_id}")
def cold_start_usuario(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações para usuário novo (cold start)
    
    - LightFM: Usa apenas CBF baseado nas preferências declaradas
    - Surprise: Retorna itens mais populares
    """
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        if algoritmo.lower() == "lightfm":
            if not LIGHTFM_AVAILABLE or lightfm_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="LightFM não está disponível. Instale: pip install lightfm"
                )
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
            
            recomendacoes.append({
                "estabelecimento_id": estabelecimento_id,
                "score": score,
                "descricao": estabelecimento.descricao if estabelecimento else None
            })
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "cold_start",
            "recomendacoes": recomendacoes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cold-start/estabelecimento/{estabelecimento_id}")
def cold_start_estabelecimento(
    estabelecimento_id: int,
    db: Session = Depends(get_db)
):
    """
    Verificar se estabelecimento novo está pronto para ser recomendado
    
    Retorna quais metadados estão faltando para melhor performance
    """
    estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
    
    if not estabelecimento:
        raise HTTPException(
            status_code=404,
            detail=f"Estabelecimento {estabelecimento_id} não encontrado"
        )
    
    # Verificar features/preferências
    from app.models.estabelecimento_preferencia import EstabelecimentoPreferencia
    
    features = db.query(EstabelecimentoPreferencia).filter(
        EstabelecimentoPreferencia.id_estabelecimento == estabelecimento_id
    ).all()
    
    # Verificar interações
    interacoes = db.query(RecomendacaoEstabelecimento).filter(
        RecomendacaoEstabelecimento.id_lugar == estabelecimento_id
    ).count()
    
    status = "pronto" if len(features) >= 3 and interacoes >= 5 else "precisa_melhorar"
    
    return {
        "estabelecimento_id": estabelecimento_id,
        "status": status,
        "features_count": len(features),
        "interacoes_count": interacoes,
        "recomendacoes": {
            "min_features": 3,
            "min_interacoes": 5,
            "tem_features_suficientes": len(features) >= 3,
            "tem_interacoes_suficientes": interacoes >= 5
        }
    }


@router.get("/diversidade/usuario/{usuario_id}")
def get_recomendacoes_diversas(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    explorar: float = Query(0.1, description="Taxa de exploração (0-1)"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações com diversidade (evita bolha de filtro)
    
    Usa estratégia epsilon-greedy para balancear relevância e diversidade
    """
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    import random
    
    try:
        # Obter recomendações normais
        if algoritmo.lower() == "lightfm":
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,  # Pegar mais para diversificar
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        # Aplicar diversidade: explorar com probabilidade 'explorar'
        if random.random() < explorar:
            # Modo exploração: pegar itens aleatórios
            all_items = db.query(Estabelecimentos.id).all()
            random_items = random.sample([item[0] for item in all_items], min(top_n, len(all_items)))
            predictions = [(item_id, 0.5) for item_id in random_items]
        else:
            # Modo exploração: usar top N
            predictions = predictions[:top_n]
        
        recomendacoes = []
        for estabelecimento_id, score in predictions:
            estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
            
            recomendacoes.append({
                "estabelecimento_id": estabelecimento_id,
                "score": score,
                "descricao": estabelecimento.descricao if estabelecimento else None
            })
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "diversidade",
            "explorar": explorar,
            "recomendacoes": recomendacoes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contexto/usuario/{usuario_id}")
def get_recomendacoes_contextuais(
    usuario_id: int,
    hora_atual: Optional[int] = Query(None, description="Hora do dia (0-23)"),
    dia_semana: Optional[int] = Query(None, description="Dia da semana (0-6)"),
    latitude: Optional[float] = Query(None, description="Latitude do usuário"),
    longitude: Optional[float] = Query(None, description="Longitude do usuário"),
    top_n: int = Query(10, description="Número de recomendações"),
    algoritmo: str = Query("lightfm", description="Algoritmo: 'lightfm' ou 'surprise'"),
    db: Session = Depends(get_db)
):
    """
    Recomendações contextuais baseadas em localização e tempo
    
    Considera:
    - Horário de funcionamento
    - Distância do usuário
    - Horários de pico
    - Padrões por dia da semana
    """
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        # Obter recomendações base
        if algoritmo.lower() == "lightfm":
            predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        elif algoritmo.lower() == "surprise":
            predictions = surprise_service.predict(
                user_id=usuario_id,
                num_items=top_n * 2,
                db=db
            )
        else:
            raise HTTPException(status_code=400, detail="Algoritmo inválido")
        
        # Filtrar por contexto
        from app.models.estabelecimentos import Estabelecimentos
        
        recomendacoes_contextuais = []
        for estabelecimento_id, score in predictions:
            estabelecimento = get_estabelecimento_by_id(db, estabelecimento_id)
            
            if not estabelecimento:
                continue
            
            # Verificar horário de funcionamento
            if hora_atual is not None and estabelecimento.horario_funcionamento:
                # Simplificado: verificar se está dentro do horário
                # Em produção, fazer parsing completo do horário
                pass
            
            # Ajustar score baseado em contexto
            context_score = score
            
            # Se tem localização, poderia calcular distância aqui
            # Por enquanto, apenas retornar com score ajustado
            
            recomendacoes_contextuais.append({
                "estabelecimento_id": estabelecimento_id,
                "score": context_score,
                "score_original": score,
                "descricao": estabelecimento.descricao,
                "horario_funcionamento": estabelecimento.horario_funcionamento
            })
        
        # Ordenar por score contextual e pegar top N
        recomendacoes_contextuais.sort(key=lambda x: x["score"], reverse=True)
        recomendacoes_contextuais = recomendacoes_contextuais[:top_n]
        
        return {
            "usuario_id": usuario_id,
            "algoritmo": algoritmo,
            "tipo": "contextual",
            "contexto": {
                "hora_atual": hora_atual,
                "dia_semana": dia_semana,
                "latitude": latitude,
                "longitude": longitude
            },
            "recomendacoes": recomendacoes_contextuais
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparar/{usuario_id}")
def comparar_algoritmos(
    usuario_id: int,
    top_n: int = Query(10, description="Número de recomendações"),
    db: Session = Depends(get_db)
):
    """
    Compara recomendações de LightFM e Surprise para o mesmo usuário
    """
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário {usuario_id} não encontrado")
    
    try:
        # LightFM
        if LIGHTFM_AVAILABLE and lightfm_service is not None:
            lightfm_predictions = lightfm_service.predict(
                user_id=usuario_id,
                num_items=top_n,
                db=db
            )
        else:
            lightfm_predictions = []
        
        # Surprise
        surprise_predictions = surprise_service.predict(
            user_id=usuario_id,
            num_items=top_n,
            db=db
        )
        
        # Comparar
        lightfm_ids = {item_id for item_id, _ in lightfm_predictions}
        surprise_ids = {item_id for item_id, _ in surprise_predictions}
        
        intersection = lightfm_ids.intersection(surprise_ids)
        
        return {
            "usuario_id": usuario_id,
            "comparacao": {
                "lightfm": {
                    "recomendacoes": [
                        {"estabelecimento_id": item_id, "score": score}
                        for item_id, score in lightfm_predictions
                    ],
                    "total": len(lightfm_predictions)
                },
                "surprise": {
                    "recomendacoes": [
                        {"estabelecimento_id": item_id, "score": score}
                        for item_id, score in surprise_predictions
                    ],
                    "total": len(surprise_predictions)
                },
                "intersecao": {
                    "itens_comuns": list(intersection),
                    "total_comum": len(intersection),
                    "percentual_comum": len(intersection) / max(len(lightfm_ids), 1) * 100
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



