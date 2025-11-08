#!/usr/bin/env python3
"""
Script para treinar LightFM via Conda
Recebe parâmetros via argumentos de linha de comando e retorna métricas em JSON
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
    """Treina LightFM com parâmetros fornecidos"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Uso: python lightfm_train.py <json_params>"}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parsear parâmetros JSON
        params_json = sys.argv[1]
        params = json.loads(params_json)
        
        # Extrair parâmetros
        loss = params.get("loss", "warp")
        use_features = params.get("usar_features", True)
        num_epochs = params.get("num_epochs", 30)
        learning_rate = params.get("learning_rate", 0.05)
        num_components = params.get("num_components", 30)
        
        # Criar serviço
        service = LightFMService()
        
        # Obter sessão do banco
        db = SessionLocal()
        
        try:
            # Treinar modelo
            metrics = service.train(
                db=db,
                loss=loss,
                use_features=use_features,
                num_epochs=num_epochs,
                learning_rate=learning_rate,
                num_components=num_components
            )
            
            # Salvar modelo
            service.save_model()
            
            # Retornar métricas em JSON
            result = {
                "success": True,
                "message": "Modelo LightFM treinado com sucesso",
                "metricas": metrics
            }
            print(json.dumps(result))
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            print(json.dumps(error_result), file=sys.stderr)
            sys.exit(1)
        finally:
            db.close()
            
    except json.JSONDecodeError as e:
        error_result = {
            "success": False,
            "error": f"Erro ao parsear JSON: {str(e)}"
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

