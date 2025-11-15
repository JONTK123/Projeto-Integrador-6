#!/usr/bin/env python3
"""
Script para registrar modelos já treinados no Model Registry do MLflow
Útil quando modelos foram treinados mas não foram registrados automaticamente
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
backend_dir = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

try:
    import mlflow
    from app.core.mlflow_config import (
        get_client,
        get_or_create_experiment,
        MODEL_NAME,
        EXPERIMENT_NAME
    )
    
    print("=" * 60)
    print("REGISTRAR MODELOS NO MLFLOW MODEL REGISTRY")
    print("=" * 60)
    
    # Obter cliente
    client = get_client()
    if client is None:
        print("❌ Erro: Não foi possível criar cliente MLflow")
        sys.exit(1)
    
    # Obter experimento
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        print(f"❌ Experimento '{EXPERIMENT_NAME}' não encontrado")
        sys.exit(1)
    
    print(f"\n📁 Experimento: {EXPERIMENT_NAME} (ID: {experiment.experiment_id})")
    
    # Buscar todos os runs do experimento
    # Nota: MLflow não aceita @ no order_by, então buscamos todos e ordenamos manualmente
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=100
    )
    
    # Ordenar manualmente por test_precision@10 (descendente)
    runs = sorted(
        runs,
        key=lambda r: r.data.metrics.get("test_precision@10", 0.0),
        reverse=True
    )
    
    print(f"\n🔍 Encontrados {len(runs)} runs no experimento")
    
    if len(runs) == 0:
        print("❌ Nenhum run encontrado. Treine um modelo primeiro.")
        sys.exit(1)
    
    # Verificar quais já estão registrados
    registered_runs = set()
    model_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    for version in model_versions:
        if "runs:/" in version.source:
            run_id = version.source.split("runs:/")[1].split("/")[0]
            registered_runs.add(run_id)
    
    print(f"📊 Runs já registrados: {len(registered_runs)}")
    
    # Registrar runs não registrados
    registered_count = 0
    best_run = None
    best_metric = -1
    
    for run in runs:
        run_id = run.info.run_id
        
        if run_id in registered_runs:
            print(f"✓ Run {run_id[:8]}... já está registrado")
            continue
        
        # Verificar métricas
        metrics = run.data.metrics
        has_warning = "evaluation_warning" in metrics
        
        # Tentar obter test_precision@10, se não tiver, usar 0.0
        test_precision = metrics.get("test_precision@10", 0.0)
        
        if has_warning:
            print(f"⚠️  Run {run_id[:8]}... tem warnings (Precision@10: {test_precision:.4f})")
            # Continuar mesmo com warnings - pode ser o único modelo disponível
        
        if test_precision > best_metric:
            best_metric = test_precision
            best_run = run
        
        # Registrar modelo
        try:
            # Verificar se o arquivo existe fisicamente
            import os
            run_dir = Path(f"mlruns/{experiment.experiment_id}/{run_id}/artifacts/model/lightfm_model.pkl")
            if not run_dir.exists():
                print(f"❌ Run {run_id[:8]}... arquivo do modelo não existe: {run_dir}")
                continue
            
            # Tentar diferentes caminhos para o modelo
            model_paths = [
                f"runs:/{run_id}/artifacts/model/lightfm_model.pkl",
                f"runs:/{run_id}/artifacts/model",
                f"runs:/{run_id}/model/lightfm_model.pkl",
                f"runs:/{run_id}/model"
            ]
            
            model_version = None
            last_error = None
            for model_uri in model_paths:
                try:
                    model_version = mlflow.register_model(model_uri, MODEL_NAME)
                    print(f"✅ Run {run_id[:8]}... registrado como versão {model_version.version}")
                    print(f"   Precision@10: {test_precision:.4f}")
                    if has_warning:
                        print(f"   ⚠️  Tem warnings, mas foi registrado")
                    registered_count += 1
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if model_version is None:
                print(f"❌ Run {run_id[:8]}... não encontrou modelo em nenhum caminho")
                print(f"   Último erro: {last_error[:100] if last_error else 'N/A'}")
        except Exception as e:
            print(f"❌ Erro ao registrar run {run_id[:8]}...: {e}")
    
    # Marcar melhor modelo como Production
    # Atualizar best_run após registrar
    model_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if len(list(model_versions)) > 0:
        try:
            # Verificar se já há modelo em produção
            production_version = None
            for version in client.search_model_versions(f"name='{MODEL_NAME}'"):
                if version.current_stage == "Production":
                    production_version = version
                    break
            
            # Encontrar melhor modelo registrado
            best_registered_version = None
            best_registered_metric = -1
            
            for version in client.search_model_versions(f"name='{MODEL_NAME}'"):
                if "runs:/" in version.source:
                    try:
                        run_id = version.source.split("runs:/")[1].split("/")[0]
                        run = client.get_run(run_id)
                        metric = run.data.metrics.get("test_precision@10", 0.0)
                        if metric > best_registered_metric:
                            best_registered_metric = metric
                            best_registered_version = version
                    except:
                        continue
            
            if production_version:
                # Comparar métricas
                try:
                    prod_run_id = production_version.source.split("runs:/")[1].split("/")[0]
                    prod_run = client.get_run(prod_run_id)
                    prod_metric = prod_run.data.metrics.get("test_precision@10", 0.0)
                    
                    if best_registered_metric > prod_metric and best_registered_version:
                        # Novo modelo é melhor
                        client.transition_model_version_stage(
                            name=MODEL_NAME,
                            version=production_version.version,
                            stage="Archived"
                        )
                        client.transition_model_version_stage(
                            name=MODEL_NAME,
                            version=best_registered_version.version,
                            stage="Production"
                        )
                        print(f"\n✅ Melhor modelo marcado como Production!")
                        print(f"   Precision@10: {best_registered_metric:.4f}")
                    else:
                        print(f"\nℹ️  Modelo em produção já é o melhor (Precision@10: {prod_metric:.4f})")
                except Exception as e:
                    print(f"\n⚠️  Erro ao comparar modelos: {e}")
            else:
                # Não há modelo em produção - marcar o melhor registrado
                if best_registered_version:
                    client.transition_model_version_stage(
                        name=MODEL_NAME,
                        version=best_registered_version.version,
                        stage="Production"
                    )
                    print(f"\n✅ Melhor modelo marcado como Production!")
                    print(f"   Precision@10: {best_registered_metric:.4f}")
        except Exception as e:
            print(f"\n⚠️  Erro ao marcar melhor modelo como Production: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    
    print(f"\n" + "=" * 60)
    print(f"✅ Processo concluído!")
    print(f"   Modelos registrados: {registered_count}")
    print(f"=" * 60)
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print(f"   Certifique-se de que o MLflow está instalado: pip install mlflow")
    sys.exit(1)
except Exception as e:
    import traceback
    print(f"❌ Erro: {e}")
    print(f"   Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

