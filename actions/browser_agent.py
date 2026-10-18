"""
actions/browser_agent.py — Autonomous, DOM-aware web browsing agent for JARVIS.

Powered by browser-use and Google Gemini.
Navigates websites, clicks interactive elements, fills forms, extracts data,
and handles complex multi-step web workflows inside Google Chrome.
Auto-discovered by core/action_loader.py.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import json
import sys
from pathlib import Path
from typing import Optional

from tools.chrome_launcher import is_cdp_available


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


_CONFIG_PATH = _base_dir() / "config" / "api_keys.json"


def _load_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _run_async(coro):
    """Safely run an async coroutine whether or not an event loop is already active."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


async def _execute_agent_task(task: str, max_steps: int = 15, player=None) -> str:
    from browser_use import Agent
    from browser_use.browser.profile import BrowserProfile
    from browser_use.llm import ChatGoogle

    config = _load_config()
    api_key = config.get("gemini_api_key", "")
    if not api_key:
        return "BrowserAgent error: No gemini_api_key configured in config/api_keys.json."

    if player:
        player.write_log(f"[BrowserAgent] Starting task: {task[:50]}...")
    print(f"[BrowserAgent] Starting autonomous web task: '{task}'")

    llm = ChatGoogle(model="gemini-3.5-flash-lite", api_key=api_key)
    fallback_llm = ChatGoogle(model="gemini-3.1-flash-lite", api_key=api_key)
    if is_cdp_available(9222):
        print("[BrowserAgent] Attaching to real Chrome session via CDP on port 9222...")
        profile = BrowserProfile(
            cdp_url="http://127.0.0.1:9222",
            keep_alive=True,
            highlight_elements=True,
        )
    else:
        profile = BrowserProfile(
            headless=False,
            channel="chrome",
            keep_alive=True,
            highlight_elements=True,
        )

    agent = Agent(
        task=task,
        llm=llm,
        fallback_llm=fallback_llm,
        browser_profile=profile,
        max_actions_per_step=4,
    )

    history = await agent.run(max_steps=max_steps)
    final = history.final_result()

    if player:
        player.write_log("[BrowserAgent] Task completed.")
    print(f"[BrowserAgent] Completed. Result: {final[:100] if final else 'Done'}")

    return final or "Web task completed successfully."


def browser_agent(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    task = str(params.get("task", "")).strip()
    if not task:
        # Fall back to 'query' or 'description'
        task = str(params.get("query", params.get("description", ""))).strip()

    if not task:
        return "Please provide a task description for the browser agent."

    max_steps = int(params.get("max_steps", 15))

    try:
        result = _run_async(_execute_agent_task(task, max_steps=max_steps, player=player))
        return result
    except Exception as e:
        print(f"[BrowserAgent] Error: {e}")
        return f"Browser agent failed to complete task: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "browser_agent",
    "description": (
        "Autonomous, high-intelligence web browsing agent. Call this whenever the user wants you "
        "to perform a multi-step web task, search and extract data from websites, fill forms, "
        "find products, check prices, read articles, or interact with web features on any site. "
        "The agent opens Google Chrome, reads live page elements, clicks, types, and returns the result."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "task": {
                "type": "STRING",
                "description": "Clear description of the web task to accomplish (e.g. 'Search for latest iPhone prices on Amazon and return the top 3 options')"
            },
            "max_steps": {
                "type": "INTEGER",
                "description": "Maximum steps/actions the agent is allowed to take (default: 15)"
            }
        },
        "required": [
            "task"
        ]
    },
    "handler": browser_agent,
}
