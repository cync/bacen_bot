#!/usr/bin/env python3
"""
Teste simples para verificar se o feedparser está funcionando
"""
import feedparser

def test_feed_urls():
    """Testa diferentes URLs de feed do BACEN"""
    urls = [
        "https://www.bcb.gov.br/api/feed/v1/normativos",
        "https://www.bcb.gov.br/feed/normativos",
        "https://www.bcb.gov.br/rss/normativos",
        "https://www.bcb.gov.br/api/feed/normativos",
        "https://www.bcb.gov.br/feed/",
        "https://www.bcb.gov.br/rss/",
    ]
    
    for url in urls:
        print(f"\n🔍 Testando URL: {url}")
        try:
            feed = feedparser.parse(url)
            print(f"Status: {feed.status if hasattr(feed, 'status') else 'N/A'}")
            print(f"Título: {feed.feed.get('title', 'N/A')}")
            print(f"Entradas: {len(feed.entries)}")
            
            if feed.entries:
                print("Primeira entrada:")
                entry = feed.entries[0]
                print(f"  Título: {entry.get('title', 'N/A')}")
                print(f"  Link: {entry.get('link', 'N/A')}")
                print(f"  Data: {entry.get('published', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_feed_urls()
