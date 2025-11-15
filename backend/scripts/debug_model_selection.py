#!/usr/bin/env python3
"""
Debug: Verificar por que o seletor não encontra modelos
"""

import sys
from pathlib import Path

# Adicionar diretório ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
backend_dir = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

try:
    from app.core.mlflow_model_selector import find_best_model_by_metrics
    from app.core.mlflow_config import get_client, EXPERIMENT_NAME
    import mlflow
    
    print("=" * 60)
    print("DEBUG: Seleção de Modelos")
    print("=" * 60)
    
    # Verificar experimento
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experimento '{EXPERIMENT_NAME}' não encontrado")
        sys.exit(1)
    
    print(f"\n✅ Experimento encontrado: {EXPERIMENT_NAME}")
    print(f"   ID: {experiment.experiment_id}")
    
    # Listar todos os runs
    client = get_client()
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=100
    )
    
    print(f"\n📊 Total de runs: {len(runs)}")
    
    if len(runs) == 0:
        print("❌ Nenhum run encontrado")
        sys.exit(1)
    
    # Analisar cada run
    print("\n🔍 Análise detalhada dos runs:")
    print("-" * 60)
    
    for i, run in enumerate(runs[:10], 1):  # Mostrar até 10 runs
        metrics = run.data.metrics
        has_warning = "evaluation_warning" in metrics
        precision = metrics.get("test_precision@10")
        
        print(f"\n{i}. Run ID: {run.info.run_id[:12]}...")
        print(f"   Status: {run.info.status}")
        print(f"   Evaluation warning: {has_warning}")
        
        if precision is not None:
            # Tentar converter
            try:
                if hasattr(precision, 'value'):
                    precision_val = float(precision.value)
                else:
                    precision_val = float(precision)
                print(f"   test_precision@10: {precision_val:.4f}")
            except Exception as e:
                print(f"   test_precision@10: {precision} (erro ao converter: {e})")
        else:
            print(f"   test_precision@10: NÃO ENCONTRADA")
        
        # Listar todas as métricas
        print(f"   Métricas disponíveis: {list(metrics.keys())}")
    
    # Testar função de seleção
    print("\n" + "=" * 60)
    print("🎯 Testando função de seleção...")
    print("=" * 60)
    
    result = find_best_model_by_metrics("test_precision@10")
    
    if result:
        run_id, info = result
        print(f"\n✅ Melhor modelo encontrado!")
        print(f"   Run ID: {run_id[:12]}...")
        print(f"   Métrica: {info['metric_value']:.4f}")
        print(f"   Has warning: {info.get('has_warning', 'N/A')}")
        print(f"   Outras métricas: {info.get('other_metrics', {})}")
    else:
        print("\n❌ Nenhum modelo válido encontrado pela função de seleção")
        print("\nPossíveis causas:")
        print("1. Todos os runs têm evaluation_warning E o fallback não está funcionando")
        print("2. Nenhum run tem a métrica test_precision@10")
        print("3. Erro ao converter métricas para float")
    
    print("\n" + "=" * 60)

except Exception as e:
    import traceback
    print(f"❌ Erro: {e}")
    print(f"\nTraceback:\n{traceback.format_exc()}")
    sys.exit(1)

