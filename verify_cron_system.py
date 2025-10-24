#!/usr/bin/env python3
"""
Verificação completa do sistema bacen-cron
"""
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sender import is_business_hours, get_execution_logs, log_execution
from storage import get_store
from bacen_feed import get_normativos_hoje

def verify_bacen_cron_system():
    """Verifica se o sistema bacen-cron está funcionando corretamente"""
    print("🔍 VERIFICAÇÃO COMPLETA DO SISTEMA BACEN-CRON")
    print("=" * 60)
    
    # 1. Verificar horário atual
    print("1️⃣ VERIFICANDO HORÁRIO ATUAL:")
    current_time = datetime.now()
    business_hours_active = is_business_hours()
    
    print(f"📅 Data/Hora atual: {current_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🕒 Horário comercial (08:00-19:25): {'ATIVO' if business_hours_active else 'INATIVO'}")
    
    if business_hours_active:
        print("✅ Sistema deve estar executando a cada 10 minutos")
    else:
        print("⏰ Sistema fora do horário - não executará")
    
    # 2. Verificar logs de execução
    print(f"\n2️⃣ VERIFICANDO LOGS DE EXECUÇÃO:")
    logs = get_execution_logs()
    
    if logs:
        print(f"📊 Total de execuções registradas: {len(logs)}")
        
        # Últimas 5 execuções
        recent_logs = logs[-5:]
        print(f"\n📋 Últimas 5 execuções:")
        for i, log in enumerate(recent_logs, 1):
            timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            status = log.get('status', 'unknown')
            details = log.get('details', {})
            
            print(f"   {i}. {timestamp.strftime('%d/%m %H:%M:%S')} - {status.upper()}")
            if details:
                if 'normativos_enviados' in details:
                    print(f"      📄 Normativos enviados: {details['normativos_enviados']}")
                if 'subscribers_count' in details:
                    print(f"      👥 Inscritos: {details['subscribers_count']}")
                if 'reason' in details:
                    print(f"      💡 Motivo: {details['reason']}")
        
        # Verificar frequência
        if len(logs) >= 2:
            last_log = logs[-1]
            second_last_log = logs[-2]
            
            last_time = datetime.fromisoformat(last_log['timestamp'].replace('Z', '+00:00'))
            second_last_time = datetime.fromisoformat(second_last_log['timestamp'].replace('Z', '+00:00'))
            
            time_diff = (last_time - second_last_time).total_seconds() / 60
            print(f"\n⏱️ Intervalo entre últimas execuções: {time_diff:.1f} minutos")
            
            if 8 <= time_diff <= 12:
                print("✅ Intervalo correto (8-12 minutos)")
            else:
                print(f"⚠️ Intervalo irregular (esperado: ~10 minutos)")
    else:
        print("❌ Nenhum log de execução encontrado")
        print("💡 Sistema pode não estar funcionando")
    
    # 3. Verificar normativos de hoje
    print(f"\n3️⃣ VERIFICANDO NORMATIVOS DE HOJE:")
    try:
        normativos_hoje = get_normativos_hoje()
        print(f"📄 Normativos encontrados hoje: {len(normativos_hoje)}")
        
        if normativos_hoje:
            print("📋 Normativos de hoje:")
            for i, normativo in enumerate(normativos_hoje, 1):
                data_str = normativo.published.strftime("%d/%m/%Y %H:%M")
                print(f"   {i}. {normativo.title}")
                print(f"      📅 Data: {data_str}")
                print(f"      🔗 Link: {normativo.link}")
    except Exception as e:
        print(f"❌ Erro ao buscar normativos: {e}")
    
    # 4. Verificar sistema de banco
    print(f"\n4️⃣ VERIFICANDO SISTEMA DE BANCO:")
    try:
        store = get_store()
        health = store.health_check()
        
        if health['status'] == 'healthy':
            print(f"✅ Banco de dados saudável")
            print(f"👥 Usuários inscritos: {health['subscriber_count']}")
            print(f"📄 Itens processados: {health['seen_items_count']}")
            
            if health['subscriber_count'] > 0:
                print("✅ Há usuários inscritos - notificações serão enviadas")
            else:
                print("⚠️ Nenhum usuário inscrito - notificações não serão enviadas")
        else:
            print(f"❌ Problema no banco: {health.get('error', 'Erro desconhecido')}")
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {e}")
    
    # 5. Simular próxima execução
    print(f"\n5️⃣ SIMULANDO PRÓXIMA EXECUÇÃO:")
    if business_hours_active:
        # Calcula próximo horário de execução (arredonda para próximo múltiplo de 10)
        current_minute = current_time.minute
        next_execution_minute = ((current_minute // 10) + 1) * 10
        
        if next_execution_minute >= 60:
            next_execution_minute = 0
            next_hour = current_time.hour + 1
        else:
            next_hour = current_time.hour
        
        next_execution = current_time.replace(hour=next_hour, minute=next_execution_minute, second=0, microsecond=0)
        time_to_next = (next_execution - current_time).total_seconds() / 60
        
        print(f"⏰ Próxima execução estimada: {next_execution.strftime('%H:%M')}")
        print(f"⏳ Tempo até próxima execução: {time_to_next:.1f} minutos")
        
        if time_to_next <= 5:
            print("🔄 Execução muito próxima - aguarde!")
        else:
            print("⏳ Aguarde próxima execução")
    else:
        print("⏰ Sistema inativo - próxima execução às 08:00")
    
    # 6. Resumo e recomendações
    print(f"\n" + "=" * 60)
    print("📋 RESUMO E RECOMENDAÇÕES")
    print("=" * 60)
    
    issues = []
    if not logs:
        issues.append("❌ Nenhum log de execução encontrado")
    if not business_hours_active:
        issues.append("⏰ Sistema fora do horário comercial")
    
    try:
        store = get_store()
        health = store.health_check()
        if health['status'] != 'healthy':
            issues.append("❌ Problema no banco de dados")
        if health['subscriber_count'] == 0:
            issues.append("⚠️ Nenhum usuário inscrito")
    except:
        issues.append("❌ Erro de conexão com banco")
    
    if not issues:
        print("✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("🎯 Você receberá notificações automáticas quando:")
        print("   • Surgir um normativo novo")
        print("   • Estiver dentro do horário (08:00-19:25)")
        print("   • Sistema executar (a cada 10 minutos)")
    else:
        print("⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   {issue}")
        
        print(f"\n🛠️ SOLUÇÕES:")
        if "Nenhum log de execução" in str(issues):
            print("   • Verificar se serviço 'bacen-cron' está rodando no Railway")
        if "Problema no banco" in str(issues):
            print("   • Verificar configuração do DATABASE_URL")
        if "Nenhum usuário inscrito" in str(issues):
            print("   • Enviar 'oi' para o bot para se inscrever")
    
    print(f"\n🌐 MONITORAMENTO:")
    print("   • Acesse: https://bacenbot-production.up.railway.app/monitor")
    print("   • Verifique logs em tempo real")
    print("   • Monitore execuções a cada 10 minutos")

if __name__ == "__main__":
    verify_bacen_cron_system()
