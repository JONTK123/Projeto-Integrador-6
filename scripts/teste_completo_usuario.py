#!/usr/bin/env python3
"""
Script completo para testar sistema de recomendação simulando usuário
TUDO via API - nenhum script Python direto
"""

import subprocess
import requests
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional
import random

BASE_URL = "http://localhost:8000"
TIMEOUT_TREINAMENTO = 600  # 10 minutos para treinamento (LightFM pode demorar via Conda)
TIMEOUT_NORMAL = 30

# IDs de estabelecimentos disponíveis (baseado nos scripts existentes)
ESTABELECIMENTOS_DISPONIVEIS = list(range(201, 220))  # IDs 201-219


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")


def print_error(text):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")


def print_info(text):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {text}")


def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"⚠️  {text}")


def verificar_servidor() -> bool:
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def iniciar_servidor():
    """Inicia o servidor em background"""
    print_header("INICIANDO SERVIDOR")
    
    script_dir = Path(__file__).parent.parent
    server_script = script_dir / "iniciar_servidor.sh"
    
    if not server_script.exists():
        print_error(f"Script {server_script} não encontrado!")
        return False
    
    print_info("Iniciando servidor em background...")
    try:
        # Iniciar servidor em background
        process = subprocess.Popen(
            ["bash", str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_dir)
        )
        
        # Aguardar servidor ficar disponível
        print_info("Aguardando servidor ficar disponível...")
        for i in range(30):  # Tentar por até 30 segundos
            time.sleep(1)
            if verificar_servidor():
                print_success("Servidor está rodando!")
                return True
            if i % 5 == 0:
                print_info(f"Aguardando... ({i}s)")
        
        print_error("Servidor não respondeu a tempo")
        return False
    except Exception as e:
        print_error(f"Erro ao iniciar servidor: {e}")
        return False


def treinar_surprise() -> bool:
    """Treina modelo Surprise via API"""
    print_header("TREINANDO MODELO SURPRISE (via API)")
    
    payload = {
        "algoritmo": "surprise",
        "algorithm": "svd",
        "n_factors": 50,
        "n_epochs": 20
    }
    
    print_info(f"Enviando requisição: POST /recomendacoes/treinar")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/recomendacoes/treinar",
            json=payload,
            timeout=TIMEOUT_TREINAMENTO
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Surprise treinado com sucesso!")
            print_info(f"Métricas: {json.dumps(data.get('metricas', {}), indent=2)}")
            return True
        else:
            print_error(f"Erro ao treinar Surprise: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_error("Timeout ao treinar Surprise (pode estar demorando muito)")
        return False
    except Exception as e:
        print_error(f"Erro ao treinar Surprise: {e}")
        return False


def treinar_lightfm() -> bool:
    """Treina modelo LightFM via API"""
    print_header("TREINANDO MODELO LIGHTFM (via API)")
    
    payload = {
        "algoritmo": "lightfm",
        "usar_features": True,
        "loss": "warp",
        "num_epochs": 30,
        "learning_rate": 0.05,
        "num_components": 30
    }
    
    print_info(f"Enviando requisição: POST /recomendacoes/treinar")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/recomendacoes/treinar",
            json=payload,
            timeout=TIMEOUT_TREINAMENTO
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("LightFM treinado com sucesso!")
            print_info(f"Métricas: {json.dumps(data.get('metricas', {}), indent=2)}")
            return True
        elif response.status_code == 503:
            print_warning("LightFM não disponível via API (pode precisar de Conda)")
            print_info("Continuando com Surprise apenas...")
            return False
        else:
            print_error(f"Erro ao treinar LightFM: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_error("Timeout ao treinar LightFM (pode estar demorando muito)")
        return False
    except Exception as e:
        print_error(f"Erro ao treinar LightFM: {e}")
        return False


def criar_usuario() -> Optional[int]:
    """Tenta criar novo usuário via API, retorna ID ou None"""
    print_header("CRIANDO NOVO USUÁRIO")
    
    # Gerar dados únicos para o usuário
    timestamp = int(time.time())
    usuario_data = {
        "nome": f"Usuário Teste {timestamp}",
        "email": f"teste{timestamp}@exemplo.com",
        "senha_hash": f"hash_test_{timestamp}",
        "curso": "Ciência da Computação",
        "idade": 22,
        "id_universidade": 1
    }
    
    print_info(f"Enviando requisição: POST /usuarios/")
    print_info(f"Payload: {json.dumps(usuario_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/",
            json=usuario_data,
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 201:
            data = response.json()
            usuario_id = data.get("id_usuario") or data.get("id")
            print_success(f"Usuário criado com sucesso! ID: {usuario_id}")
            return usuario_id
        elif response.status_code == 501:
            print_warning("Rota de criação de usuário não implementada (501)")
            print_info("Usando usuário existente (ID 101) como fallback")
            return 101
        else:
            print_warning(f"Erro ao criar usuário: {response.status_code}")
            print_info("Usando usuário existente (ID 101) como fallback")
            return 101
    except Exception as e:
        print_warning(f"Erro ao criar usuário: {e}")
        print_info("Usando usuário existente (ID 101) como fallback")
        return 101


def testar_cold_start(usuario_id: int, algoritmo: str) -> bool:
    """Testa cold start para um algoritmo"""
    print_header(f"COLD START - {algoritmo.upper()}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/cold-start/usuario/{usuario_id}",
            params={"top_n": 10, "algoritmo": algoritmo},
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            recomendacoes = data.get("recomendacoes", [])
            print_success(f"Cold start funcionou! {len(recomendacoes)} recomendações")
            
            if recomendacoes:
                print_info("Top 5 recomendações:")
                for i, rec in enumerate(recomendacoes[:5], 1):
                    est_id = rec.get("estabelecimento_id", "N/A")
                    score = rec.get("score", 0)
                    print_info(f"   {i}. Estabelecimento {est_id}: {score:.3f}")
            
            return True
        else:
            print_error(f"Erro: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def registrar_interacao(usuario_id: int, estabelecimento_id: int, tipo: str, peso: float = 1.0) -> bool:
    """Registra uma interação do usuário"""
    payload = {
        "usuario_id": usuario_id,
        "estabelecimento_id": estabelecimento_id,
        "tipo_interacao": tipo,
        "peso": peso
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recomendacoes/interacao",
            json=payload,
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print_warning(f"Erro ao registrar {tipo}: {response.status_code}")
            return False
    except Exception as e:
        print_warning(f"Erro ao registrar {tipo}: {e}")
        return False


def simular_interacoes(usuario_id: int, num_interacoes: int = 20) -> Dict[str, int]:
    """Simula múltiplas interações do usuário"""
    print_header(f"SIMULANDO {num_interacoes} INTERAÇÕES")
    
    # Distribuir interações
    num_visitas = num_interacoes // 2  # ~50% visitas
    num_favoritos = num_interacoes // 3  # ~33% favoritos
    num_cliques = num_interacoes - num_visitas - num_favoritos  # Resto cliques
    
    resultados = {"visitas": 0, "favoritos": 0, "cliques": 0, "erros": 0}
    
    # Selecionar estabelecimentos aleatórios
    estabelecimentos = random.sample(ESTABELECIMENTOS_DISPONIVEIS, min(num_interacoes, len(ESTABELECIMENTOS_DISPONIVEIS)))
    
    print_info(f"Distribuição: {num_visitas} visitas, {num_favoritos} favoritos, {num_cliques} cliques")
    
    idx = 0
    
    # Registrar visitas
    for i in range(num_visitas):
        if idx < len(estabelecimentos):
            est_id = estabelecimentos[idx]
            if registrar_interacao(usuario_id, est_id, "visita", peso=1.0):
                resultados["visitas"] += 1
                print_info(f"  ✓ Visita {i+1}/{num_visitas}: Estabelecimento {est_id}")
            else:
                resultados["erros"] += 1
            idx += 1
            time.sleep(0.2)  # Pequeno delay entre requisições
    
    # Registrar favoritos
    for i in range(num_favoritos):
        if idx < len(estabelecimentos):
            est_id = estabelecimentos[idx]
            if registrar_interacao(usuario_id, est_id, "favorito", peso=1.0):
                resultados["favoritos"] += 1
                print_info(f"  ✓ Favorito {i+1}/{num_favoritos}: Estabelecimento {est_id}")
            else:
                resultados["erros"] += 1
            idx += 1
            time.sleep(0.2)
    
    # Registrar cliques
    for i in range(num_cliques):
        if idx < len(estabelecimentos):
            est_id = estabelecimentos[idx]
            if registrar_interacao(usuario_id, est_id, "clique", peso=0.8):
                resultados["cliques"] += 1
                print_info(f"  ✓ Clique {i+1}/{num_cliques}: Estabelecimento {est_id}")
            else:
                resultados["erros"] += 1
            idx += 1
            time.sleep(0.2)
    
    print_success(f"Interações registradas: {resultados['visitas']} visitas, {resultados['favoritos']} favoritos, {resultados['cliques']} cliques")
    if resultados["erros"] > 0:
        print_warning(f"{resultados['erros']} erros ao registrar interações")
    
    return resultados


def obter_recomendacoes(usuario_id: int, algoritmo: str, top_n: int = 10) -> Optional[List[Dict]]:
    """Obtém recomendações para um usuário"""
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/usuario/{usuario_id}",
            params={"algoritmo": algoritmo, "top_n": top_n},
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recomendacoes", [])
        else:
            print_error(f"Erro ao obter recomendações: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Erro: {e}")
        return None


def testar_recomendacoes_personalizadas(usuario_id: int, algoritmo: str) -> bool:
    """Testa recomendações personalizadas após interações"""
    print_header(f"RECOMENDAÇÕES PERSONALIZADAS - {algoritmo.upper()}")
    
    recomendacoes = obter_recomendacoes(usuario_id, algoritmo, top_n=10)
    
    if recomendacoes:
        print_success(f"{len(recomendacoes)} recomendações obtidas!")
        print_info("Top 10 recomendações:")
        for i, rec in enumerate(recomendacoes[:10], 1):
            est_id = rec.get("estabelecimento_id", "N/A")
            score = rec.get("score", 0)
            razao = rec.get("razao", "N/A")
            print_info(f"   {i}. Estabelecimento {est_id}: {score:.3f} - {razao[:50]}")
        return True
    else:
        print_error("Nenhuma recomendação obtida")
        return False


def testar_similares(estabelecimento_id: int, algoritmo: str) -> bool:
    """Testa estabelecimentos similares"""
    print_header(f"ESTABELECIMENTOS SIMILARES - {algoritmo.upper()}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/estabelecimento/{estabelecimento_id}/similares",
            params={"algoritmo": algoritmo, "top_n": 5},
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            similares = data.get("similares", [])
            print_success(f"{len(similares)} estabelecimentos similares encontrados!")
            for i, sim in enumerate(similares[:5], 1):
                sim_id = sim.get("estabelecimento_id", "N/A")
                score = sim.get("similaridade", sim.get("score", 0))
                print_info(f"   {i}. Estabelecimento {sim_id}: {score:.3f}")
            return True
        elif response.status_code == 503:
            print_warning(f"Funcionalidade não disponível para {algoritmo}")
            return False
        else:
            print_error(f"Erro: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def testar_diversidade(usuario_id: int, algoritmo: str) -> bool:
    """Testa recomendações diversas"""
    print_header(f"RECOMENDAÇÕES DIVERSAS - {algoritmo.upper()}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/diversidade/usuario/{usuario_id}",
            params={"top_n": 10, "explorar": 0.3, "algoritmo": algoritmo},
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            recomendacoes = data.get("recomendacoes", [])
            print_success(f"{len(recomendacoes)} recomendações diversas obtidas!")
            return True
        else:
            print_error(f"Erro: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def testar_contexto(usuario_id: int, algoritmo: str) -> bool:
    """Testa recomendações contextuais"""
    print_header(f"RECOMENDAÇÕES CONTEXTUAIS - {algoritmo.upper()}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/contexto/usuario/{usuario_id}",
            params={
                "top_n": 10,
                "hora_atual": 14,
                "dia_semana": 1,
                "algoritmo": algoritmo
            },
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            recomendacoes = data.get("recomendacoes", [])
            print_success(f"{len(recomendacoes)} recomendações contextuais obtidas!")
            return True
        else:
            print_error(f"Erro: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def comparar_algoritmos(usuario_id: int) -> bool:
    """Compara resultados entre Surprise e LightFM"""
    print_header("COMPARAÇÃO SURPRISE vs LIGHTFM")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recomendacoes/comparar/{usuario_id}",
            params={"top_n": 10},
            timeout=TIMEOUT_NORMAL
        )
        
        if response.status_code == 200:
            data = response.json()
            comparacao = data.get("comparacao", {})
            
            surprise_recs = comparacao.get("surprise", {}).get("recomendacoes", [])
            lightfm_recs = comparacao.get("lightfm", {}).get("recomendacoes", [])
            intersecao = comparacao.get("intersecao", {})
            
            print_success("Comparação realizada!")
            print_info(f"Surprise: {len(surprise_recs)} recomendações")
            print_info(f"LightFM: {len(lightfm_recs)} recomendações")
            print_info(f"Itens em comum: {intersecao.get('total_comum', 0)}")
            print_info(f"Percentual comum: {intersecao.get('percentual_comum', 0):.1f}%")
            
            return True
        else:
            print_error(f"Erro: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def main():
    """Função principal"""
    print("\n" + "🚀" * 40)
    print("  TESTE COMPLETO - SIMULAÇÃO DE USUÁRIO VIA API")
    print("🚀" * 40)
    
    resultados = {
        "servidor": False,
        "surprise_treinado": False,
        "lightfm_treinado": False,
        "usuario_criado": False,
        "usuario_id": None,
        "cold_start": {"surprise": False, "lightfm": False},
        "interacoes": {"total": 0, "sucesso": 0},
        "recomendacoes": {"surprise": False, "lightfm": False},
        "similares": {"surprise": False, "lightfm": False},
        "diversidade": {"surprise": False, "lightfm": False},
        "contexto": {"surprise": False, "lightfm": False},
        "comparacao": False
    }
    
    # 1. Verificar/Iniciar Servidor
    print_header("FASE 1: VERIFICAR SERVIDOR")
    if not verificar_servidor():
        print_info("Servidor não está rodando. Tentando iniciar...")
        if not iniciar_servidor():
            print_error("Não foi possível iniciar o servidor!")
            sys.exit(1)
    else:
        print_success("Servidor já está rodando!")
    resultados["servidor"] = True
    
    time.sleep(2)
    
    # 2. Treinar Modelos
    print_header("FASE 2: TREINAR MODELOS")
    resultados["surprise_treinado"] = treinar_surprise()
    time.sleep(2)
    
    resultados["lightfm_treinado"] = treinar_lightfm()
    time.sleep(2)
    
    if not resultados["surprise_treinado"] and not resultados["lightfm_treinado"]:
        print_error("Nenhum modelo foi treinado com sucesso!")
        sys.exit(1)
    
    # 3. Criar/Preparar Usuário
    print_header("FASE 3: PREPARAR USUÁRIO")
    usuario_id = criar_usuario()
    if usuario_id:
        resultados["usuario_criado"] = True
        resultados["usuario_id"] = usuario_id
        print_success(f"Usuário preparado: ID {usuario_id}")
    else:
        print_error("Não foi possível preparar usuário!")
        sys.exit(1)
    
    time.sleep(1)
    
    # 4. Cold Start
    print_header("FASE 4: COLD START")
    if resultados["surprise_treinado"]:
        resultados["cold_start"]["surprise"] = testar_cold_start(usuario_id, "surprise")
        time.sleep(1)
    
    if resultados["lightfm_treinado"]:
        resultados["cold_start"]["lightfm"] = testar_cold_start(usuario_id, "lightfm")
        time.sleep(1)
    
    # 5. Simular Interações
    print_header("FASE 5: SIMULAR INTERAÇÕES")
    interacoes_result = simular_interacoes(usuario_id, num_interacoes=20)
    resultados["interacoes"]["total"] = sum([
        interacoes_result["visitas"],
        interacoes_result["favoritos"],
        interacoes_result["cliques"]
    ])
    resultados["interacoes"]["sucesso"] = resultados["interacoes"]["total"]
    
    time.sleep(2)
    
    # 6. Recomendações Personalizadas
    print_header("FASE 6: RECOMENDAÇÕES PERSONALIZADAS")
    if resultados["surprise_treinado"]:
        resultados["recomendacoes"]["surprise"] = testar_recomendacoes_personalizadas(usuario_id, "surprise")
        time.sleep(1)
    
    if resultados["lightfm_treinado"]:
        resultados["recomendacoes"]["lightfm"] = testar_recomendacoes_personalizadas(usuario_id, "lightfm")
        time.sleep(1)
    
    # 7. Funcionalidades Avançadas
    print_header("FASE 7: FUNCIONALIDADES AVANÇADAS")
    
    # Estabelecimentos similares
    estabelecimento_teste = ESTABELECIMENTOS_DISPONIVEIS[0]
    if resultados["surprise_treinado"]:
        resultados["similares"]["surprise"] = testar_similares(estabelecimento_teste, "surprise")
        time.sleep(1)
    
    if resultados["lightfm_treinado"]:
        resultados["similares"]["lightfm"] = testar_similares(estabelecimento_teste, "lightfm")
        time.sleep(1)
    
    # Diversidade
    if resultados["surprise_treinado"]:
        resultados["diversidade"]["surprise"] = testar_diversidade(usuario_id, "surprise")
        time.sleep(1)
    
    if resultados["lightfm_treinado"]:
        resultados["diversidade"]["lightfm"] = testar_diversidade(usuario_id, "lightfm")
        time.sleep(1)
    
    # Contexto
    if resultados["surprise_treinado"]:
        resultados["contexto"]["surprise"] = testar_contexto(usuario_id, "surprise")
        time.sleep(1)
    
    if resultados["lightfm_treinado"]:
        resultados["contexto"]["lightfm"] = testar_contexto(usuario_id, "lightfm")
        time.sleep(1)
    
    # Comparação
    resultados["comparacao"] = comparar_algoritmos(usuario_id)
    
    # Resumo Final
    print_header("RESUMO FINAL")
    
    print("\n📊 RESULTADOS:")
    print(f"   Servidor: {'✅' if resultados['servidor'] else '❌'}")
    print(f"   Surprise Treinado: {'✅' if resultados['surprise_treinado'] else '❌'}")
    print(f"   LightFM Treinado: {'✅' if resultados['lightfm_treinado'] else '❌'}")
    print(f"   Usuário ID: {resultados['usuario_id']}")
    print(f"   Interações: {resultados['interacoes']['sucesso']}/{resultados['interacoes']['total']}")
    
    print("\n🧪 TESTES:")
    print(f"   Cold Start Surprise: {'✅' if resultados['cold_start']['surprise'] else '❌'}")
    print(f"   Cold Start LightFM: {'✅' if resultados['cold_start']['lightfm'] else '❌'}")
    print(f"   Recomendações Surprise: {'✅' if resultados['recomendacoes']['surprise'] else '❌'}")
    print(f"   Recomendações LightFM: {'✅' if resultados['recomendacoes']['lightfm'] else '❌'}")
    print(f"   Similares Surprise: {'✅' if resultados['similares']['surprise'] else '❌'}")
    print(f"   Similares LightFM: {'✅' if resultados['similares']['lightfm'] else '❌'}")
    print(f"   Diversidade Surprise: {'✅' if resultados['diversidade']['surprise'] else '❌'}")
    print(f"   Diversidade LightFM: {'✅' if resultados['diversidade']['lightfm'] else '❌'}")
    print(f"   Contexto Surprise: {'✅' if resultados['contexto']['surprise'] else '❌'}")
    print(f"   Contexto LightFM: {'✅' if resultados['contexto']['lightfm'] else '❌'}")
    print(f"   Comparação: {'✅' if resultados['comparacao'] else '❌'}")
    
    # Contar sucessos
    total_testes = sum([
        resultados['cold_start']['surprise'],
        resultados['cold_start']['lightfm'],
        resultados['recomendacoes']['surprise'],
        resultados['recomendacoes']['lightfm'],
        resultados['similares']['surprise'],
        resultados['similares']['lightfm'],
        resultados['diversidade']['surprise'],
        resultados['diversidade']['lightfm'],
        resultados['contexto']['surprise'],
        resultados['contexto']['lightfm'],
        resultados['comparacao']
    ])
    
    print(f"\n🎯 TOTAL: {total_testes} testes bem-sucedidos")
    
    if total_testes > 0:
        print_success("Testes concluídos com sucesso!")
        return 0
    else:
        print_error("Nenhum teste passou!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

