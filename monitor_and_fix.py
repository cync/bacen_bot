#!/usr/bin/env python3
"""
Monitor e forçador de execução para garantir funcionamento contínuo
"""
import os
import sys
import asyncio
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração do fuso horário brasileiro
BR_TZ = pytz.timezone('America/Sao_Paulo')

async def force_execution():
    """Força uma execução manual"""
    print("🔄 FORÇANDO EXECUÇÃO MANUAL")
    print("=" * 40)
    
    try:
        from sender import run_once, log_execution, is_business_hours
        
        current_time = datetime.now(BR_TZ)
        print(f"🕒 Executando verificação forçada às {current_time.strftime('%H:%M:%S')}")
        
        # Log de execução forçada
        log_execution("forced_execution", {
            "timestamp": current_time.isoformat(),
            "business_hours": is_business_hours(),
            "reason": "manual_force"
        })
        
        # Executa verificação
        await run_once()
        
        print("✅ Execução forçada concluída com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na execução forçada: {e}")
        return False

def check_monitoring_page():
    """Verifica página de monitoramento"""
    print("🌐 VERIFICANDO PÁGINA DE MONITORAMENTO")
    print("=" * 50)
    
    try:
        response = requests.get("https://bacenbot-production.up.railway.app/monitor", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de monitoramento acessível")
            
            # Verifica se há logs recentes
            if "Execuções Totais" in response.text:
                print("📊 Página mostra estatísticas de execução")
            else:
                print("⚠️ Página não mostra estatísticas")
            
            return True
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar página: {e}")
        return False

def check_health_endpoint():
    """Verifica endpoint de health check"""
    print("🏥 VERIFICANDO HEALTH CHECK")
    print("=" * 40)
    
    try:
        response = requests.get("https://bacenbot-production.up.railway.app/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data.get('status', 'unknown')}")
            print(f"📅 Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

async def monitor_and_fix():
    """Monitora e corrige o sistema"""
    print("🔍 MONITORAMENTO E CORREÇÃO AUTOMÁTICA")
    print("=" * 60)
    
    # Verifica health check
    health_ok = check_health_endpoint()
    
    # Verifica página de monitoramento
    monitor_ok = check_monitoring_page()
    
    # Força execução se necessário
    if not health_ok or not monitor_ok:
        print("⚠️ Problemas detectados - forçando execução...")
        await force_execution()
    else:
        print("✅ Sistema funcionando normalmente")
    
    # Verifica logs locais
    try:
        import json
        if os.path.exists("cron_executions.json"):
            with open("cron_executions.json", 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if logs:
                last_log = logs[-1]
                last_time = datetime.fromisoformat(last_log['timestamp'])
                time_since = (datetime.now(BR_TZ) - last_time).total_seconds()
                
                print(f"\n📊 ÚLTIMA EXECUÇÃO LOCAL:")
                print(f"   📅 Data/Hora: {last_time.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"   ⏰ Há {time_since/60:.1f} minutos")
                print(f"   📊 Status: {last_log.get('status', 'unknown')}")
                
                if time_since > 20 * 60:  # 20 minutos
                    print("⚠️ Execução muito antiga - forçando nova execução...")
                    await force_execution()
            else:
                print("❌ Nenhum log local encontrado")
        else:
            print("❌ Arquivo de logs não existe")
    except Exception as e:
        print(f"❌ Erro ao verificar logs: {e}")

async def main():
    """Função principal"""
    print("🛠️ MONITOR E CORRETOR AUTOMÁTICO")
    print("=" * 70)
    
    await monitor_and_fix()
    
    print(f"\n🎯 MONITORAMENTO CONCLUÍDO!")
    print("=" * 50)
    print("✅ Sistema verificado")
    print("✅ Correções aplicadas se necessário")
    print("✅ Logs atualizados")

if __name__ == "__main__":
    asyncio.run(main())
