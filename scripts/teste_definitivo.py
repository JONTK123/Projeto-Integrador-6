#!/usr/bin/env python3
"""
TESTE DEFINITIVO - Todas as Rotas e Modelos
Executa testes completos de todas as funcionalidades
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def testar_rota(nome, metodo, url, params=None, json_data=None, esperado=200):
    """Testa uma rota e retorna resultado"""
    try:
        if metodo == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif metodo == "POST":
            response = requests.post(url, json=json_data, timeout=30)
        else:
            return False, f"Método {metodo} não suportado"
        
        if response.status_code == esperado:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "🎯" * 40)
    print("  TESTE DEFINITIVO - TODAS AS ROTAS E MODELOS")
    print("🎯" * 40)
    print(f"\n⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # 1. Health Check
    print_header("1. HEALTH CHECK")
    sucesso, dados = testar_rota("Health Check", "GET", f"{BASE_URL}/")
    if sucesso:
        print_success("API está online!")
        print(f"   Status: {dados.get('status')}")
        print(f"   Versão: {dados.get('version')}")
        resultados['health'] = True
    else:
        print_error(f"API offline: {dados}")
        resultados['health'] = False
        print_error("Servidor não está rodando! Inicie com: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # 2. Treinar Surprise
    print_header("2. TREINAR MODELO SURPRISE")
    sucesso, dados = testar_rota(
        "Treinar Surprise",
        "POST",
        f"{BASE_URL}/recomendacoes/treinar",
        json_data={"algoritmo": "surprise", "algorithm": "svd", "n_factors": 50, "n_epochs": 20}
    )
    if sucesso:
        print_success("Surprise treinado com sucesso!")
        print(f"   RMSE: {dados.get('metricas', {}).get('rmse', 'N/A'):.3f}")
        print(f"   MAE: {dados.get('metricas', {}).get('mae', 'N/A'):.3f}")
        resultados['surprise_treinado'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['surprise_treinado'] = False
    
    # 3. Recomendações Surprise
    print_header("3. RECOMENDAÇÕES - SURPRISE (Usuário 101)")
    sucesso, dados = testar_rota(
        "Recomendações Surprise",
        "GET",
        f"{BASE_URL}/recomendacoes/usuario/101",
        params={"algoritmo": "surprise", "top_n": 5}
    )
    if sucesso:
        print_success(f"Recomendações obtidas: {len(dados.get('recomendacoes', []))} itens")
        for i, rec in enumerate(dados.get('recomendacoes', [])[:5], 1):
            print(f"   {i}. Estabelecimento {rec['estabelecimento_id']}: {rec['score']:.3f}")
        resultados['recomendacoes_surprise'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['recomendacoes_surprise'] = False
    
    # 4. Estabelecimentos Similares
    print_header("4. ESTABELECIMENTOS SIMILARES (ID 201)")
    sucesso, dados = testar_rota(
        "Similares",
        "GET",
        f"{BASE_URL}/recomendacoes/estabelecimento/201/similares",
        params={"algoritmo": "surprise", "top_n": 5}
    )
    if sucesso:
        print_success(f"Similares encontrados: {len(dados.get('similares', []))}")
        for i, sim in enumerate(dados.get('similares', [])[:5], 1):
            sim_id = sim.get('estabelecimento_id', 'N/A')
            sim_score = sim.get('similaridade', sim.get('score', 0))
            print(f"   {i}. ID {sim_id}: {sim_score:.3f}")
        resultados['similares'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['similares'] = False
    
    # 5. Registrar Interação
    print_header("5. REGISTRAR INTERAÇÃO")
    sucesso, dados = testar_rota(
        "Registrar Interação",
        "POST",
        f"{BASE_URL}/recomendacoes/interacao",
        json_data={"usuario_id": 101, "estabelecimento_id": 205, "tipo_interacao": "favorito", "score": 5}
    )
    if sucesso:
        print_success("Interação registrada!")
        print(f"   Usuário: {dados.get('usuario_id')}")
        print(f"   Estabelecimento: {dados.get('estabelecimento_id')}")
        print(f"   Score: {dados.get('score')}")
        resultados['interacao'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['interacao'] = False
    
    # 6. Cold Start Usuário
    print_header("6. COLD START - USUÁRIO")
    sucesso, dados = testar_rota(
        "Cold Start Usuário",
        "GET",
        f"{BASE_URL}/recomendacoes/cold-start/usuario/101",
        params={"algoritmo": "surprise", "top_n": 5}
    )
    if sucesso:
        print_success(f"Recomendações cold start: {len(dados.get('recomendacoes', []))} itens")
        resultados['cold_start_usuario'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['cold_start_usuario'] = False
    
    # 7. Cold Start Estabelecimento
    print_header("7. COLD START - ESTABELECIMENTO")
    sucesso, dados = testar_rota(
        "Cold Start Estabelecimento",
        "GET",
        f"{BASE_URL}/recomendacoes/cold-start/estabelecimento/201"
    )
    if sucesso:
        print_success("Status do estabelecimento obtido!")
        print(f"   Status: {dados.get('status')}")
        print(f"   Features: {dados.get('features_count')}")
        print(f"   Interações: {dados.get('interacoes_count')}")
        resultados['cold_start_estabelecimento'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['cold_start_estabelecimento'] = False
    
    # 8. Recomendações Diversas
    print_header("8. RECOMENDAÇÕES DIVERSAS")
    sucesso, dados = testar_rota(
        "Recomendações Diversas",
        "GET",
        f"{BASE_URL}/recomendacoes/diversidade/usuario/101",
        params={"top_n": 5, "explorar": 0.3, "algoritmo": "surprise"}
    )
    if sucesso:
        print_success(f"Recomendações diversas: {len(dados.get('recomendacoes', []))} itens")
        print(f"   Taxa de exploração: {dados.get('explorar', 0)}")
        resultados['diversas'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['diversas'] = False
    
    # 9. Recomendações Contextuais
    print_header("9. RECOMENDAÇÕES CONTEXTUAIS")
    sucesso, dados = testar_rota(
        "Recomendações Contextuais",
        "GET",
        f"{BASE_URL}/recomendacoes/contexto/usuario/101",
        params={"top_n": 5, "hora_atual": 14, "dia_semana": 1, "algoritmo": "surprise"}
    )
    if sucesso:
        print_success(f"Recomendações contextuais: {len(dados.get('recomendacoes', []))} itens")
        contexto = dados.get('contexto', {})
        print(f"   Hora: {contexto.get('hora_atual')}")
        print(f"   Dia: {contexto.get('dia_semana')}")
        resultados['contextuais'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['contextuais'] = False
    
    # 10. Comparar Algoritmos
    print_header("10. COMPARAR ALGORITMOS")
    sucesso, dados = testar_rota(
        "Comparar Algoritmos",
        "GET",
        f"{BASE_URL}/recomendacoes/comparar/101",
        params={"top_n": 5}
    )
    if sucesso:
        print_success("Comparação realizada!")
        comparacao = dados.get('comparacao', {})
        print(f"   Algoritmos comparados: {len(comparacao)}")
        resultados['comparar'] = True
    else:
        print_error(f"Erro: {dados}")
        resultados['comparar'] = False
    
    # 11. Verificar Modelos
    print_header("11. STATUS DOS MODELOS")
    import os
    from pathlib import Path
    
    models_dir = Path("models")
    surprise_model = models_dir / "surprise_model.pkl"
    lightfm_model = models_dir / "lightfm_model.pkl"
    
    if surprise_model.exists():
        size = surprise_model.stat().st_size / 1024
        print_success(f"Surprise: {size:.1f} KB")
        resultados['modelo_surprise'] = True
    else:
        print_error("Surprise: Modelo não encontrado")
        resultados['modelo_surprise'] = False
    
    if lightfm_model.exists():
        size = lightfm_model.stat().st_size / 1024
        print_success(f"LightFM: {size:.1f} KB")
        resultados['modelo_lightfm'] = True
    else:
        print_info("LightFM: Modelo não encontrado (pode não estar instalado)")
        resultados['modelo_lightfm'] = False
    
    # Resumo Final
    print_header("RESUMO FINAL DO TESTE DEFINITIVO")
    
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v)
    
    print(f"\n📊 Resultados:")
    print(f"   ✅ Sucessos: {sucesso}/{total}")
    print(f"   ❌ Falhas: {total - sucesso}/{total}")
    print(f"   📈 Taxa de sucesso: {(sucesso/total)*100:.1f}%")
    
    print("\n📋 Detalhes:")
    for nome, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"   {status} {nome}")
    
    if sucesso == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema 100% funcional!")
    elif sucesso >= total * 0.8:
        print(f"\n✅ Sistema funcional! {sucesso}/{total} testes passaram.")
    else:
        print(f"\n⚠️  Sistema com problemas. {total - sucesso} teste(s) falharam.")
    
    print(f"\n⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if sucesso == total else 1

if __name__ == "__main__":
    sys.exit(main())

