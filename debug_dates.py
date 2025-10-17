#!/usr/bin/env python3
"""
Teste detalhado para debug das datas
"""
import sys
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bacen_feed import parse_bacen_feed

def debug_dates():
    """Debug das datas dos normativos"""
    print("🔍 Debug das datas dos normativos...")
    
    normativos = parse_bacen_feed()
    
    if not normativos:
        print("❌ Nenhum normativo encontrado")
        return
    
    print(f"📊 Total de normativos: {len(normativos)}")
    
    # Mostra as datas dos primeiros 5 normativos
    for i, normativo in enumerate(normativos[:5], 1):
        print(f"\n{i}. {normativo.title}")
        print(f"   Data original: {normativo.published}")
        print(f"   Data apenas: {normativo.published.date()}")
        print(f"   Ano: {normativo.published.year}")
        print(f"   Mês: {normativo.published.month}")
        print(f"   Dia: {normativo.published.day}")
    
    # Verifica data atual
    print(f"\n📅 Data atual:")
    print(f"   UTC: {datetime.now(timezone.utc)}")
    print(f"   UTC date: {datetime.now(timezone.utc).date()}")
    
    try:
        import pytz
        br_tz = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(br_tz)
        print(f"   SP: {now_br}")
        print(f"   SP date: {now_br.date()}")
    except ImportError:
        print("   pytz não disponível")

if __name__ == "__main__":
    debug_dates()
