#!/usr/bin/env python3
"""
Módulo para buscar normativos do BACEN por período
"""
import feedparser
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
import re

BR_TZ = ZoneInfo("America/Sao_Paulo")

class BACENNormativo:
    def __init__(self, title: str, link: str, published: datetime, summary: str = ""):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary

def get_bacen_feed_url() -> str:
    """Retorna a URL do feed RSS do BACEN para normativos"""
    return "https://www.bcb.gov.br/api/feed/v1/normativos"

def parse_bacen_feed() -> List[BACENNormativo]:
    """Parseia o feed RSS do BACEN e retorna lista de normativos"""
    feed_url = get_bacen_feed_url()
    feed = feedparser.parse(feed_url)
    
    normativos = []
    for entry in feed.entries:
        try:
            # Extrai data de publicação
            published_dt = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                published_dt = datetime.now(timezone.utc)
            
            # Converte para horário de SP
            published_dt = published_dt.astimezone(BR_TZ)
            
            normativo = BACENNormativo(
                title=entry.get('title', 'Normativo sem título'),
                link=entry.get('link', ''),
                published=published_dt,
                summary=entry.get('summary', '')[:200] + '...' if len(entry.get('summary', '')) > 200 else entry.get('summary', '')
            )
            normativos.append(normativo)
        except Exception as e:
            print(f"Erro ao processar entrada do feed: {e}")
            continue
    
    return normativos

def get_ultimo_normativo() -> Optional[BACENNormativo]:
    """Retorna o último normativo publicado"""
    normativos = parse_bacen_feed()
    if normativos:
        # Ordena por data de publicação (mais recente primeiro)
        normativos.sort(key=lambda x: x.published, reverse=True)
        return normativos[0]
    return None

def get_normativos_hoje() -> List[BACENNormativo]:
    """Retorna todos os normativos publicados hoje"""
    hoje = datetime.now(BR_TZ).date()
    normativos = parse_bacen_feed()
    
    normativos_hoje = []
    for normativo in normativos:
        if normativo.published.date() == hoje:
            normativos_hoje.append(normativo)
    
    return normativos_hoje

def get_normativos_ontem() -> List[BACENNormativo]:
    """Retorna todos os normativos publicados ontem"""
    ontem = (datetime.now(BR_TZ) - timedelta(days=1)).date()
    normativos = parse_bacen_feed()
    
    normativos_ontem = []
    for normativo in normativos:
        if normativo.published.date() == ontem:
            normativos_ontem.append(normativo)
    
    return normativos_ontem

def get_normativos_semanal() -> List[BACENNormativo]:
    """Retorna todos os normativos publicados esta semana"""
    hoje = datetime.now(BR_TZ)
    inicio_semana = hoje - timedelta(days=hoje.weekday())  # Segunda-feira
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    
    normativos = parse_bacen_feed()
    
    normativos_semana = []
    for normativo in normativos:
        if normativo.published >= inicio_semana:
            normativos_semana.append(normativo)
    
    return normativos_semana

def format_normativo_message(normativo: BACENNormativo) -> str:
    """Formata uma mensagem para um normativo"""
    data_str = normativo.published.strftime("%d/%m/%Y %H:%M")
    
    message = f"📄 <b>{normativo.title}</b>\n"
    message += f"🕒 {data_str}\n"
    if normativo.summary:
        message += f"\n{normativo.summary}\n"
    message += f"\n🔗 {normativo.link}"
    
    return message

def format_multiple_normativos_message(normativos: List[BACENNormativo], periodo: str) -> str:
    """Formata uma mensagem para múltiplos normativos"""
    if not normativos:
        return f"❌ Nenhum normativo encontrado para {periodo}."
    
    message = f"📋 <b>Normativos do BACEN - {periodo}</b>\n"
    message += f"📊 Total: {len(normativos)} normativo(s)\n\n"
    
    for i, normativo in enumerate(normativos[:10], 1):  # Limita a 10 para não sobrecarregar
        data_str = normativo.published.strftime("%d/%m/%Y %H:%M")
        message += f"{i}. <b>{normativo.title}</b>\n"
        message += f"   🕒 {data_str}\n"
        message += f"   🔗 {normativo.link}\n\n"
    
    if len(normativos) > 10:
        message += f"... e mais {len(normativos) - 10} normativo(s)"
    
    return message
