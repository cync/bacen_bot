import os
import asyncio
import feedparser
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import re

from storage import get_store

BR_TZ = ZoneInfo("America/Sao_Paulo")

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
    dt_br = dt_utc.astimezone(BR_TZ)
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

async def run_once():
    s = get_settings()
    store = get_store()
    subscribers = store.list_subscribers()
    if not subscribers:
        print("Nenhum inscrito — nada a enviar.")
        return

    feeds = [u.strip() for u in s.RSS_FEEDS.split(",") if u.strip()]
    bot = Bot(token=s.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)

    try:
        for feed_url in feeds:
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
                    except Exception as ex:
                        print(f"Falha ao enviar para {chat_id}: {ex}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run_once())
