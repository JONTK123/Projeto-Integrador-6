#!/usr/bin/env python3
"""
Script para fazer predições LightFM via Conda
Recebe user_id e num_items via argumentos de linha de comando e retorna predições em JSON
"""

import sys
import json
import warnings
from pathlib import Path

# Suprimir warnings do LightFM (especialmente sobre OpenMP) e redirecionar para stderr
warnings.filterwarnings('ignore')
# Redirecionar warnings restantes para stderr para não interferir no JSON
import logging
logging.captureWarnings(True)

# Adicionar diretório raiz do projeto ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.services.lightfm_service import LightFMService

def main():
    """Faz predição LightFM com parâmetros fornecidos"""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Uso: python lightfm_predict.py <user_id> <num_items>"}), file=sys.stderr)
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    num_items = int(sys.argv[2])
    
    try:
        service = LightFMService()
        service.load_model()
        
        db = SessionLocal()
        try:
            predictions = service.predict(
                user_id=user_id,
                num_items=num_items,
                db=db
            )
            result = [[int(item_id), float(score)] for item_id, score in predictions]
            print(json.dumps(result))
        finally:
            db.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
