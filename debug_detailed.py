#!/usr/bin/env python3
"""
Debug detalhado das datas
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
import pytz

def debug_detailed_dates():
    """Debug detalhado das datas"""
    print("🔍 Debug detalhado das datas...")
    
    # Data atual
    br_tz = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(br_tz)
    hoje = now_br.date()
    ontem = (now_br - timedelta(days=1)).date()
    
    print(f"📅 Data atual SP: {now_br}")
    print(f"📅 Hoje: {hoje}")
    print(f"📅 Ontem: {ontem}")
    
    normativos = parse_bacen_feed()
    
    print(f"\n📊 Analisando {len(normativos)} normativos:")
    
    for i, normativo in enumerate(normativos[:5], 1):
        print(f"\n{i}. {normativo.title}")
        print(f"   Data original: {normativo.published}")
        print(f"   Data SP: {normativo.published.astimezone(br_tz)}")
        print(f"   Data SP apenas: {normativo.published.astimezone(br_tz).date()}")
        print(f"   É hoje? {normativo.published.astimezone(br_tz).date() == hoje}")
        print(f"   É ontem? {normativo.published.astimezone(br_tz).date() == ontem}")

if __name__ == "__main__":
    debug_detailed_dates()
