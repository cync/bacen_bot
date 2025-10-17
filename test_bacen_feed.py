#!/usr/bin/env python3
"""
Script de teste para verificar a busca de normativos do BACEN
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bacen_feed import (
    get_ultimo_normativo, 
    get_normativos_hoje, 
    get_normativos_ontem, 
    get_normativos_semanal,
    format_normativo_message,
    format_multiple_normativos_message,
    parse_bacen_feed
)

def test_feed_parsing():
    """Testa o parsing do feed RSS"""
    print("🔍 Testando parsing do feed RSS...")
    try:
        normativos = parse_bacen_feed()
        print(f"✅ Feed parseado com sucesso! Encontrados {len(normativos)} normativos")
        
        if normativos:
            print("\n📋 Primeiros 3 normativos:")
            for i, normativo in enumerate(normativos[:3], 1):
                print(f"{i}. {normativo.title}")
                print(f"   Data: {normativo.published}")
                print(f"   Link: {normativo.link}")
                print()
        
        return normativos
    except Exception as e:
        print(f"❌ Erro ao parsear feed: {e}")
        return []

def test_ultimo_normativo():
    """Testa a busca do último normativo"""
    print("\n🔍 Testando busca do último normativo...")
    try:
        normativo = get_ultimo_normativo()
        if normativo:
            print("✅ Último normativo encontrado:")
            print(format_normativo_message(normativo))
        else:
            print("❌ Nenhum normativo encontrado")
    except Exception as e:
        print(f"❌ Erro ao buscar último normativo: {e}")

def test_normativos_hoje():
    """Testa a busca de normativos de hoje"""
    print("\n🔍 Testando busca de normativos de hoje...")
    try:
        normativos = get_normativos_hoje()
        print(f"✅ Encontrados {len(normativos)} normativos de hoje")
        if normativos:
            msg = format_multiple_normativos_message(normativos, "Hoje")
            print(msg[:500] + "..." if len(msg) > 500 else msg)
    except Exception as e:
        print(f"❌ Erro ao buscar normativos de hoje: {e}")

def test_normativos_ontem():
    """Testa a busca de normativos de ontem"""
    print("\n🔍 Testando busca de normativos de ontem...")
    try:
        normativos = get_normativos_ontem()
        print(f"✅ Encontrados {len(normativos)} normativos de ontem")
        if normativos:
            msg = format_multiple_normativos_message(normativos, "Ontem")
            print(msg[:500] + "..." if len(msg) > 500 else msg)
    except Exception as e:
        print(f"❌ Erro ao buscar normativos de ontem: {e}")

def test_normativos_semanal():
    """Testa a busca de normativos desta semana"""
    print("\n🔍 Testando busca de normativos desta semana...")
    try:
        normativos = get_normativos_semanal()
        print(f"✅ Encontrados {len(normativos)} normativos desta semana")
        if normativos:
            msg = format_multiple_normativos_message(normativos, "Esta Semana")
            print(msg[:500] + "..." if len(msg) > 500 else msg)
    except Exception as e:
        print(f"❌ Erro ao buscar normativos desta semana: {e}")

def main():
    """Executa todos os testes"""
    print("🧪 Testando funcionalidades de busca de normativos do BACEN")
    print("=" * 60)
    
    # Teste 1: Parsing do feed
    normativos = test_feed_parsing()
    
    if not normativos:
        print("\n❌ Não foi possível obter normativos do feed. Verifique:")
        print("1. Conexão com a internet")
        print("2. URL do feed RSS do BACEN")
        print("3. Formato do feed")
        return
    
    # Teste 2: Último normativo
    test_ultimo_normativo()
    
    # Teste 3: Normativos de hoje
    test_normativos_hoje()
    
    # Teste 4: Normativos de ontem
    test_normativos_ontem()
    
    # Teste 5: Normativos desta semana
    test_normativos_semanal()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
