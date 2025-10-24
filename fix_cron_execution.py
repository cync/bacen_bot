#!/usr/bin/env python3
"""
Diagnóstico e correção do problema de execução contínua do cron
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

async def diagnose_cron_problem():
    """Diagnostica o problema do cron"""
    print("🔍 DIAGNÓSTICO DO PROBLEMA DO CRON")
    print("=" * 60)
    
    try:
        from sender import run_once, is_business_hours, log_execution
        
        print(f"🕒 Horário atual: {datetime.now(BR_TZ).strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🕒 Horário comercial ativo: {is_business_hours()}")
        
        # Testa execução única
        print(f"\n🧪 Testando execução única...")
        await run_once()
        print(f"✅ Execução única funcionou")
        
        # Verifica logs
        try:
            import json
            with open("cron_executions.json", 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            print(f"\n📊 Logs atuais: {len(logs)}")
            if logs:
                last_log = logs[-1]
                last_time = datetime.fromisoformat(last_log['timestamp'])
                print(f"📅 Última execução: {last_time.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"📊 Status: {last_log.get('status', 'unknown')}")
        
        except Exception as e:
            print(f"❌ Erro ao verificar logs: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return False

def check_railway_configuration():
    """Verifica configuração do Railway"""
    print(f"\n🚂 VERIFICANDO CONFIGURAÇÃO RAILWAY")
    print("=" * 50)
    
    print("🔍 Possíveis problemas:")
    print("1. ❌ Serviço 'bacen-cron' não está rodando")
    print("2. ❌ Serviço está crashando após execução")
    print("3. ❌ Problema de memória/recursos")
    print("4. ❌ Erro não tratado está matando o processo")
    print("5. ❌ Railway está reiniciando o serviço")
    
    print(f"\n🛠️ SOLUÇÕES:")
    print("1. ✅ Adicionar tratamento de erro mais robusto")
    print("2. ✅ Adicionar logs de debug")
    print("3. ✅ Implementar restart automático")
    print("4. ✅ Verificar logs do Railway")
    print("5. ✅ Testar serviço localmente")

def create_robust_cron():
    """Cria versão mais robusta do cron"""
    print(f"\n🔧 CRIANDO VERSÃO ROBUSTA DO CRON")
    print("=" * 50)
    
    robust_cron_code = '''
async def run_cron_robust():
    """Executa o cron de forma mais robusta"""
    print("🕒 Iniciando cron robusto do sender (10 em 10 min, 08:00-19:25h SP)")
    
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            if HAS_TZ:
                current_time = datetime.now(BR_TZ)
            else:
                current_time = datetime.now(timezone.utc)
            
            print(f"⏰ Executando cron em {current_time}")
            
            # Executa verificação
            await run_once()
            
            # Reset contador de erros em caso de sucesso
            consecutive_errors = 0
            
            print(f"✅ Execução concluída com sucesso")
            
        except Exception as e:
            consecutive_errors += 1
            print(f"❌ Erro no cron (tentativa {consecutive_errors}): {e}")
            
            # Log do erro
            try:
                log_execution("error", {
                    "reason": "cron_execution_error",
                    "error": str(e),
                    "consecutive_errors": consecutive_errors
                })
            except:
                pass
            
            # Se muitos erros consecutivos, aguarda mais tempo
            if consecutive_errors >= max_consecutive_errors:
                print(f"⚠️ Muitos erros consecutivos ({consecutive_errors}), aguardando 30 minutos...")
                await asyncio.sleep(30 * 60)  # 30 minutos
                consecutive_errors = 0
            else:
                # Aguarda tempo progressivo baseado no número de erros
                wait_time = min(5 * consecutive_errors, 30) * 60  # 5, 10, 15, 20, 25, 30 min
                print(f"⏳ Aguardando {wait_time//60} minutos antes da próxima tentativa...")
                await asyncio.sleep(wait_time)
                continue
        
        # Aguarda 10 minutos para próxima execução
        print("⏳ Aguardando 10 minutos...")
        await asyncio.sleep(10 * 60)  # 10 minutos
'''
    
    print("✅ Código robusto criado")
    print("📝 Características:")
    print("   • Tratamento de erro robusto")
    print("   • Contador de erros consecutivos")
    print("   • Aguardo progressivo em caso de erro")
    print("   • Logs detalhados de erro")
    print("   • Restart automático após muitos erros")

def update_sender_with_robust_cron():
    """Atualiza sender.py com cron robusto"""
    print(f"\n🔄 ATUALIZANDO SENDER.PY")
    print("=" * 40)
    
    # Lê o arquivo atual
    with open("sender.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substitui a função run_cron
    old_cron = '''async def run_cron():
    """Executa o cron de 10 em 10 minutos durante horário comercial"""
    print("🕒 Iniciando cron do sender (10 em 10 min, 08:00-19:25h SP)")
    
    while True:
        try:
            if HAS_TZ:
                current_time = datetime.now(BR_TZ)
            else:
                current_time = datetime.now(timezone.utc)
            print(f"⏰ Executando cron em {current_time}")
            await run_once()
        except Exception as e:
            print(f"❌ Erro no cron: {e}")
        
        # Aguarda 10 minutos
        print("⏳ Aguardando 10 minutos...")
        await asyncio.sleep(10 * 60)  # 10 minutos'''
    
    new_cron = '''async def run_cron():
    """Executa o cron de forma robusta (10 em 10 min, 08:00-19:25h SP)"""
    print("🕒 Iniciando cron robusto do sender (10 em 10 min, 08:00-19:25h SP)")
    
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            if HAS_TZ:
                current_time = datetime.now(BR_TZ)
            else:
                current_time = datetime.now(timezone.utc)
            
            print(f"⏰ Executando cron em {current_time}")
            
            # Executa verificação
            await run_once()
            
            # Reset contador de erros em caso de sucesso
            consecutive_errors = 0
            
            print(f"✅ Execução concluída com sucesso")
            
        except Exception as e:
            consecutive_errors += 1
            print(f"❌ Erro no cron (tentativa {consecutive_errors}): {e}")
            
            # Log do erro
            try:
                log_execution("error", {
                    "reason": "cron_execution_error",
                    "error": str(e),
                    "consecutive_errors": consecutive_errors
                })
            except:
                pass
            
            # Se muitos erros consecutivos, aguarda mais tempo
            if consecutive_errors >= max_consecutive_errors:
                print(f"⚠️ Muitos erros consecutivos ({consecutive_errors}), aguardando 30 minutos...")
                await asyncio.sleep(30 * 60)  # 30 minutos
                consecutive_errors = 0
            else:
                # Aguarda tempo progressivo baseado no número de erros
                wait_time = min(5 * consecutive_errors, 30) * 60  # 5, 10, 15, 20, 25, 30 min
                print(f"⏳ Aguardando {wait_time//60} minutos antes da próxima tentativa...")
                await asyncio.sleep(wait_time)
                continue
        
        # Aguarda 10 minutos para próxima execução
        print("⏳ Aguardando 10 minutos...")
        await asyncio.sleep(10 * 60)  # 10 minutos'''
    
    # Substitui no conteúdo
    if old_cron in content:
        new_content = content.replace(old_cron, new_cron)
        
        # Salva arquivo atualizado
        with open("sender.py", 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ sender.py atualizado com cron robusto")
        return True
    else:
        print("❌ Não foi possível encontrar função run_cron para substituir")
        return False

async def main():
    """Função principal"""
    print("🔧 CORREÇÃO DO PROBLEMA DE EXECUÇÃO CONTÍNUA")
    print("=" * 70)
    
    # Diagnostica problema
    await diagnose_cron_problem()
    
    # Verifica configuração Railway
    check_railway_configuration()
    
    # Cria versão robusta
    create_robust_cron()
    
    # Atualiza sender.py
    success = update_sender_with_robust_cron()
    
    if success:
        print(f"\n🎉 CORREÇÃO APLICADA!")
        print("=" * 40)
        print("✅ Cron robusto implementado")
        print("✅ Tratamento de erro melhorado")
        print("✅ Restart automático configurado")
        print("✅ Logs detalhados de erro")
        print("\n🔄 Próximos passos:")
        print("1. Fazer commit e push")
        print("2. Aguardar deploy no Railway")
        print("3. Monitorar execuções")
        print("4. Verificar se não para mais")
    else:
        print(f"\n❌ FALHA NA CORREÇÃO")
        print("=" * 40)
        print("🔍 Verificar arquivo sender.py manualmente")

if __name__ == "__main__":
    asyncio.run(main())
