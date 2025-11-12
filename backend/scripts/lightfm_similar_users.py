#!/usr/bin/env python3
"""
Script para obter usuários similares via Conda
"""

import sys
import json
from pathlib import Path

# Adicionar diretório raiz do projeto ao path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from app.services.lightfm_service import LightFMService
from app.core.database import SessionLocal

def main():
    """Obtém usuários similares"""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Uso: python lightfm_similar_users.py <user_id> <num_users>"}), file=sys.stderr)
        sys.exit(1)
        
    try:
        user_id = int(sys.argv[1])
        num_users = int(sys.argv[2])
        
        service = LightFMService()
        
        # Carregar modelo
        service.load_model()
        
        db = SessionLocal()
        try:
            similar_users = service.get_similar_users(user_id=user_id, num_users=num_users)
            # Forçar a conversão para tipos nativos de Python aqui para garantir
            # Usar .item() para converter valores NumPy escalares para tipos Python nativos
            similar_users_py = []
            for uid, score in similar_users:
                uid_int = int(uid.item() if hasattr(uid, 'item') else uid)
                score_float = float(score.item() if hasattr(score, 'item') else score)
                similar_users_py.append((uid_int, score_float))
            print(json.dumps(similar_users_py))
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(json.dumps({"error": error_msg}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
