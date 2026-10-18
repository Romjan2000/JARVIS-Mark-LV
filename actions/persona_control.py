"""
persona_control.py — Dynamic Persona, 3D Face Model & Sci-Fi Visualizer Control.

Enables hands-free voice control and tool-calling to switch avatars, face models,
Tony Stark / sci-fi faceless visualizers, and UI theme accents on the fly.
Auto-discovered by core/action_loader.py.
"""
from __future__ import annotations

from typing import Any, Optional

from memory.config_manager import (
    AVAILABLE_FACE_MODELS,
    HUD_STYLES,
    save_face_model,
    save_hud_style,
    save_voice,
)
from core.personas import (
    ALL_PERSONAS,
    MALE_PERSONAS,
    FEMALE_PERSONAS,
    VISUALIZER_PERSONAS,
    get_persona,
    get_matching_voice,
)


def persona_control(
    parameters: dict | None = None,
    player=None,
    speak=None,
    session_memory=None,
    response=None,
) -> str:
    """Controls assistant persona, 3D face model, sci-fi visualizer, and UI theme."""
    params = parameters or {}
    action = str(params.get("action", "switch_persona")).lower().strip()
    target = str(params.get("name", "") or params.get("target", "") or params.get("style", "")).lower().strip()

    # ── 1. List Available Visualizers & Face Mode ────────────────────────────
    if action in ("list", "catalog", "help"):
        visualizers = ", ".join(f"{v['name']}" for v in VISUALIZER_PERSONAS.values())
        msg = (
            f"Available Modes:\n"
            f"• 3D Animated Holographic Face: Original Canonical Face Model (face)\n"
            f"• Tony Stark / Sci-Fi Visualizers: {visualizers}"
        )
        if player and hasattr(player, "write_log"):
            player.write_log("SYS: Displaying HUD visual catalog.")
        return msg

    # ── 2. Switch HUD Style / Visualizer Directly ────────────────────────────
    if action in ("set_hud_style", "hud_style", "visualizer", "set_visualizer"):
        style_key = target
        # Fuzzy match visualizer names
        for vk, vinfo in VISUALIZER_PERSONAS.items():
            if target in (vk, vinfo["name"].lower(), vinfo["title"].lower()):
                style_key = vk
                break

        if style_key not in HUD_STYLES:
            style_key = "face" if ("face" in target or "original" in target) else "arc_reactor"

        save_hud_style(style_key)
        if player:
            if hasattr(player, "set_hud_style"):
                player.set_hud_style(style_key)
            if style_key in VISUALIZER_PERSONAS:
                v = VISUALIZER_PERSONAS[style_key]
                if hasattr(player, "apply_ui_accent") and v.get("accent_color"):
                    player.apply_ui_accent(v["accent_color"])
                if hasattr(player, "write_log"):
                    player.write_log(f"SYS: HUD mode switched to {v['name']}.")
            else:
                if hasattr(player, "set_face_model"):
                    player.set_face_model("original")
                if hasattr(player, "write_log"):
                    player.write_log(f"SYS: HUD mode switched to Original 3D Face Avatar.")

        if style_key == "face":
            return "HUD switched to the original 3D animated holographic face avatar, sir."
        v_name = VISUALIZER_PERSONAS.get(style_key, {}).get("name", style_key.title())
        return f"Activated {v_name} visualizer. All telemetry systems synced."

    # ── 3. Switch 3D Face Model ──────────────────────────────────────────────
    if action in ("set_face_model", "face_model", "change_face", "show_face", "face"):
        save_face_model("original")
        save_hud_style("face")

        if player:
            if hasattr(player, "set_hud_style"):
                player.set_hud_style("face")
            if hasattr(player, "set_face_model"):
                player.set_face_model("original")
            if hasattr(player, "write_log"):
                player.write_log("SYS: Reverted to original 3D face avatar model.")

        return "Switched back to the original 3D canonical face avatar model."

    # ── 4. Unified Persona Switch (Presets: Face/Visualizer + Color + Voice) ──
    # Resolve target persona key
    resolved_key = None
    for pk, pinfo in ALL_PERSONAS.items():
        if target in (pk, pinfo["name"].lower(), pinfo.get("title", "").lower()):
            resolved_key = pk
            break

    if not resolved_key:
        # Check partial matching (e.g. "arc" -> "arc_reactor", "tesseract" -> "tesseract")
        for pk in ALL_PERSONAS:
            if target in pk or pk in target:
                resolved_key = pk
                break

    if not resolved_key:
        return (
            f"Persona '{target}' not recognized. Try 'original' / 'canonical', 'arc reactor', "
            f"'quantum sphere', 'cyber iris', 'tesseract', 'black hole', or 'neural lotus'."
        )

    p = ALL_PERSONAS[resolved_key]
    is_visualizer = p.get("type") == "visualizer"

    if is_visualizer:
        save_hud_style(resolved_key)
        v_voice = p.get("gemini_voice", "Charon")
        save_voice(v_voice)
        if player:
            if hasattr(player, "set_hud_style"):
                player.set_hud_style(resolved_key)
            if hasattr(player, "apply_ui_accent") and p.get("accent_color"):
                player.apply_ui_accent(p["accent_color"])
            if hasattr(player, "write_log"):
                player.write_log(f"SYS: Switched to visualizer — {p['name']} ({p['title']}).")
        return f"{p['name']} online. {p['desc']}"

    # Face Persona (renders original canonical 3D face model with persona voice & styling)
    save_face_model("original")
    save_hud_style("face")
    v_voice = p.get("gemini_voice", "Aoede")
    save_voice(v_voice)

    if player:
        if hasattr(player, "set_hud_style"):
            player.set_hud_style("face")
        if hasattr(player, "set_face_model"):
            player.set_face_model("original")
        if hasattr(player, "apply_ui_accent") and p.get("accent_color"):
            player.apply_ui_accent(p["accent_color"])
        if hasattr(player, "write_log"):
            player.write_log(f"SYS: Switched to persona — {p['name']} ({p['title']}).")

    if resolved_key == "ares":
        return "Ares online. Tactical Vanguard standing by, Commander. All perimeters secure."
    if resolved_key == "apollo":
        return "Apollo active! Systems primed and ready to innovate. What are we building today?"
    if resolved_key == "atlas":
        return "Atlas present, sir. Quantum architecture aligned. Proceeding with measured wisdom."
    if resolved_key == "seraphina":
        return "Seraphina at your service, darling. Always one step ahead... let's make this interesting."
    if resolved_key == "lumi":
        return "Lumi is here, Captain! All systems sparkle-ready! Let's do our best together!"

    return f"Switched to {p['name']} ({p['title']}). Voice model synchronized."


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "persona_control",
    "description": (
        "Switches the assistant's AI persona, 3D face model, sci-fi visualizer, HUD mode, or theme colors. "
        "Call this tool IMMEDIATELY whenever the user asks to switch face, change avatar, change persona, "
        "or activate a sci-fi visualizer like the Arc Reactor, Quantum Sphere, or Black Hole. "
        "Examples: 'switch to original face', 'activate Arc Reactor', 'switch visualizer to Black Hole', "
        "'show face', 'list visualizers'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "'switch_persona' (default, switches face/visualizer + matched voice + UI theme), "
                    "'set_face_model' (switches 3D face mesh), "
                    "'set_hud_style' (switches between face and faceless visualizers), "
                    "or 'list' (shows all available options)."
                ),
            },
            "name": {
                "type": "STRING",
                "description": (
                    "The name of the target mode or visualizer: "
                    "'original', 'face', or Sci-Fi Visualizers: 'arc_reactor', 'quantum_sphere', "
                    "'cyber_iris', 'tesseract', 'black_hole', 'neural_lotus'."
                ),
            },
        },
        "required": [],
    },
    "handler": persona_control,
}
