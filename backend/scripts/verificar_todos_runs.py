#!/usr/bin/env python3
"""
Script para verificar todos os runs e comparar métricas
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
backend_dir = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

try:
    from app.core.mlflow_config import get_client, EXPERIMENT_NAME
    import mlflow
    
    print("=" * 60)
    print("TODOS OS RUNS DO EXPERIMENTO")
    print("=" * 60)
    
    client = get_client()
    if not client:
        print("❌ Erro: Cliente MLflow não disponível")
        sys.exit(1)
    
    # Obter experimento
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experimento '{EXPERIMENT_NAME}' não encontrado")
        sys.exit(1)
    
    # Listar todos os runs (ordenar por tempo - mais recente primeiro)
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=100,
        order_by=["start_time DESC"]
    )
    
    if not runs:
        print("\nℹ️  Nenhum run encontrado")
        sys.exit(0)
    
    print(f"\n📊 Total de runs: {len(runs)}")
    print(f"\n🔝 Últimos 10 runs (mais recente primeiro):\n")
    
    for i, run in enumerate(runs[:10], 1):
        print(f"{i}. Run ID: {run.info.run_id[:12]}...")
        print(f"   Status: {run.info.status}")
        
        metrics = run.data.metrics
        has_warning = "evaluation_warning" in metrics
        
        if has_warning:
            print(f"   ⚠️  Tem evaluation_warning")
        
        # Obter métricas principais
        precision = metrics.get("test_precision_at_10", "N/A")
        auc = metrics.get("test_auc", "N/A")
        
        try:
            if precision != "N/A":
                if hasattr(precision, 'value'):
                    precision_val = float(precision.value)
                else:
                    precision_val = float(precision)
                print(f"   test_precision_at_10: {precision_val:.4f}")
            else:
                print(f"   test_precision_at_10: N/A")
            
            if auc != "N/A":
                if hasattr(auc, 'value'):
                    auc_val = float(auc.value)
                else:
                    auc_val = float(auc)
                print(f"   test_auc: {auc_val:.4f}")
            else:
                print(f"   test_auc: N/A")
        except Exception as e:
            print(f"   Métricas: Erro ao converter ({e})")
        
        print()
    
    print("=" * 60)
    print("\n💡 Análise:")
    
    # Encontrar melhor run por precision@10
    valid_runs = []
    for run in runs:
        metrics = run.data.metrics
        precision = metrics.get("test_precision_at_10")
        
        if precision is not None:
            try:
                if hasattr(precision, 'value'):
                    p_val = float(precision.value)
                else:
                    p_val = float(precision)
                
                valid_runs.append({
                    "run_id": run.info.run_id,
                    "precision": p_val,
                    "has_warning": "evaluation_warning" in metrics
                })
            except:
                pass
    
    if valid_runs:
        # Ordenar por precision (maior primeiro)
        valid_runs.sort(key=lambda x: x["precision"], reverse=True)
        
        print(f"\n🏆 Melhor run por test_precision_at_10:")
        best = valid_runs[0]
        print(f"   Run ID: {best['run_id'][:12]}...")
        print(f"   Precision: {best['precision']:.4f}")
        print(f"   Warning: {'Sim' if best['has_warning'] else 'Não'}")
        
        print(f"\n📋 Top 5 melhores:")
        for i, r in enumerate(valid_runs[:5], 1):
            warning_str = " ⚠️" if r["has_warning"] else ""
            print(f"   {i}. {r['run_id'][:12]}... - {r['precision']:.4f}{warning_str}")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    import traceback
    print(f"❌ Erro: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

