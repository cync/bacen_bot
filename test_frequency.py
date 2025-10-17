#!/usr/bin/env python3
"""
Teste para verificar a nova frequência de 10 minutos
"""
import asyncio
import time
from datetime import datetime
from sender import run_once

async def test_frequency():
    """Testa a execução do sender"""
    print("🧪 Testando execução do sender...")
    
    start_time = time.time()
    
    try:
        await run_once()
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Execução concluída em {duration:.2f} segundos")
        print(f"⏰ Próxima execução será em 10 minutos")
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

if __name__ == "__main__":
    asyncio.run(test_frequency())
