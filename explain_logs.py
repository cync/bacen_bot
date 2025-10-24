#!/usr/bin/env python3
"""
Explicação detalhada do sistema de logs de execução
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sender import get_execution_logs

def explain_execution_logs():
    """Explica o que está sendo contabilizado nas execuções"""
    print("📊 EXPLICAÇÃO: EXECUÇÕES TOTAIS")
    print("=" * 60)
    
    logs = get_execution_logs()
    
    print(f"📋 Total de logs encontrados: {len(logs)}")
    print()
    
    if logs:
        print("🔍 TIPOS DE EXECUÇÃO CONTABILIZADOS:")
        print()
        
        # Conta cada tipo de status
        status_counts = {}
        for log in logs:
            status = log.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Explica cada tipo
        explanations = {
            'started': '🚀 INÍCIO - Quando o cron inicia uma verificação',
            'success': '✅ SUCESSO - Quando normativos novos são encontrados e enviados',
            'no_new_items': 'ℹ️ SEM NOVIDADES - Quando não há normativos novos',
            'skipped': '⏭️ PULADO - Quando execução é pulada (fora do horário, sem inscritos, etc)',
            'error': '❌ ERRO - Quando ocorre algum erro durante a execução'
        }
        
        for status, count in status_counts.items():
            explanation = explanations.get(status, f"❓ DESCONHECIDO - {status}")
            print(f"   {explanation}")
            print(f"      📊 Quantidade: {count}")
            print()
        
        print("📈 RESUMO:")
        print(f"   • Total de execuções: {len(logs)}")
        print(f"   • Sucessos: {status_counts.get('success', 0)}")
        print(f"   • Sem novidades: {status_counts.get('no_new_items', 0)}")
        print(f"   • Puladas: {status_counts.get('skipped', 0)}")
        print(f"   • Erros: {status_counts.get('error', 0)}")
        
        print()
        print("🕒 ÚLTIMAS 5 EXECUÇÕES:")
        recent_logs = logs[-5:]
        for i, log in enumerate(recent_logs, 1):
            timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            status = log.get('status', 'unknown')
            details = log.get('details', {})
            
            print(f"   {i}. {timestamp.strftime('%d/%m %H:%M:%S')} - {status.upper()}")
            if details:
                if 'reason' in details:
                    print(f"      💡 Motivo: {details['reason']}")
                if 'normativos_enviados' in details:
                    print(f"      📄 Normativos enviados: {details['normativos_enviados']}")
                if 'subscribers_count' in details:
                    print(f"      👥 Inscritos: {details['subscribers_count']}")
    
    else:
        print("❌ NENHUM LOG ENCONTRADO")
        print()
        print("💡 POSSÍVEIS MOTIVOS:")
        print("   • Sistema nunca foi executado")
        print("   • Arquivo de logs não existe")
        print("   • Serviço bacen-cron não está rodando")
        print("   • Problema de permissões no arquivo")
    
    print()
    print("=" * 60)
    print("📋 O QUE SIGNIFICA 'EXECUÇÕES TOTAIS'")
    print("=" * 60)
    print()
    print("🎯 'Execuções Totais' contabiliza TODAS as tentativas de execução")
    print("   do sistema bacen-cron, incluindo:")
    print()
    print("✅ EXECUÇÕES VÁLIDAS:")
    print("   • 🚀 Início de verificação")
    print("   • ✅ Sucesso (normativos enviados)")
    print("   • ℹ️ Sem novidades (nenhum normativo novo)")
    print()
    print("⏭️ EXECUÇÕES PULADAS:")
    print("   • ⏰ Fora do horário comercial (08:00-19:25)")
    print("   • 👥 Sem usuários inscritos")
    print("   • 🗄️ Problema no banco de dados")
    print()
    print("❌ EXECUÇÕES COM ERRO:")
    print("   • 🌐 Falha ao buscar normativos")
    print("   • 📱 Erro ao enviar notificações")
    print("   • 💾 Problema de armazenamento")
    print()
    print("📊 LIMITE DE LOGS:")
    print("   • Sistema mantém apenas os últimos 100 logs")
    print("   • Logs antigos são removidos automaticamente")
    print("   • Arquivo: cron_executions.json")
    print()
    print("🔄 FREQUÊNCIA:")
    print("   • Execução a cada 10 minutos")
    print("   • Apenas durante horário comercial")
    print("   • Total esperado por dia: ~68 execuções")

if __name__ == "__main__":
    explain_execution_logs()
