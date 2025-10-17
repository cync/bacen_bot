import os
import asyncio
import feedparser
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re

from storage import get_store

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
    RSS_FEEDS: str = Field(..., description="CSV de URLs de feeds RSS (Normas do BCB)")
    MAX_ITEMS_PER_FEED: int = int(os.getenv("MAX_ITEMS_PER_FEED", "50"))

def get_settings() -> Settings:
    return Settings(
        TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"],
        RSS_FEEDS=os.environ["RSS_FEEDS"],
        MAX_ITEMS_PER_FEED=int(os.getenv("MAX_ITEMS_PER_FEED", "50")),
    )

def strip_html(html: str) -> str:
    # remove tags de forma segura
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text(" ", strip=True)
    # normaliza espaços
    return re.sub(r"\s+", " ", text).strip()

def dt_to_br_str(dt_utc: datetime) -> str:
    # converte UTC -> São Paulo e formata
    if HAS_TZ:
        dt_br = dt_utc.astimezone(BR_TZ)
    else:
        dt_br = dt_utc
    return dt_br.strftime("%d/%m/%Y %H:%M %Z")

def published_dt(entry) -> datetime:
    # tenta published_parsed -> updated_parsed -> agora
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def build_message(entry, when_str: str) -> str:
    title = entry.get("title", "Nova publicação")
    link = entry.get("link", "")
    # resumo sucinto: até ~300 chars
    raw_summary = entry.get("summary", "") or entry.get("description", "")
    summary = strip_html(raw_summary)[:300]
    # mensagem final (curta, com data/hora BR)
    parts = [f"🆕 <b>{title}</b>", f"🕒 {when_str}"]
    if summary:
        parts.append(summary)
    if link:
        parts.append(link)
    return "\n".join(parts)

def is_business_hours() -> bool:
    """Verifica se está no horário comercial (09-19h SP)"""
    if HAS_TZ:
        now_sp = datetime.now(BR_TZ)
    else:
        now_sp = datetime.now(timezone.utc)
    return 9 <= now_sp.hour < 19

async def run_once():
    """Executa uma vez o processamento de feeds"""
    if not is_business_hours():
        print("Fora do horário comercial (09-19h SP) — nada a processar.")
        return
    
    s = get_settings()
    store = get_store()
    subscribers = store.list_subscribers()
    if not subscribers:
        print("Nenhum inscrito — nada a enviar.")
        return

    feeds = [u.strip() for u in s.RSS_FEEDS.split(",") if u.strip()]
    bot = Bot(token=s.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        for feed_url in feeds:
            print(f"Processando feed: {feed_url}")
            d = feedparser.parse(feed_url)
            for e in d.entries[: s.MAX_ITEMS_PER_FEED]:
                item_id = getattr(e, "id", None) or getattr(e, "guid", None) or getattr(e, "link", None) or e.get("title", "")
                if not item_id:
                    continue
                if not store.mark_new_and_return_is_new(feed_url, item_id):
                    continue  # já enviado antes

                when = published_dt(e)
                when_str = dt_to_br_str(when)
                msg = build_message(e, when_str)

                # broadcast simples
                for chat_id in subscribers:
                    try:
                        await bot.send_message(chat_id, msg, disable_web_page_preview=False)
                        print(f"✅ Enviado para {chat_id}")
                    except Exception as ex:
                        print(f"❌ Falha ao enviar para {chat_id}: {ex}")
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
