#!/usr/bin/env python3
"""
Script Python para criar banco de dados no AWS RDS
Não precisa de psql instalado - usa SQLAlchemy
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Configurações do banco AWS RDS
DB_CONFIG = {
    'host': 'synapse-database.cbsymmi08a0x.sa-east-1.rds.amazonaws.com',
    'port': 5432,
    'user': 'filipemota',
    'password': 'filipemota',
    'database': 'postgres'  # Conecta ao banco padrão primeiro
}

# URL de conexão para o banco padrão (postgres)
CONNECTION_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Nome do banco a ser criado
TARGET_DB = 'lightfm_recommendations'

def verificar_conexao():
    """Verifica se consegue conectar ao RDS"""
    print("🔍 Verificando conexão com AWS RDS...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Porta: {DB_CONFIG['port']}")
    print(f"   Usuário: {DB_CONFIG['user']}")
    print()
    
    try:
        engine = create_engine(CONNECTION_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL!")
            print(f"   Versão: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def listar_bancos():
    """Lista todos os bancos de dados"""
    print("\n📋 Listando bancos de dados existentes...")
    try:
        engine = create_engine(CONNECTION_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"))
            bancos = [row[0] for row in result]
            print("   Bancos encontrados:")
            for banco in bancos:
                marker = "✅" if banco == TARGET_DB else "  "
                print(f"   {marker} {banco}")
            return bancos
    except Exception as e:
        print(f"❌ Erro ao listar bancos: {e}")
        return []

def verificar_banco_existe(bancos):
    """Verifica se o banco já existe"""
    return TARGET_DB in bancos

def criar_banco():
    """Cria o banco de dados"""
    print(f"\n🔨 Criando banco '{TARGET_DB}'...")
    
    try:
        engine = create_engine(CONNECTION_URL)
        # PostgreSQL não permite criar banco dentro de transação
        # Precisamos usar autocommit
        with engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Termina qualquer transação
            conn.execute(text(f"CREATE DATABASE {TARGET_DB};"))
            conn.execute(text("COMMIT"))
        
        print(f"✅ Banco '{TARGET_DB}' criado com sucesso!")
        return True
    except ProgrammingError as e:
        if "already exists" in str(e).lower():
            print(f"⚠️ Banco '{TARGET_DB}' já existe!")
            return True
        else:
            print(f"❌ Erro ao criar banco: {e}")
            return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 Criar Banco de Dados no AWS RDS")
    print("=" * 60)
    print()
    
    # 1. Verificar conexão
    if not verificar_conexao():
        print("\n❌ Não foi possível conectar ao banco.")
        print("   Verifique:")
        print("   - Credenciais estão corretas")
        print("   - Security Group permite conexão do seu IP")
        print("   - RDS está rodando")
        sys.exit(1)
    
    # 2. Listar bancos existentes
    bancos = listar_bancos()
    
    # 3. Verificar se já existe
    if verificar_banco_existe(bancos):
        print(f"\n✅ Banco '{TARGET_DB}' já existe!")
        print("   Não é necessário criar novamente.")
        sys.exit(0)
    
    # 4. Criar banco
    if criar_banco():
        print("\n" + "=" * 60)
        print("✅ SUCESSO!")
        print("=" * 60)
        print(f"\nBanco '{TARGET_DB}' criado com sucesso no AWS RDS!")
        print("\n📋 Próximos passos:")
        print("   1. Execute as migrações:")
        print("      alembic upgrade head")
        print("\n   2. Verifique o banco criado")
        print("\n   3. Inicie o servidor:")
        print("      uvicorn app.main:app --reload")
    else:
        print("\n❌ Falha ao criar banco.")
        sys.exit(1)

if __name__ == "__main__":
    main()

