"""
news_service.py — High-quality news gathering and summarization engine for JARVIS.

Gathers and organizes:
  • Bangladesh national, political, and economic news from premier outlets
    (The Daily Star, Prothom Alo, TBS News, Dhaka Tribune, Jugantor, Ittefaq).
  • High-impact international news (geopolitics, global economy, major world events).
  • Multi-source resilience: Google News RSS aggregator + direct feeds + DuckDuckGo fallback.
  • In-memory caching (15-min TTL) to prevent redundant network fetches.
  • Dual outputs: rich Markdown for the HUD display panel + structured prompts for Gemini voice.
"""
from __future__ import annotations

import html
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Cache structure: {cache_key: (timestamp, data)}
_CACHE: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL = 900  # 15 minutes


def _clean_text(text: str) -> str:
    """Unescape HTML entities and strip unwanted whitespace/tags."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_rss(url: str, timeout: float = 4.5) -> List[Dict[str, str]]:
    """Fetches and parses an RSS feed, returning a list of cleaned article dicts."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    articles = []
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            tree = ET.fromstring(content)
            for item in tree.findall(".//item"):
                raw_title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                source_elem = item.find("source")
                source = source_elem.text if source_elem is not None and source_elem.text else ""
                pub_date = item.findtext("pubDate", "")

                title = _clean_text(raw_title)
                # Google News RSS formats title as "Headline - Source Name"
                if " - " in title and not source:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0].strip()
                    source = parts[1].strip()
                elif source and title.endswith(f" - {source}"):
                    title = title[:-len(f" - {source}")].strip()

                if not title or len(title) < 12:
                    continue

                snippet = _clean_text(desc)
                # Skip duplicate snippet if it just repeats title
                if snippet.lower() == title.lower() or snippet.startswith(title):
                    snippet = ""

                articles.append({
                    "title": title,
                    "source": source,
                    "snippet": snippet,
                    "url": link,
                    "published": pub_date,
                })
    except Exception:
        pass
    return articles


def _fetch_ddg_fallback(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Fallback to DuckDuckGo news search if RSS feeds are unreachable."""
    try:
        from actions.web_search import _ddg_news
        results = _ddg_news(query, max_results=max_results)
        cleaned = []
        for r in results:
            t = _clean_text(r.get("title", ""))
            if t and len(t) > 10:
                cleaned.append({
                    "title": t,
                    "source": r.get("source", "Web"),
                    "snippet": _clean_text(r.get("snippet", "")),
                    "url": r.get("url", ""),
                    "published": "",
                })
        return cleaned
    except Exception:
        return []


def _deduplicate(articles: List[Dict[str, str]], limit: int = 8) -> List[Dict[str, str]]:
    """Deduplicates articles based on normalized title similarity."""
    seen_tokens = []
    unique = []

    for art in articles:
        t = art["title"].lower()
        # Extract meaningful alphanumeric words
        words = set(re.findall(r"\w{4,}", t))
        if not words:
            words = set(re.findall(r"\w+", t))

        is_dup = False
        for seen in seen_tokens:
            intersection = words & seen
            smaller = min(len(words), len(seen))
            if smaller > 0 and (len(intersection) / smaller) > 0.65:
                is_dup = True
                break

        if not is_dup:
            seen_tokens.append(words)
            unique.append(art)
            if len(unique) >= limit:
                break

    return unique


# ── Core Fetching Functions ───────────────────────────────────────────────────

def get_bangladesh_news(limit: int = 6, prefer_bangla: bool = False) -> List[Dict[str, str]]:
    """
    Fetches top stories from premier Bangladeshi newspapers.
    Covers national, political, economic, and social developments.
    """
    cache_key = f"bd_news_{prefer_bangla}_{limit}"
    now = time.monotonic()
    if cache_key in _CACHE and (now - _CACHE[cache_key][0]) < CACHE_TTL:
        return _CACHE[cache_key][1]

    articles = []

    # 1. Targeted query focusing on Bangladesh's premier newspapers
    if prefer_bangla:
        bd_url = (
            "https://news.google.com/rss/search?"
            + urllib.parse.urlencode({
                "q": "(site:prothomalo.com OR site:ittefaq.com.bd OR site:jugantor.com OR site:kalerkantho.com) when:2d",
                "hl": "bn",
                "gl": "BD",
                "ceid": "BD:bn",
            })
        )
    else:
        bd_url = (
            "https://news.google.com/rss/search?"
            + urllib.parse.urlencode({
                "q": "(site:thedailystar.net OR site:dhakatribune.com OR site:en.prothomalo.com OR site:tbsnews.net) when:2d",
                "hl": "en-BD",
                "gl": "BD",
                "ceid": "BD:en",
            })
        )

    articles = _fetch_rss(bd_url)

    # 2. If targeted outlets returned few results, broaden to general Bangladesh query
    if len(articles) < limit:
        broad_url = (
            "https://news.google.com/rss/search?"
            + urllib.parse.urlencode({
                "q": "Bangladesh when:1d",
                "hl": "en-BD",
                "gl": "BD",
                "ceid": "BD:en",
            })
        )
        articles.extend(_fetch_rss(broad_url))

    # 3. Fallback to DDG if RSS is blocked/empty
    if not articles:
        articles = _fetch_ddg_fallback("Bangladesh news today", max_results=limit)

    results = _deduplicate(articles, limit=limit)
    _CACHE[cache_key] = (now, results)
    return results


def get_international_news(limit: int = 4) -> List[Dict[str, str]]:
    """
    Fetches crucial, high-impact world/international news headlines
    (geopolitics, global tech/economy, international breaking news).
    """
    cache_key = f"intl_news_{limit}"
    now = time.monotonic()
    if cache_key in _CACHE and (now - _CACHE[cache_key][0]) < CACHE_TTL:
        return _CACHE[cache_key][1]

    # Google News World Topic
    world_url = (
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?"
        "hl=en-US&gl=US&ceid=US:en"
    )
    articles = _fetch_rss(world_url)

    # Fallback to DDG world news
    if not articles:
        articles = _fetch_ddg_fallback("world breaking news today", max_results=limit)

    results = _deduplicate(articles, limit=limit)
    _CACHE[cache_key] = (now, results)
    return results


def get_topic_news(topic: str, limit: int = 6) -> List[Dict[str, str]]:
    """Fetches recent news articles on any specific topic or category."""
    cache_key = f"topic_{topic.strip().lower()}_{limit}"
    now = time.monotonic()
    if cache_key in _CACHE and (now - _CACHE[cache_key][0]) < CACHE_TTL:
        return _CACHE[cache_key][1]

    url = (
        "https://news.google.com/rss/search?"
        + urllib.parse.urlencode({
            "q": f"{topic.strip()} when:3d",
            "hl": "en-BD",
            "gl": "BD",
            "ceid": "BD:en",
        })
    )
    articles = _fetch_rss(url)
    if not articles:
        articles = _fetch_ddg_fallback(f"{topic} news", max_results=limit)

    results = _deduplicate(articles, limit=limit)
    _CACHE[cache_key] = (now, results)
    return results


# ── Digest Builder ────────────────────────────────────────────────────────────

def build_news_digest(
    scope: str = "balanced",
    category: str = "all",
    prefer_bangla: bool = False,
    bd_count: int = 5,
    intl_count: int = 3,
) -> Dict[str, Any]:
    """
    Assembles a comprehensive, organized news digest.

    Returns a dict with:
      • 'bd_articles': List of Bangladesh news items
      • 'intl_articles': List of International news items
      • 'display_markdown': Formatted Markdown for the HUD content panel
      • 'prompt_summary': Structured prompt for Gemini Live voice recap
    """
    bd_items: List[Dict[str, str]] = []
    intl_items: List[Dict[str, str]] = []

    scope = (scope or "balanced").lower().strip()

    if scope in ("balanced", "both", "all", "default"):
        bd_items = get_bangladesh_news(limit=bd_count, prefer_bangla=prefer_bangla)
        intl_items = get_international_news(limit=intl_count)
    elif scope in ("bangladesh", "bd", "local", "national"):
        bd_items = get_bangladesh_news(limit=bd_count + 2, prefer_bangla=prefer_bangla)
    elif scope in ("international", "world", "global"):
        intl_items = get_international_news(limit=intl_count + 3)
    else:
        # Custom topic scope
        bd_items = get_topic_news(scope, limit=bd_count + intl_count)

    # 1. Build Markdown for UI Display
    md_lines = []
    today_str = datetime.now().strftime("%A, %d %B %Y")
    md_lines.append(f"## Daily News Digest — {today_str}\n")

    counter = 1
    if bd_items:
        md_lines.append("### [Bangladesh Highlights]")
        for it in bd_items:
            src = f" — *{it['source']}*" if it.get("source") else ""
            md_lines.append(f"{counter}. **{it['title']}**{src}")
            if it.get("snippet"):
                md_lines.append(f"   _{it['snippet'][:180]}..._")
            counter += 1
        md_lines.append("")

    if intl_items:
        md_lines.append("### [Global & International Highlights]")
        for it in intl_items:
            src = f" — *{it['source']}*" if it.get("source") else ""
            md_lines.append(f"{counter}. **{it['title']}**{src}")
            if it.get("snippet"):
                md_lines.append(f"   _{it['snippet'][:180]}..._")
            counter += 1
        md_lines.append("")

    if not bd_items and not intl_items:
        md_lines.append("No recent news headlines could be fetched at this time.")

    display_markdown = "\n".join(md_lines).strip()

    # 2. Build Speech / Prompt Summary for Gemini Live
    prompt_lines = [
        "Today's curated headlines:",
    ]
    if bd_items:
        prompt_lines.append("[Bangladesh Headlines]")
        for i, it in enumerate(bd_items, 1):
            src = f" ({it['source']})" if it.get("source") else ""
            prompt_lines.append(f"- {it['title']}{src}")

    if intl_items:
        prompt_lines.append("\n[International Headlines]")
        for i, it in enumerate(intl_items, 1):
            src = f" ({it['source']})" if it.get("source") else ""
            prompt_lines.append(f"- {it['title']}{src}")

    prompt_summary = "\n".join(prompt_lines).strip()

    return {
        "bd_articles": bd_items,
        "intl_articles": intl_items,
        "display_markdown": display_markdown,
        "prompt_summary": prompt_summary,
    }
