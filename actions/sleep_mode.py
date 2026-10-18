"""
sleep_mode.py — Sleep and wake control for JARVIS.

Allows the assistant to go to sleep when told by the user in English, Bengali,
or any language, and stay quiet until explicitly awakened by name.
Auto-discovered by core/action_loader.py.
"""
from __future__ import annotations

from typing import Callable, Optional

_SLEEP_HOOK: Optional[Callable[[str], None]] = None
_WAKE_HOOK: Optional[Callable[[str], None]] = None
_STATUS_HOOK: Optional[Callable[[], bool]] = None

def register_hooks(
    on_sleep: Optional[Callable[[str], None]] = None,
    on_wake: Optional[Callable[[str], None]] = None,
    is_awake: Optional[Callable[[], bool]] = None,
) -> None:
    """Called by main.py to bind the live session's sleep/wake handlers."""
    global _SLEEP_HOOK, _WAKE_HOOK, _STATUS_HOOK
    _SLEEP_HOOK = on_sleep
    _WAKE_HOOK = on_wake
    _STATUS_HOOK = is_awake


def sleep_mode(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    action = str(params.get("action", "sleep")).lower().strip()
    reason = str(params.get("reason", "user request")).strip()

    if action in ("wake", "awake", "wakeup"):
        if _WAKE_HOOK:
            _WAKE_HOOK(reason)
        elif player and hasattr(player, "set_state"):
            player.set_state("LISTENING")
        if player:
            player.write_log("SYS: Awake and listening.")
        return "Awake and listening, sir."

    if action == "status":
        awake = _STATUS_HOOK() if _STATUS_HOOK else True
        return f"JARVIS is currently {'awake' if awake else 'sleeping'}."

    # Default: go to sleep
    if _SLEEP_HOOK:
        _SLEEP_HOOK(reason)
    elif player and hasattr(player, "set_state"):
        player.set_state("SLEEPING")

    if player:
        player.write_log("SYS: JARVIS entered sleep mode. Call my name to wake me.")

    print(f"[SleepMode] Assistant entered sleep mode ({reason}).")
    return "[SLEEP_ACTIVE] I am now going to sleep, sir. Call my name when you need me."


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "sleep_mode",
    "description": (
        "Controls sleep mode. Call this tool IMMEDIATELY whenever the user tells you to sleep, "
        "go to sleep, shut up, be quiet, standby, or take a rest in ANY language. "
        "Examples in English: 'go to sleep', 'sleep', 'be quiet', 'standby'. "
        "Examples in Bengali: 'ঘুমিয়ে পড়ো', 'ঘুম যাও', 'চুপ থাকো', 'স্ট্যান্ডবাই যাও', 'বিশ্রাম নাও'. "
        "While in sleep mode, you remain silent and only awake when the user calls your name."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'sleep' to enter sleep mode (default), 'wake' to wake up, or 'status'."
            },
            "reason": {
                "type": "STRING",
                "description": "Optional reason for entering sleep mode or waking up."
            }
        },
        "required": []
    },
    "handler": sleep_mode,
}
