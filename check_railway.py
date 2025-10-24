#!/usr/bin/env python3
"""
Monitor Railway Services - Verifica se os serviços estão rodando
"""
import requests
import json
from datetime import datetime

def check_railway_services():
    """Verifica o status dos serviços no Railway"""
    print("🚂 VERIFICANDO SERVIÇOS RAILWAY")
    print("=" * 50)
    
    services = [
        {
            "name": "bacen-reply-bot",
            "url": "https://bacenbot-production.up.railway.app/health",
            "port": 8000
        },
        {
            "name": "bacen-cron", 
            "url": "https://bacenbot-production.up.railway.app/monitor",
            "port": 8001
        }
    ]
    
    for service in services:
        print(f"\n🔍 Verificando {service['name']}:")
        try:
            response = requests.get(service['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {service['name']} - ONLINE")
                print(f"   📡 Status: {response.status_code}")
                print(f"   🌐 URL: {service['url']}")
                
                # Se for o monitor, mostra informações extras
                if service['name'] == 'bacen-cron':
                    if 'ATIVO' in response.text:
                        print("   🟢 Sistema ATIVO")
                    elif 'INATIVO' in response.text:
                        print("   🔴 Sistema INATIVO")
                    
                    if 'execuções' in response.text.lower():
                        print("   📊 Logs de execução disponíveis")
                        
            else:
                print(f"❌ {service['name']} - ERRO")
                print(f"   📡 Status: {response.status_code}")
                print(f"   🌐 URL: {service['url']}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {service['name']} - FALHA DE CONEXÃO")
            print(f"   🌐 URL: {service['url']}")
            print(f"   💥 Erro: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print("📋 RESUMO")
    print("=" * 50)
    
    # Verifica se ambos os serviços estão funcionando
    try:
        reply_response = requests.get(services[0]['url'], timeout=5)
        monitor_response = requests.get(services[1]['url'], timeout=5)
        
        if reply_response.status_code == 200 and monitor_response.status_code == 200:
            print("✅ AMBOS OS SERVIÇOS FUNCIONANDO!")
            print("🎯 Sistema pronto para:")
            print("   • Receber comandos do Telegram")
            print("   • Executar cron a cada 10 minutos")
            print("   • Enviar notificações automáticas")
        else:
            print("⚠️ PROBLEMAS DETECTADOS:")
            if reply_response.status_code != 200:
                print(f"   ❌ bacen-reply-bot: Status {reply_response.status_code}")
            if monitor_response.status_code != 200:
                print(f"   ❌ bacen-cron: Status {monitor_response.status_code}")
                
    except Exception as e:
        print(f"❌ ERRO AO VERIFICAR SERVIÇOS: {e}")
    
    print(f"\n🌐 LINKS ÚTEIS:")
    print(f"   • Health Check: https://bacenbot-production.up.railway.app/health")
    print(f"   • Monitor: https://bacenbot-production.up.railway.app/monitor")
    print(f"   • Bot Telegram: @bacen_bot")

if __name__ == "__main__":
    check_railway_services()
