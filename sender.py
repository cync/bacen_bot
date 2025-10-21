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

# Funções removidas - agora usamos o sistema integrado do bacen_feed.py

def is_business_hours() -> bool:
    """Verifica se está no horário comercial (09-19h SP)"""
    if HAS_TZ:
        now_sp = datetime.now(BR_TZ)
    else:
        now_sp = datetime.now(timezone.utc)
    return 9 <= now_sp.hour < 19

async def run_once():
    """Executa uma vez o processamento do feed do BACEN"""
    if not is_business_hours():
        print("Fora do horário comercial (09-19h SP) — nada a processar.")
        return
    
    s = get_settings()
    store = get_store()
    subscribers = store.list_subscribers()
    if not subscribers:
        print("Nenhum inscrito — nada a enviar.")
        return

    print("🔍 Buscando normativos do BACEN...")
    normativos = parse_bacen_feed()
    
    if not normativos:
        print("❌ Nenhum normativo encontrado no feed do BACEN")
        return
    
    # Ordena por data de publicação (mais recente primeiro)
    normativos.sort(key=lambda x: x.published, reverse=True)
    
    bot = Bot(token=s.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        novos_normativos = 0
        
        for normativo in normativos[:s.MAX_ITEMS_PER_FEED]:
            # Usa o link como ID único para o normativo
            item_id = normativo.link or normativo.title
            
            if not item_id:
                continue
                
            # Verifica se já foi enviado antes
            if not store.mark_new_and_return_is_new("bacen_feed", item_id):
                continue  # já enviado antes

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
        
        if novos_normativos > 0:
            print(f"📊 Total de novos normativos enviados: {novos_normativos}")
        else:
            print("ℹ️ Nenhum normativo novo encontrado")
            
    finally:
        await bot.session.close()

async def run_cron():
    """Executa o cron de 10 em 10 minutos durante horário comercial"""
    print("🕒 Iniciando cron do sender (10 em 10 min, 09-19h SP)")
    
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
