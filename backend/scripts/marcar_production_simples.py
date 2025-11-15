#!/usr/bin/env python3
"""
Script simples para marcar modelo como Production
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir.parent))

import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = "lightfm_model"

# Configurar tracking URI
mlflow.set_tracking_uri(f"file://{project_root}/mlruns")

client = MlflowClient()

# Listar versões
versions = client.search_model_versions(f"name='{MODEL_NAME}'")

if len(versions) == 0:
    print("❌ Nenhum modelo registrado")
    sys.exit(1)

print(f"Modelos encontrados: {len(versions)}")
for v in versions:
    print(f"  Versão {v.version}: {v.current_stage}")

# Pegar última versão
last_version = max(versions, key=lambda v: int(v.version))
print(f"\nMarcando versão {last_version.version} como Production...")

try:
    # Arquivar versão em produção atual se houver
    for v in versions:
        if v.current_stage == "Production":
            try:
                client.transition_model_version_stage(
                    name=MODEL_NAME,
                    version=v.version,
                    stage="Archived"
                )
                print(f"  Versão {v.version} arquivada")
            except:
                pass
    
    # Marcar última como Production
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=last_version.version,
        stage="Production"
    )
    print(f"✅ Versão {last_version.version} marcada como Production!")
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\nTente usar a UI do MLflow para marcar manualmente:")
    print("  mlflow ui --backend-store-uri file://$(pwd)/mlruns")
    sys.exit(1)

