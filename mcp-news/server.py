import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx
from mcp.server.fastmcp import FastMCP

# feedparser через httpx чтобы обойти системные SSL-проблемы
def _fetch_feed(url: str) -> feedparser.FeedParserDict:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    return feedparser.parse(r.text)

mcp = FastMCP("mcp-news", host="0.0.0.0", port=8000, stateless_http=True)

SOURCES = ["https://habr.com/ru/rss/all/all/?fl=ru"]


def parse_period(period: str) -> float:
    """Convert period string like '7d', '24h' to seconds."""
    match = re.match(r"(\d+)([dh])", period.strip().lower())
    if not match:
        return 7 * 24 * 3600
    value, unit = int(match.group(1)), match.group(2)
    return value * (86400 if unit == "d" else 3600)


def safe_timestamp(date_str: str) -> float | None:
    try:
        return parsedate_to_datetime(date_str).timestamp()
    except Exception:
        try:
            return datetime.fromisoformat(date_str).timestamp()
        except Exception:
            return None


@mcp.tool()
def get_news(topic: str, period: str = "7d", limit: int = 7) -> list[dict]:
    """
    Получить список новостей с Хабра по теме и периоду.

    Args:
        topic: Тема или ключевое слово для поиска. Пустая строка — все новости.
        period: Период давности материалов: '7d', '24h', '3d', '30d'.
        limit: Максимальное число статей (1–20).

    Returns:
        Список словарей {title, url, published_at, source, snippet}.
    """
    limit = max(1, min(20, limit))
    max_age = parse_period(period)
    now = datetime.now(timezone.utc).timestamp()

    items = []
    for url in SOURCES:
        try:
            feed = _fetch_feed(url)
            for entry in feed.entries:
                pub = entry.get("published") or entry.get("updated") or ""
                ts = safe_timestamp(pub)
                age = (now - ts) if ts else 0

                if ts and age > max_age:
                    continue

                title = entry.get("title", "")
                snippet = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:200]

                if topic.strip():
                    needle = topic.lower()
                    if needle not in title.lower() and needle not in snippet.lower():
                        continue

                items.append({
                    "title": title,
                    "url": entry.get("link", ""),
                    "published_at": pub,
                    "source": "habr",
                    "snippet": snippet,
                })
        except Exception as e:
            print(f"RSS error {url}: {e}")

    items.sort(key=lambda i: safe_timestamp(i["published_at"]) or 0, reverse=True)
    return items[:limit]


@mcp.tool()
def fetch_article(url: str) -> dict:
    """
    Получить расширенный текст статьи по URL с Хабра.

    Args:
        url: URL статьи.

    Returns:
        Словарь {title, text, author, published_at}.
    """
    try:
        feed = _fetch_feed(url)
        if not feed.entries:
            raise ValueError("No entries found")
        entry = feed.entries[0]
        text = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:1000]
        author = ""
        if entry.get("authors"):
            author = entry["authors"][0].get("name", "")
        elif entry.get("author"):
            author = entry.get("author", "")
        return {
            "title": entry.get("title", ""),
            "text": text,
            "author": author,
            "published_at": entry.get("published") or entry.get("updated") or "",
        }
    except Exception as e:
        return {"error": str(e), "url": url}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
