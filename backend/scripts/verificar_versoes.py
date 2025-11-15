#!/usr/bin/env python3
"""
Script para verificar versões registradas e suas métricas
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
backend_dir = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

try:
    from app.core.mlflow_config import get_client, MODEL_NAME
    import mlflow
    
    print("=" * 60)
    print("VERSÕES REGISTRADAS NO MODEL REGISTRY")
    print("=" * 60)
    
    client = get_client()
    if not client:
        print("❌ Erro: Cliente MLflow não disponível")
        sys.exit(1)
    
    # Listar versões
    versions = list(client.search_model_versions(f"name='{MODEL_NAME}'"))
    
    if not versions:
        print("\nℹ️  Nenhuma versão registrada")
        sys.exit(0)
    
    print(f"\n📊 Total de versões: {len(versions)}\n")
    
    for version in sorted(versions, key=lambda v: int(v.version)):
        print(f"Versão {version.version}:")
        print(f"  Source: {version.source}")
        
        # Extrair run_id
        if "runs:/" in version.source:
            run_id = version.source.split("runs:/")[1].split("/")[0]
            print(f"  Run ID: {run_id[:12]}...")
            
            # Obter métricas do run
            try:
                run = client.get_run(run_id)
                metrics = run.data.metrics
                
                precision = metrics.get("test_precision_at_10", "N/A")
                auc = metrics.get("test_auc", "N/A")
                
                # Converter para float se necessário
                try:
                    if hasattr(precision, 'value'):
                        precision = float(precision.value)
                    if hasattr(auc, 'value'):
                        auc = float(auc.value)
                    
                    print(f"  Métricas:")
                    print(f"    - test_precision_at_10: {precision:.4f}")
                    print(f"    - test_auc: {auc:.4f}")
                except:
                    print(f"  Métricas:")
                    print(f"    - test_precision_at_10: {precision}")
                    print(f"    - test_auc: {auc}")
            except Exception as e:
                print(f"  ⚠️  Erro ao obter métricas: {e}")
        
        # Verificar tags
        try:
            if isinstance(version.tags, dict):
                tags = version.tags
            else:
                tags = {tag.key: tag.value for tag in version.tags} if version.tags else {}
            
            if tags.get("is_best") == "true":
                print(f"  ⭐ MELHOR MODELO (tag is_best=true)")
        except:
            pass
        
        print()
    
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f"❌ Erro: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

