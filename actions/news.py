"""
actions/news.py — Dedicated news action tool for JARVIS.

Gathers and organizes news with focus on:
  • Bangladesh premier news (The Daily Star, Prothom Alo, TBS News, Dhaka Tribune, etc.)
  • High-impact international world news (geopolitics, global economy, world events)
  • Displays formatted Markdown on the HUD dynamic content panel.
  • Supplies Gemini Live with structured headline summaries for vocal delivery.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from actions.news_service import build_news_digest


def get_news_action(
    parameters: Optional[Dict[str, Any]] = None,
    player: Any = None,
    session_memory: Any = None,
    speak: Any = None,
    response: Any = None,
) -> str:
    params = parameters or {}
    scope = str(params.get("scope", "balanced")).strip().lower()
    lang = str(params.get("language", "auto")).strip().lower()

    prefer_bangla = (lang in ("bn", "bangla", "bengali"))

    if player and hasattr(player, "write_log"):
        player.write_log(f"[News] Fetching {scope} news digest...")

    try:
        digest = build_news_digest(
            scope=scope,
            prefer_bangla=prefer_bangla,
            bd_count=5,
            intl_count=3,
        )

        # Show rich formatted Markdown on the HUD Dynamic Content Panel below the face
        if player and hasattr(player, "show_content"):
            title = "NEWS — Bangladesh & World Highlights"
            if scope in ("bangladesh", "bd"):
                title = "NEWS — Bangladesh Highlights"
            elif scope in ("international", "world"):
                title = "NEWS — World Headlines"
            player.show_content(title, digest["display_markdown"])

        # Return prompt summary to Gemini Live for voice output
        return (
            f"{digest['prompt_summary']}\n\n"
            "[INSTRUCTION] Present a concise, engaging, and informative news summary. "
            "Highlight the most important Bangladesh stories and the key international headline. "
            "Explain briefly what is happening naturally in your conversational voice. "
            "Do not just read links or numbers."
        )

    except Exception as e:
        err = f"Failed to fetch news: {e}"
        if player and hasattr(player, "write_log"):
            player.write_log(f"SYS: {err}")
        return err


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "get_news",
    "description": (
        "Fetches curated, well-organized news headlines and summaries. "
        "Call this tool whenever the user asks for news, headlines, current events, "
        "Bangladeshi news (national, politics, economy), or international world news. "
        "Returns both key Bangladesh national/economic news and major international developments."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "scope": {
                "type": "STRING",
                "description": "'balanced' (default: Bangladesh + World), 'bangladesh' (Bangladesh only), 'international' (World only), or a custom topic."
            },
            "language": {
                "type": "STRING",
                "description": "'auto' (default), 'en' for English sources, or 'bn' for Bengali sources."
            }
        },
        "required": []
    },
    "handler": get_news_action,
}
