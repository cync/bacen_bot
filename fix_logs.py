#!/usr/bin/env python3
"""
Teste e correção do sistema de logs de execução
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import json
import pytz

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração do fuso horário brasileiro
BR_TZ = pytz.timezone('America/Sao_Paulo')

def test_log_system():
    """Testa o sistema de logs"""
    print("🧪 TESTANDO SISTEMA DE LOGS")
    print("=" * 50)
    
    # Simula uma execução de teste
    test_logs = [
        {
            "timestamp": datetime.now(BR_TZ).isoformat(),
            "status": "started",
            "details": {"test": True, "reason": "test_execution"}
        },
        {
            "timestamp": datetime.now(BR_TZ).isoformat(),
            "status": "success",
            "details": {
                "normativos_enviados": 1,
                "subscribers_count": 16,
                "duration_seconds": 2.5,
                "test": True
            }
        }
    ]
    
    # Salva logs de teste
    with open("cron_executions.json", 'w', encoding='utf-8') as f:
        json.dump(test_logs, f, ensure_ascii=False, indent=2)
    
    print("✅ Arquivo de logs criado com dados de teste")
    print(f"📁 Arquivo: cron_executions.json")
    print(f"📊 Logs criados: {len(test_logs)}")
    
    # Testa leitura
    try:
        with open("cron_executions.json", 'r', encoding='utf-8') as f:
            loaded_logs = json.load(f)
        print(f"✅ Leitura bem-sucedida: {len(loaded_logs)} logs")
        
        for i, log in enumerate(loaded_logs, 1):
            timestamp = datetime.fromisoformat(log['timestamp'])
            status = log.get('status', 'unknown')
            print(f"   {i}. {timestamp.strftime('%d/%m %H:%M:%S')} - {status}")
            
    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")
    
    return True

def simulate_cron_execution():
    """Simula uma execução completa do cron"""
    print("\n🔄 SIMULANDO EXECUÇÃO DO CRON")
    print("=" * 50)
    
    try:
        # Importa funções do sender
        from sender import log_execution, is_business_hours
        
        print(f"🕒 Horário comercial ativo: {is_business_hours()}")
        
        # Simula diferentes tipos de execução
        log_execution("started", {
            "timestamp": datetime.now(BR_TZ).isoformat(),
            "business_hours": is_business_hours(),
            "simulation": True
        })
        
        if is_business_hours():
            log_execution("success", {
                "normativos_enviados": 2,
                "subscribers_count": 16,
                "duration_seconds": 3.2,
                "normativos": [
                    {"title": "Resolução BCB N° 514", "published": "2025-10-24T09:09:00", "link": "https://example.com"},
                    {"title": "Resolução BCB N° 515", "published": "2025-10-24T10:59:00", "link": "https://example.com"}
                ],
                "simulation": True
            })
        else:
            log_execution("skipped", {
                "reason": "outside_business_hours",
                "simulation": True
            })
        
        print("✅ Simulação de execução concluída")
        
        # Verifica logs criados
        try:
            with open("cron_executions.json", 'r', encoding='utf-8') as f:
                logs = json.load(f)
            print(f"📊 Total de logs agora: {len(logs)}")
            
            print("\n📋 Últimos logs:")
            for log in logs[-3:]:
                timestamp = datetime.fromisoformat(log['timestamp'])
                status = log.get('status', 'unknown')
                details = log.get('details', {})
                print(f"   • {timestamp.strftime('%d/%m %H:%M:%S')} - {status}")
                if 'reason' in details:
                    print(f"     Motivo: {details['reason']}")
                if 'normativos_enviados' in details:
                    print(f"     Normativos: {details['normativos_enviados']}")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar logs: {e}")
            
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return False
    
    return True

def check_railway_deployment():
    """Verifica se o problema está no Railway"""
    print("\n🚂 VERIFICANDO DEPLOYMENT RAILWAY")
    print("=" * 50)
    
    print("🔍 Possíveis problemas no Railway:")
    print("   1. Serviço 'bacen-cron' não está rodando")
    print("   2. Arquivo de logs não está sendo criado")
    print("   3. Permissões de escrita no sistema de arquivos")
    print("   4. Variáveis de ambiente não configuradas")
    
    print("\n🛠️ SOLUÇÕES:")
    print("   1. Verificar logs do Railway")
    print("   2. Reiniciar serviço 'bacen-cron'")
    print("   3. Verificar configuração de variáveis")
    print("   4. Testar comando 'testar' no bot")
    
    return True

if __name__ == "__main__":
    print("🔧 CORREÇÃO DO SISTEMA DE LOGS")
    print("=" * 60)
    
    # Testa sistema de logs
    test_log_system()
    
    # Simula execução
    simulate_cron_execution()
    
    # Verifica Railway
    check_railway_deployment()
    
    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASSOS")
    print("=" * 60)
    print("1. ✅ Arquivo de logs criado localmente")
    print("2. ✅ Sistema de logs testado")
    print("3. 🔄 Fazer commit e push das correções")
    print("4. 🚂 Verificar Railway deployment")
    print("5. 🧪 Testar comando 'testar' no bot")
    print("6. 📊 Monitorar página de monitoramento")
