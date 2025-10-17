#!/usr/bin/env python3
"""
Teste da nova funcionalidade de análise de temas e mini-resumos
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
    get_normativos_semanal,
    format_normativo_message,
    format_multiple_normativos_message
)

def test_topic_extraction():
    """Testa a extração de temas e mini-resumos"""
    print("🧪 Testando análise de temas e mini-resumos...")
    
    # Teste 1: Último normativo
    print("\n1️⃣ Testando último normativo:")
    try:
        normativo = get_ultimo_normativo()
        if normativo:
            print(f"✅ Tema extraído: {normativo.tema}")
            print(f"✅ Mini-resumo: {normativo.mini_resumo[:100]}...")
            print("\n📱 Formato da mensagem:")
            msg = format_normativo_message(normativo)
            print(msg[:300] + "..." if len(msg) > 300 else msg)
        else:
            print("❌ Nenhum normativo encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Normativos da semana
    print("\n2️⃣ Testando normativos da semana:")
    try:
        normativos = get_normativos_semanal()
        if normativos:
            print(f"✅ Encontrados {len(normativos)} normativos")
            print("\n📋 Temas encontrados:")
            temas = {}
            for normativo in normativos[:5]:  # Primeiros 5
                tema = normativo.tema
                temas[tema] = temas.get(tema, 0) + 1
                print(f"   • {tema}")
            
            print(f"\n📊 Resumo dos temas:")
            for tema, count in temas.items():
                print(f"   • {tema}: {count} normativo(s)")
        else:
            print("❌ Nenhum normativo encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_topic_extraction()
