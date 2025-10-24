#!/usr/bin/env python3
"""
Teste do cron robusto
"""
import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração do fuso horário brasileiro
BR_TZ = pytz.timezone('America/Sao_Paulo')

async def test_robust_cron():
    """Testa o cron robusto"""
    print("🧪 TESTE DO CRON ROBUSTO")
    print("=" * 50)
    
    try:
        from sender import run_cron
        
        print(f"🕒 Iniciando teste do cron robusto...")
        print(f"📅 Horário: {datetime.now(BR_TZ).strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Executa por 1 minuto para testar
        print(f"⏰ Executando cron por 1 minuto para teste...")
        
        # Cria task para executar cron
        cron_task = asyncio.create_task(run_cron())
        
        # Aguarda 1 minuto
        await asyncio.sleep(60)
        
        # Cancela o cron
        cron_task.cancel()
        
        print(f"✅ Teste concluído")
        
        # Verifica logs
        try:
            import json
            with open("cron_executions.json", 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            print(f"\n📊 Logs após teste: {len(logs)}")
            
            # Mostra últimos 3 logs
            recent_logs = logs[-3:]
            for i, log in enumerate(recent_logs, 1):
                timestamp = datetime.fromisoformat(log['timestamp'])
                status = log.get('status', 'unknown')
                print(f"   {i}. {timestamp.strftime('%d/%m %H:%M:%S')} - {status}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar logs: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESTE DO CRON ROBUSTO")
    print("=" * 60)
    
    success = asyncio.run(test_robust_cron())
    
    if success:
        print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        print("🎯 Próximos passos:")
        print("1. Fazer commit e push")
        print("2. Deploy no Railway")
        print("3. Monitorar execuções")
    else:
        print(f"\n❌ TESTE FALHOU")
        print("=" * 30)
        print("🔍 Verificar configuração")
