#!/usr/bin/env python3
"""
Script para treinar LightFM usando Python 3.11 via conda
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz do projeto ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Importar após configurar path
from app.core.database import SessionLocal
from app.services.lightfm_service import LightFMService

def main():
    """Treina LightFM usando Python 3.11"""
    print("=" * 60)
    print("🎓 Treinando LightFM com Python 3.11")
    print("=" * 60)
    print()
    
    # Criar serviço
    service = LightFMService()
    
    # Obter sessão do banco
    db = SessionLocal()
    
    try:
        print("🔄 Treinando modelo...")
        metrics = service.train(
            db=db,
            loss="warp",
            use_features=True,
            num_epochs=30,
            learning_rate=0.05,
            num_components=30
        )
        
        print("✅ Treinamento concluído!")
        print(f"📊 Métricas: {metrics}")
        
        # Salvar modelo
        service.save_model()
        print("💾 Modelo salvo!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

