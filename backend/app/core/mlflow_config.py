"""
Configuração do MLflow para rastreamento de experimentos do LightFM

Este módulo centraliza as configurações do MLflow e fornece utilitários
para gerenciar experimentos e modelos.
"""

import os
from pathlib import Path
from typing import Optional
import mlflow
from mlflow.tracking import MlflowClient

# Nome do experimento no MLflow
EXPERIMENT_NAME = "lightfm_recommendations"

# Nome do modelo no Model Registry
MODEL_NAME = "lightfm_model"

# Diretório padrão para armazenar artefatos do MLflow
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    f"file://{Path(__file__).parent.parent.parent.parent / 'mlruns'}"
)


def get_or_create_experiment() -> str:
    """
    Obtém ou cria o experimento no MLflow
    
    Returns:
        ID do experimento (string)
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    try:
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
            print(f"✅ Experimento '{EXPERIMENT_NAME}' criado com ID: {experiment_id}")
        else:
            experiment_id = experiment.experiment_id
            print(f"ℹ️  Usando experimento existente '{EXPERIMENT_NAME}' (ID: {experiment_id})")
        
        return experiment_id
    except Exception as e:
        print(f"⚠️  Erro ao configurar experimento MLflow: {e}")
        print(f"   Continuando sem MLflow...")
        raise


def get_client() -> Optional[MlflowClient]:
    """
    Retorna o cliente MLflow configurado
    
    Returns:
        MlflowClient ou None se houver erro
    """
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        return MlflowClient()
    except Exception as e:
        print(f"⚠️  Erro ao criar cliente MLflow: {e}")
        return None


def get_best_model_run() -> Optional[str]:
    """
    Busca o run com melhor métrica (test_precision_at_10) no experimento
    
    Returns:
        run_id do melhor modelo ou None se não encontrar
    """
    try:
        client = get_client()
        if client is None:
            return None
        
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            return None
        
        # Buscar todos os runs do experimento (sem order_by com @)
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=100  # Buscar mais runs para ordenar manualmente
        )
        
        if not runs or len(runs) == 0:
            return None
        
        # Ordenar manualmente por test_precision_at_10 (descendente)
        # Filtrar runs que têm a métrica e não têm evaluation_warning
        valid_runs = []
        for run in runs:
            metrics = run.data.metrics
            # Ignorar runs com warnings de avaliação
            if "evaluation_warning" in metrics:
                continue
            # Obter test_precision_at_10
            precision = metrics.get("test_precision_at_10")
            if precision is not None:
                # Converter para float se necessário
                if hasattr(precision, 'value'):
                    precision_val = float(precision.value)
                else:
                    precision_val = float(precision)
                valid_runs.append((run, precision_val))
        
        if len(valid_runs) == 0:
            return None
        
        # Ordenar por precision (descendente) e retornar o melhor
        valid_runs.sort(key=lambda x: x[1], reverse=True)
        best_run = valid_runs[0][0]
        return best_run.info.run_id
        
    except Exception as e:
        print(f"⚠️  Erro ao buscar melhor modelo: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None


def get_production_model_version() -> Optional[str]:
    """
    Busca a versão do melhor modelo (com tag is_best=true)
    Como stages estão deprecated, usamos tags
    
    Returns:
        Versão do melhor modelo ou None
    """
    try:
        client = get_client()
        if client is None:
            return None
        
        # Buscar versão com tag is_best=true
        model_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        
        for version in model_versions:
            # Tags podem ser dict ou lista - normalizar
            try:
                if isinstance(version.tags, dict):
                    tags = version.tags
                else:
                    tags = {tag.key: tag.value for tag in version.tags} if version.tags else {}
            except Exception:
                tags = {}
            
            if tags.get("is_best") == "true":
                return version.version
        
        # Fallback: retornar última versão registrada (maior número)
        versions_list = list(model_versions)
        if versions_list:
            versions_sorted = sorted(versions_list, key=lambda v: int(v.version), reverse=True)
            return versions_sorted[0].version
        
        return None
    except Exception as e:
        print(f"⚠️  Erro ao buscar melhor modelo: {e}")
        return None


def register_model_to_production(run_id: str, metric_name: str = "test_precision_at_10"):
    """
    Registra um modelo no Model Registry e marca como Production
    
    Args:
        run_id: ID do run do MLflow
        metric_name: Nome da métrica usada para comparar modelos
    """
    try:
        client = get_client()
        if client is None:
            return False
        
        # Registrar modelo - usar o caminho do artefato salvo
        # O modelo foi salvo como artefato em "model/lightfm_model.pkl"
        # MLflow não registra artefatos genéricos, então vamos usar uma abordagem diferente:
        # Simplesmente não registrar no Model Registry quando há warnings
        # Quando não há warnings, o modelo já foi salvo como pyfunc no train()
        
        # Para modelos com métricas válidas, tentar registrar
        # O modelo deve ter sido salvo como pyfunc no método train()
        model_uri = f"runs:/{run_id}/model"
        try:
            model_version = mlflow.register_model(model_uri, MODEL_NAME)
        except Exception as e:
            # Se falhar, o modelo foi salvo apenas como artefato
            # Neste caso, não podemos registrar no Model Registry
            # Mas ainda podemos usar o artefato diretamente
            raise ValueError(f"Não foi possível registrar modelo no Model Registry. Modelo salvo como artefato em runs:/{run_id}/model/lightfm_model.pkl")
        
        # Verificar se há modelo em produção
        production_version = get_production_model_version()
        
        if production_version is None:
            # Primeiro modelo - marcar como Production
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=model_version.version,
                stage="Production"
            )
            print(f"✅ Modelo registrado e marcado como Production (versão {model_version.version})")
        else:
            # Comparar métricas
            current_run = client.get_run(run_id)
            current_metric = current_run.data.metrics.get(metric_name, 0.0)
            
            production_run_id = None
            for version in client.search_model_versions(f"name='{MODEL_NAME}'"):
                if version.current_stage == "Production":
                    # Extrair run_id do source
                    if "runs:/" in version.source:
                        production_run_id = version.source.split("runs:/")[1].split("/")[0]
                        break
            
            if production_run_id:
                try:
                    production_run = client.get_run(production_run_id)
                    # Converter métrica para float se necessário
                    prod_metric_val = production_run.data.metrics.get(metric_name, 0.0)
                    if hasattr(prod_metric_val, 'value'):
                        production_metric = float(prod_metric_val.value)
                    else:
                        production_metric = float(prod_metric_val)
                    
                    # Converter métrica atual para float se necessário
                    if hasattr(current_metric, 'value'):
                        current_metric_float = float(current_metric.value)
                    else:
                        current_metric_float = float(current_metric)
                    
                    if current_metric_float > production_metric:
                        # Novo modelo é melhor - atualizar produção
                        try:
                            client.transition_model_version_stage(
                                name=MODEL_NAME,
                                version=production_version,
                                stage="Archived"
                            )
                            client.transition_model_version_stage(
                                name=MODEL_NAME,
                                version=model_version.version,
                                stage="Production"
                            )
                            print(f"✅ Novo modelo é melhor! Marcado como Production (versão {model_version.version})")
                            print(f"   Métrica anterior: {production_metric:.4f} → Nova: {current_metric_float:.4f}")
                        except Exception as stage_err:
                            print(f"⚠️  Erro ao fazer transição de stage: {stage_err}")
                            print(f"   Modelo registrado como versão {model_version.version}, mas precisa ser marcado manualmente")
                    else:
                        # Modelo atual é melhor - manter em produção
                        try:
                            client.transition_model_version_stage(
                                name=MODEL_NAME,
                                version=model_version.version,
                                stage="Staging"
                            )
                            print(f"ℹ️  Modelo atual é melhor. Novo modelo em Staging (versão {model_version.version})")
                        except Exception as stage_err:
                            print(f"⚠️  Erro ao marcar como Staging: {stage_err}")
                            print(f"   Modelo registrado como versão {model_version.version}")
                except Exception as comp_err:
                    print(f"⚠️  Erro ao comparar modelos: {comp_err}")
                    # Não conseguiu comparar - marcar como Staging
                    try:
                        client.transition_model_version_stage(
                            name=MODEL_NAME,
                            version=model_version.version,
                            stage="Staging"
                        )
                        print(f"ℹ️  Modelo registrado em Staging (versão {model_version.version})")
                    except Exception as stage_err:
                        print(f"⚠️  Erro ao marcar como Staging: {stage_err}")
            else:
                # Não conseguiu comparar - marcar como Staging
                try:
                    client.transition_model_version_stage(
                        name=MODEL_NAME,
                        version=model_version.version,
                        stage="Staging"
                    )
                    print(f"ℹ️  Modelo registrado em Staging (versão {model_version.version})")
                except Exception as stage_err:
                    print(f"⚠️  Erro ao marcar como Staging: {stage_err}")
                    print(f"   Modelo registrado como versão {model_version.version}, mas precisa ser marcado manualmente")
        
        return True
    except Exception as e:
        print(f"⚠️  Erro ao registrar modelo: {e}")
        return False

