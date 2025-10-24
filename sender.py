import os
import asyncio
import feedparser
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
import re
import json

from storage import get_store
from bacen_feed import parse_bacen_feed, BACENNormativo, format_normativo_message

# Load environment variables from .env file
load_dotenv()

# Compatibilidade com Windows - usar pytz se disponível, senão usar UTC
try:
    import pytz
    BR_TZ = pytz.timezone('America/Sao_Paulo')
    HAS_TZ = True
except ImportError:
    # Fallback para UTC se pytz não estiver disponível
    BR_TZ = timezone.utc
    HAS_TZ = False
    print("⚠️ pytz não disponível, usando UTC como fallback")

class Settings(BaseModel):
    TELEGRAM_TOKEN: str = Field(...)
    MAX_ITEMS_PER_FEED: int = int(os.getenv("MAX_ITEMS_PER_FEED", "50"))

def get_settings() -> Settings:
    return Settings(
        TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"],
        MAX_ITEMS_PER_FEED=int(os.getenv("MAX_ITEMS_PER_FEED", "50")),
    )

# Sistema de logs de execução
EXECUTION_LOG_FILE = "cron_executions.json"

def log_execution(status: str, details: dict = None):
    """Registra uma execução do cron"""
    try:
        # Carrega logs existentes
        if os.path.exists(EXECUTION_LOG_FILE):
            with open(EXECUTION_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Adiciona novo log
        log_entry = {
            "timestamp": datetime.now(BR_TZ).isoformat(),
            "status": status,
            "details": details or {}
        }
        
        logs.append(log_entry)
        
        # Mantém apenas os últimos 100 logs
        if len(logs) > 100:
            logs = logs[-100:]
        
        # Salva logs
        with open(EXECUTION_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

def get_execution_logs():
    """Retorna os logs de execução"""
    try:
        if os.path.exists(EXECUTION_LOG_FILE):
            with open(EXECUTION_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Erro ao carregar logs: {e}")
        return []

def is_business_hours() -> bool:
    """Verifica se está no horário comercial (08:00-19:25h SP)"""
    if HAS_TZ:
        now_sp = datetime.now(BR_TZ)
    else:
        now_sp = datetime.now(timezone.utc)
    
    # Horário comercial: 08:00 até 19:25 (horário de SP)
    hour = now_sp.hour
    minute = now_sp.minute
    
    # 08:00 até 19:25
    if hour < 8:
        return False
    elif hour == 8:
        return True  # A partir das 08:00
    elif hour < 19:
        return True  # Entre 09:00 e 18:59
    elif hour == 19:
        return minute <= 25  # Até 19:25
    else:
        return False  # Após 19:25

async def run_once():
    """Executa uma vez o processamento do feed do BACEN"""
    start_time = datetime.now(BR_TZ)
    print(f"🕒 [{start_time.strftime('%H:%M:%S')}] Iniciando verificação de normativos...")
    
    # Log de início
    log_execution("started", {
        "timestamp": start_time.isoformat(),
        "business_hours": is_business_hours()
    })
    
    if not is_business_hours():
        print("⏰ Fora do horário comercial (08:00-19:25h SP) — nada a processar.")
        log_execution("skipped", {"reason": "outside_business_hours"})
        return
    
    s = get_settings()
    store = get_store()
    
    # Verificação de saúde do banco
    health = store.health_check()
    if health['status'] != 'healthy':
        print(f"❌ Problema no banco de dados: {health.get('error', 'Erro desconhecido')}")
        log_execution("error", {"reason": "database_unhealthy", "error": health.get('error')})
        return
    
    print(f"✅ Banco de dados saudável - {health['subscriber_count']} inscrito(s)")
    
    subscribers = store.list_subscribers()
    if not subscribers:
        print("ℹ️ Nenhum inscrito — nada a enviar.")
        log_execution("skipped", {"reason": "no_subscribers"})
        return

    print(f"🔍 Buscando normativos do BACEN...")
    normativos = parse_bacen_feed()
    
    if not normativos:
        print("❌ Nenhum normativo encontrado no feed do BACEN")
        log_execution("error", {"reason": "no_normativos_found"})
        return
    
    # Ordena por data de publicação (mais recente primeiro)
    normativos.sort(key=lambda x: x.published, reverse=True)
    print(f"📊 {len(normativos)} normativos encontrados no feed")
    
    bot = Bot(token=s.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        novos_normativos = 0
        normativos_enviados = []
        
        for normativo in normativos[:s.MAX_ITEMS_PER_FEED]:
            # Usa o link como ID único para o normativo
            item_id = normativo.link or normativo.title
            
            if not item_id:
                continue
                
            # Verifica se já foi enviado antes
            if not store.mark_new_and_return_is_new("bacen_feed", item_id):
                continue  # já enviado antes

            print(f"🆕 Novo normativo detectado: {normativo.title}")

            # Formata a mensagem usando o sistema do BACEN
            msg = format_normativo_message(normativo)
            
            # Adiciona prefixo de notificação
            notification_msg = f"🆕 <b>NOVO NORMATIVO BACEN</b>\n\n{msg}"

            # Envia para todos os inscritos
            for chat_id in subscribers:
                try:
                    await bot.send_message(chat_id, notification_msg, disable_web_page_preview=False)
                    print(f"✅ Enviado para {chat_id}: {normativo.title}")
                except Exception as ex:
                    print(f"❌ Falha ao enviar para {chat_id}: {ex}")
            
            novos_normativos += 1
            normativos_enviados.append({
                "title": normativo.title,
                "published": normativo.published.isoformat(),
                "link": normativo.link
            })
        
        end_time = datetime.now(BR_TZ)
        duration = (end_time - start_time).total_seconds()
        
        if novos_normativos > 0:
            print(f"📊 Total de novos normativos enviados: {novos_normativos}")
            log_execution("success", {
                "normativos_enviados": novos_normativos,
                "subscribers_count": len(subscribers),
                "duration_seconds": duration,
                "normativos": normativos_enviados
            })
        else:
            print("ℹ️ Nenhum normativo novo encontrado")
            log_execution("no_new_items", {
                "subscribers_count": len(subscribers),
                "duration_seconds": duration
            })
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        log_execution("error", {"reason": "execution_error", "error": str(e)})
    finally:
        await bot.session.close()
        print(f"🏁 Verificação concluída às {datetime.now(BR_TZ).strftime('%H:%M:%S')}")

async def run_cron():
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
        await asyncio.sleep(10 * 60)  # 10 minutos

if __name__ == "__main__":
    asyncio.run(run_once())
