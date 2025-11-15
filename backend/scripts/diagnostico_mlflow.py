#!/usr/bin/env python3
"""
Script de diagnóstico do MLflow
Verifica se o MLflow está configurado corretamente
"""

import sys
from pathlib import Path

# Adicionar diretório raiz e backend ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
backend_dir = script_dir.parent

# Adicionar ambos os caminhos
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("DIAGNÓSTICO MLFLOW")
print("=" * 60)

# 1. Verificar se MLflow está instalado
print("\n1. Verificando instalação do MLflow...")
try:
    import mlflow
    print(f"   ✅ MLflow instalado - Versão: {mlflow.__version__}")
except ImportError:
    print("   ❌ MLflow NÃO está instalado!")
    print("   Execute: pip install mlflow>=2.8.0")
    sys.exit(1)

# 2. Verificar configuração do MLflow
print("\n2. Verificando configuração...")
try:
    from app.core.mlflow_config import (
        MLFLOW_TRACKING_URI,
        EXPERIMENT_NAME,
        MODEL_NAME
    )
    print(f"   ✅ Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"   ✅ Nome do Experimento: {EXPERIMENT_NAME}")
    print(f"   ✅ Nome do Modelo: {MODEL_NAME}")
except Exception as e:
    print(f"   ❌ Erro ao importar configuração: {e}")
    sys.exit(1)

# 3. Verificar se o diretório mlruns existe
print("\n3. Verificando diretório mlruns...")
mlruns_dir = project_root / "mlruns"
if mlruns_dir.exists():
    print(f"   ✅ Diretório mlruns existe: {mlruns_dir}")
    
    # Listar experimentos
    experiments = list(mlruns_dir.glob("*/meta.yaml"))
    print(f"   📁 Experimentos encontrados: {len(experiments)}")
    for exp_file in experiments:
        exp_id = exp_file.parent.name
        print(f"      - Experimento ID: {exp_id}")
        
        # Verificar runs
        runs_dir = exp_file.parent
        runs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name != ".trash" and d.name != "models"]
        print(f"        Runs encontrados: {len(runs)}")
        for run_dir in runs[:5]:  # Mostrar apenas os 5 primeiros
            if run_dir.name.startswith("."):
                continue
            print(f"          - Run: {run_dir.name}")
else:
    print(f"   ⚠️  Diretório mlruns não existe: {mlruns_dir}")
    print(f"   (Será criado no primeiro treinamento)")

# 4. Testar criação de experimento
print("\n4. Testando criação de experimento...")
try:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment:
        print(f"   ✅ Experimento '{EXPERIMENT_NAME}' existe (ID: {experiment.experiment_id})")
    else:
        print(f"   ℹ️  Experimento '{EXPERIMENT_NAME}' não existe (será criado no primeiro treinamento)")
except Exception as e:
    print(f"   ❌ Erro ao verificar experimento: {e}")

# 5. Testar criação de run
print("\n5. Testando criação de run...")
try:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    if experiment:
        mlflow.set_experiment(experiment_id=experiment.experiment_id)
    else:
        mlflow.set_experiment(EXPERIMENT_NAME)
    
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"   ✅ Run criado com sucesso (ID: {run_id})")
        mlflow.log_param("test_param", "test_value")
        mlflow.log_metric("test_metric", 1.0)
        print(f"   ✅ Parâmetros e métricas registrados")
    
    print(f"   ✅ Run finalizado com sucesso")
except Exception as e:
    import traceback
    print(f"   ❌ Erro ao criar run: {e}")
    print(f"   Traceback:\n{traceback.format_exc()}")

# 6. Verificar permissões
print("\n6. Verificando permissões...")
try:
    test_file = mlruns_dir / "test_write.tmp"
    test_file.write_text("test")
    test_file.unlink()
    print(f"   ✅ Permissões de escrita OK")
except Exception as e:
    print(f"   ❌ Erro de permissão: {e}")

print("\n" + "=" * 60)
print("DIAGNÓSTICO CONCLUÍDO")
print("=" * 60)

