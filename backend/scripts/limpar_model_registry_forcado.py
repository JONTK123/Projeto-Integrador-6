#!/usr/bin/env python3
"""
Script para limpar Model Registry removendo arquivos diretamente
Usa essa abordagem devido a bug de serialização no MLflow

USO: python limpar_model_registry_forcado.py [--confirmar]
"""

import sys
from pathlib import Path
import shutil

# Caminho do projeto
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("=" * 60)
print("LIMPAR MODEL REGISTRY (FORÇADO)")
print("=" * 60)

model_registry_path = project_root / "mlruns" / "models"

if not model_registry_path.exists():
    print(f"\nℹ️  Diretório do Model Registry não encontrado: {model_registry_path}")
    print("Nenhuma ação necessária.")
    sys.exit(0)

# Listar modelos
models = list(model_registry_path.iterdir())
if not models:
    print("\nℹ️  Nenhum modelo encontrado no Model Registry")
    sys.exit(0)

print(f"\n📊 Modelos encontrados:")
total_versions = 0
for model_dir in models:
    if model_dir.is_dir():
        versions = [d.name for d in model_dir.iterdir() if d.is_dir() and d.name.startswith("version-")]
        total_versions += len(versions)
        print(f"  - {model_dir.name}: {len(versions)} versões")

print(f"\n⚠️  ATENÇÃO: Isso removerá {total_versions} versões")
print("Os RUNS (experimentos) serão mantidos.")

# Verificar se tem flag --confirmar
if "--confirmar" not in sys.argv:
    print("\n❌ Para confirmar, execute:")
    print(f"   python {Path(__file__).name} --confirmar")
    sys.exit(0)

print(f"\n🗑️  Removendo Model Registry...")

try:
    # Remover diretório completo do Model Registry
    shutil.rmtree(model_registry_path)
    print(f"✅ Model Registry removido com sucesso!")
    print(f"\n📂 Removido: {model_registry_path}")
    print(f"   {total_versions} versões removidas")
    print(f"\n✅ Limpeza concluída!")
    print(f"Os RUNS foram mantidos - você pode compará-los na UI do MLflow")
    print(f"Treine novamente para criar novas versões.")
except Exception as e:
    print(f"❌ Erro ao remover: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
