import os
import time
import subprocess
import platform
import shutil
from pathlib import Path

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False

_SYSTEM = platform.system()

_APP_ALIASES: dict[str, dict[str, str]] = {

    "chrome":             {"Windows": "chrome",                  "Darwin": "Google Chrome",        "Linux": "google-chrome"},
    "google chrome":      {"Windows": "chrome",                  "Darwin": "Google Chrome",        "Linux": "google-chrome"},
    "firefox":            {"Windows": "firefox",                 "Darwin": "Firefox",              "Linux": "firefox"},
    "edge":               {"Windows": "msedge",                  "Darwin": "Microsoft Edge",       "Linux": "microsoft-edge"},
    "brave":              {"Windows": "brave",                   "Darwin": "Brave Browser",        "Linux": "brave-browser"},
    "safari":             {"Windows": "msedge",                  "Darwin": "Safari",               "Linux": "firefox"},
    "opera":              {"Windows": "opera",                   "Darwin": "Opera",                "Linux": "opera"},
    "whatsapp":           {"Windows": "WhatsApp",                "Darwin": "WhatsApp",             "Linux": "whatsapp"},
    "telegram":           {"Windows": "Telegram",                "Darwin": "Telegram",             "Linux": "telegram"},
    "discord":            {"Windows": "Discord",                 "Darwin": "Discord",              "Linux": "discord"},
    "slack":              {"Windows": "Slack",                   "Darwin": "Slack",                "Linux": "slack"},
    "zoom":               {"Windows": "Zoom",                    "Darwin": "zoom.us",              "Linux": "zoom"},
    "teams":              {"Windows": "msteams",                 "Darwin": "Microsoft Teams",      "Linux": "teams"},
    "skype":              {"Windows": "skype",                   "Darwin": "Skype",                "Linux": "skype"},
    "signal":             {"Windows": "signal",                  "Darwin": "Signal",               "Linux": "signal"},
    "spotify":            {"Windows": "Spotify",                 "Darwin": "Spotify",              "Linux": "spotify"},
    "vlc":                {"Windows": "vlc",                     "Darwin": "VLC",                  "Linux": "vlc"},
    "netflix":            {"Windows": "Netflix",                 "Darwin": "Netflix",              "Linux": "firefox"},
    "vscode":             {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "visual studio code": {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "code":               {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "terminal":           {"Windows": "wt",                      "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "cmd":                {"Windows": "cmd.exe",                 "Darwin": "Terminal",             "Linux": "bash"},
    "powershell":         {"Windows": "powershell.exe",          "Darwin": "Terminal",             "Linux": "bash"},
    "postman":            {"Windows": "Postman",                 "Darwin": "Postman",              "Linux": "postman"},
    "git":                {"Windows": "git-bash",                "Darwin": "Terminal",             "Linux": "bash"},
    "figma":              {"Windows": "Figma",                   "Darwin": "Figma",                "Linux": "figma"},
    "blender":            {"Windows": "blender",                 "Darwin": "Blender",              "Linux": "blender"},
    "word":               {"Windows": "winword",                 "Darwin": "Microsoft Word",       "Linux": "libreoffice --writer"},
    "excel":              {"Windows": "excel",                   "Darwin": "Microsoft Excel",      "Linux": "libreoffice --calc"},
    "powerpoint":         {"Windows": "powerpnt",                "Darwin": "Microsoft PowerPoint", "Linux": "libreoffice --impress"},
    "libreoffice":        {"Windows": "soffice",                 "Darwin": "LibreOffice",          "Linux": "libreoffice"},
    "notepad":            {"Windows": "notepad.exe",             "Darwin": "TextEdit",             "Linux": "gedit"},
    "textedit":           {"Windows": "notepad.exe",             "Darwin": "TextEdit",             "Linux": "gedit"},
    "explorer":           {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "file explorer":      {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "finder":             {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "task manager":       {"Windows": "taskmgr.exe",             "Darwin": "Activity Monitor",     "Linux": "gnome-system-monitor"},
    "settings":           {"Windows": "ms-settings:",            "Darwin": "System Preferences",   "Linux": "gnome-control-center"},
    "calculator":         {"Windows": "calc.exe",                "Darwin": "Calculator",           "Linux": "gnome-calculator"},
    "paint":              {"Windows": "mspaint.exe",             "Darwin": "Preview",              "Linux": "gimp"},
    "instagram":          {"Windows": "Instagram",               "Darwin": "Instagram",            "Linux": "firefox"},
    "tiktok":             {"Windows": "TikTok",                  "Darwin": "TikTok",               "Linux": "firefox"},
    "notion":             {"Windows": "Notion",                  "Darwin": "Notion",               "Linux": "notion"},
    "obsidian":           {"Windows": "Obsidian",                "Darwin": "Obsidian",             "Linux": "obsidian"},
    "capcut":             {"Windows": "CapCut",                  "Darwin": "CapCut",               "Linux": "capcut"},
    "steam":              {"Windows": "steam",                   "Darwin": "Steam",                "Linux": "steam"},
    "epic":               {"Windows": "EpicGamesLauncher",       "Darwin": "Epic Games Launcher",  "Linux": "legendary"},
    "epic games":         {"Windows": "EpicGamesLauncher",       "Darwin": "Epic Games Launcher",  "Linux": "legendary"},
}


def _normalize(raw: str) -> str:
    key = raw.lower().strip()

    if key in _APP_ALIASES:
        return _APP_ALIASES[key].get(_SYSTEM, raw)

    for alias_key, os_map in _APP_ALIASES.items():
        if alias_key in key or key in alias_key:
            return os_map.get(_SYSTEM, raw)

    return raw  

def _find_windows_app(app_name: str) -> str | None:
    """Finds an executable or .lnk shortcut for an application on Windows."""
    name_clean = app_name.lower().strip()
    if name_clean.endswith(".exe"):
        name_clean = name_clean[:-4]

    # 1. Check Start Menu .lnk shortcuts
    start_dirs = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("ALLUSERSPROFILE", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]
    for d in start_dirs:
        if d.exists():
            for lnk in d.rglob("*.lnk"):
                stem = lnk.stem.lower()
                if name_clean == stem or name_clean in stem:
                    return str(lnk)

    # 2. Check Windows Registry App Paths
    try:
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                k = winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
                num_keys = winreg.QueryInfoKey(k)[0]
                for i in range(num_keys):
                    sub = winreg.EnumKey(k, i)
                    sub_clean = sub.lower()
                    if sub_clean.endswith(".exe"):
                        sub_clean = sub_clean[:-4]
                    if name_clean == sub_clean or name_clean in sub_clean:
                        sk = winreg.OpenKey(k, sub)
                        val = winreg.QueryValue(sk, "")
                        clean_val = val.strip('"')
                        if clean_val and Path(clean_val).exists():
                            return clean_val
            except Exception:
                pass
    except Exception:
        pass

    # 3. Check AppData\Local\Programs
    local_prog = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
    if local_prog.exists():
        for p in local_prog.rglob("*.exe"):
            if name_clean == p.stem.lower() or name_clean in p.stem.lower():
                return str(p)

    return None


def _launch_windows(app_name: str) -> bool:
    # 1. URI protocols (e.g. ms-settings:, calc:, etc.)
    if ":" in app_name:
        try:
            os.startfile(app_name)
            time.sleep(1.0)
            return True
        except Exception:
            try:
                subprocess.Popen(f'start "" "{app_name}"', shell=True)
                time.sleep(1.0)
                return True
            except Exception:
                pass

    # 2. Direct path or Start Menu / Registry resolution
    target = _find_windows_app(app_name)
    if target:
        try:
            os.startfile(target)
            time.sleep(1.2)
            return True
        except Exception as e:
            print(f"[open_app] os.startfile failed for '{target}': {e}")

    # 3. PATH check via shutil.which
    which_bin = shutil.which(app_name) or shutil.which(app_name.split(".")[0])
    if which_bin:
        try:
            os.startfile(which_bin)
            time.sleep(1.2)
            return True
        except Exception:
            try:
                subprocess.Popen(app_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1.2)
                return True
            except Exception:
                pass

    # 4. Try Windows 'start' command
    try:
        p = subprocess.Popen(f'start "" "{app_name}"', shell=True)
        time.sleep(1.2)
        if p.poll() in (None, 0):
            return True
    except Exception:
        pass

    # 5. Fallback: Windows Start Menu search using clipboard (Unicode safe)
    try:
        import pyautogui
        pyautogui.PAUSE = 0.1
        pyautogui.press("win")
        time.sleep(0.6)
        if _PYPERCLIP:
            pyperclip.copy(app_name)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "v")
        else:
            pyautogui.write(app_name, interval=0.04)
        time.sleep(0.8)
        pyautogui.press("enter")
        time.sleep(2.0)
        return True
    except Exception as e:
        print(f"[open_app] Start Menu search failed: {e}")

    return False


def _launch_macos(app_name: str) -> bool:

    try:
        result = subprocess.run(
            ["open", "-a", app_name],
            capture_output=True, timeout=8
        )
        if result.returncode == 0:
            time.sleep(1.0)
            return True
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["open", "-a", f"{app_name}.app"],
            capture_output=True, timeout=8
        )
        if result.returncode == 0:
            time.sleep(1.0)
            return True
    except Exception:
        pass

    binary = shutil.which(app_name) or shutil.which(app_name.lower())
    if binary:
        try:
            subprocess.Popen(
                [binary],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1.0)
            return True
        except Exception:
            pass

    try:
        import pyautogui
        pyautogui.hotkey("command", "space")
        time.sleep(0.6)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.8)
        pyautogui.press("enter")
        time.sleep(1.5)
        return True
    except Exception as e:
        print(f"[open_app] Spotlight failed: {e}")

    return False


_LINUX_TERMINAL_FALLBACKS = [
    "x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal",
    "xterm", "lxterminal", "mate-terminal", "tilix", "alacritty", "kitty",
]

def _launch_linux(app_name: str) -> bool:

    # terminal emulators: try common ones in order
    if app_name in ("x-terminal-emulator", "gnome-terminal", "terminal"):
        for term in _LINUX_TERMINAL_FALLBACKS:
            if shutil.which(term):
                try:
                    subprocess.Popen([term], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(1.0)
                    return True
                except Exception:
                    continue

    binary = (
        shutil.which(app_name) or
        shutil.which(app_name.lower()) or
        shutil.which(app_name.lower().replace(" ", "-")) or
        shutil.which(app_name.lower().replace(" ", "_"))
    )
    if binary:
        try:
            subprocess.Popen(
                [binary],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1.0)
            return True
        except Exception:
            pass

    try:
        subprocess.run(
            ["xdg-open", app_name],
            capture_output=True, timeout=5
        )
        return True
    except Exception:
        pass

    for desktop_name in [
        app_name.lower(),
        app_name.lower().replace(" ", "-"),
        app_name.lower().replace(" ", ""),
    ]:
        try:
            result = subprocess.run(
                ["gtk-launch", desktop_name],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    return False


_OS_LAUNCHERS = {
    "Windows": _launch_windows,
    "Darwin":  _launch_macos,
    "Linux":   _launch_linux,
}

def _close_app(app_name: str) -> str:
    name_clean = app_name.lower().strip()
    if name_clean.endswith(".exe"):
        name_clean = name_clean[:-4]
    normalized = _normalize(name_clean).lower()
    if normalized.endswith(".exe"):
        normalized = normalized[:-4]

    targets = {name_clean, normalized}
    closed = []

    if _PSUTIL:
        for p in psutil.process_iter(["pid", "name"]):
            try:
                pname = p.info["name"].lower()
                pstem = pname[:-4] if pname.endswith(".exe") else pname
                for t in targets:
                    if t == pstem or t in pstem:
                        p.terminate()
                        closed.append(p.info["name"])
                        break
            except Exception:
                pass

    if _SYSTEM == "Windows" and not closed:
        for t in targets:
            try:
                res = subprocess.run(["taskkill", "/f", "/im", f"{t}.exe"], capture_output=True, timeout=5)
                if res.returncode == 0:
                    closed.append(f"{t}.exe")
            except Exception:
                pass

    if closed:
        return f"Closed {app_name}."
    return f"No active process found for '{app_name}'."


def open_app(
    parameters=None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    action = params.get("action", "open").lower().strip()
    app_name = params.get("app_name", "").strip()

    if not app_name:
        return "No application name provided."

    if action in ("close", "quit", "kill", "stop", "exit"):
        if player:
            player.write_log(f"[close_app] {app_name}")
        return _close_app(app_name)

    launcher = _OS_LAUNCHERS.get(_SYSTEM)
    if launcher is None:
        return f"Unsupported operating system: {_SYSTEM}"

    normalized = _normalize(app_name)
    print(f"[open_app] Launching: '{app_name}' -> '{normalized}' ({_SYSTEM})")

    if player:
        player.write_log(f"[open_app] {app_name}")

    try:
        if launcher(normalized):
            return f"Opened {app_name}."
        if normalized.lower() != app_name.lower():
            if launcher(app_name):
                return f"Opened {app_name}."
        return (
            f"Could not confirm that {app_name} launched. "
            f"It may still be loading, or it might not be installed."
        )
    except Exception as e:
        print(f"[open_app] Error: {e}")
        return f"Failed to open {app_name}: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "open_app",
    "description": "Opens or closes any application on the computer. Use this whenever the user asks to open, launch, start, close, quit, or kill any app, program, or website.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": "Exact name of the application (e.g. 'WhatsApp', 'Chrome', 'Spotify', 'Notepad', 'VS Code')"
            },
            "action": {
                "type": "STRING",
                "description": "'open' to launch (default) or 'close' to terminate the app"
            }
        },
        "required": [
            "app_name"
        ]
    },
    "handler": open_app,
}
