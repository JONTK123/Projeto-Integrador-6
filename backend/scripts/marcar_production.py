#!/usr/bin/env python3
"""
Script para marcar um modelo como Production no MLflow
Útil quando o registro automático falha
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
    from app.core.mlflow_config import get_client, MODEL_NAME, get_production_model_version
    
    print("=" * 60)
    print("MARCAR MODELO COMO PRODUCTION")
    print("=" * 60)
    
    client = get_client()
    if client is None:
        print("❌ Erro: Não foi possível criar cliente MLflow")
        sys.exit(1)
    
    # Listar todas as versões
    versions = list(client.search_model_versions(f"name='{MODEL_NAME}'"))
    
    if len(versions) == 0:
        print("❌ Nenhum modelo registrado encontrado")
        sys.exit(1)
    
    print(f"\n📊 Modelos registrados: {len(versions)}")
    for v in versions:
        print(f"   Versão {v.version}: {v.current_stage} (Run: {v.run_id[:8]}...)")
    
    # Verificar se já há modelo em produção
    production_version = get_production_model_version()
    
    if production_version:
        print(f"\n⚠️  Já existe modelo em produção: versão {production_version}")
        resposta = input("Deseja substituir? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada")
            sys.exit(0)
        
        # Arquivar modelo atual
        try:
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=production_version,
                stage="Archived"
            )
            print(f"✅ Modelo versão {production_version} arquivado")
        except Exception as e:
            print(f"⚠️  Erro ao arquivar modelo: {e}")
    
    # Perguntar qual versão marcar como Production
    print(f"\nQual versão deseja marcar como Production?")
    print("(Deixe em branco para usar a última versão)")
    versao_input = input("Versão: ").strip()
    
    if versao_input:
        try:
            version_num = int(versao_input)
        except ValueError:
            print("❌ Versão inválida")
            sys.exit(1)
    else:
        # Usar última versão
        version_num = max([int(v.version) for v in versions])
        print(f"Usando última versão: {version_num}")
    
    # Marcar como Production
    try:
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=str(version_num),
            stage="Production"
        )
        print(f"\n✅ Modelo versão {version_num} marcado como Production!")
    except Exception as e:
        print(f"\n❌ Erro ao marcar como Production: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Concluído!")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)
except Exception as e:
    import traceback
    print(f"❌ Erro: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

