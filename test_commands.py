#!/usr/bin/env python3
"""
Teste local do bot para verificar os comandos
"""
import os
import sys
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
    format_multiple_normativos_message
)

def test_commands():
    """Testa todos os comandos do bot"""
    print("🤖 Testando comandos do bot...")
    
    # Teste 1: ultimo
    print("\n1️⃣ Testando comando 'ultimo':")
    try:
        normativo = get_ultimo_normativo()
        if normativo:
            msg = format_normativo_message(normativo)
            print("✅ Comando 'ultimo' funcionando:")
            print(msg[:200] + "..." if len(msg) > 200 else msg)
        else:
            print("❌ Comando 'ultimo' não retornou resultado")
    except Exception as e:
        print(f"❌ Erro no comando 'ultimo': {e}")
    
    # Teste 2: hoje
    print("\n2️⃣ Testando comando 'hoje':")
    try:
        normativos = get_normativos_hoje()
        msg = format_multiple_normativos_message(normativos, "Hoje")
        print("✅ Comando 'hoje' funcionando:")
        print(msg[:200] + "..." if len(msg) > 200 else msg)
    except Exception as e:
        print(f"❌ Erro no comando 'hoje': {e}")
    
    # Teste 3: ontem
    print("\n3️⃣ Testando comando 'ontem':")
    try:
        normativos = get_normativos_ontem()
        msg = format_multiple_normativos_message(normativos, "Ontem")
        print("✅ Comando 'ontem' funcionando:")
        print(msg[:200] + "..." if len(msg) > 200 else msg)
    except Exception as e:
        print(f"❌ Erro no comando 'ontem': {e}")
    
    # Teste 4: semanal
    print("\n4️⃣ Testando comando 'semanal':")
    try:
        normativos = get_normativos_semanal()
        msg = format_multiple_normativos_message(normativos, "Esta Semana")
        print("✅ Comando 'semanal' funcionando:")
        print(msg[:200] + "..." if len(msg) > 200 else msg)
    except Exception as e:
        print(f"❌ Erro no comando 'semanal': {e}")

if __name__ == "__main__":
    test_commands()
