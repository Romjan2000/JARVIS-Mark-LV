"""
tools/chrome_launcher.py — Chrome DevTools Protocol (CDP) Launcher and Health Detector.

Enables JARVIS to attach directly to the user's running Chrome browser,
preserving all user profiles, extensions, cookies, and logged-in accounts
(Facebook, YouTube, Messenger, etc.) with zero profile-locking conflicts.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

_OS = platform.system()


def is_cdp_available(port: int = 9222) -> bool:
    """Checks if Chrome DevTools Protocol is reachable on the given port."""
    url = f"http://127.0.0.1:{port}/json/version"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-CDP-Probe"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_cdp_version_info(port: int = 9222) -> dict:
    """Retrieves Chrome version, browser details, and WebSocket debugger URL."""
    url = f"http://127.0.0.1:{port}/json/version"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-CDP-Probe"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}
    return {}


def find_chrome_executable() -> Optional[str]:
    """Finds the Google Chrome executable on the system."""
    if _OS == "Windows":
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
        for p in candidates:
            if p.exists():
                return str(p)

        try:
            import winreg
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    k = winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                    val, _ = winreg.QueryValueEx(k, "")
                    winreg.CloseKey(k)
                    exe = val.strip().strip('"')
                    if exe and Path(exe).exists():
                        return exe
                except Exception:
                    continue
        except Exception:
            pass

    elif _OS == "Darwin":
        p = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if p.exists():
            return str(p)
    else:
        for b in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
            found = shutil.which(b)
            if found:
                return found

    return shutil.which("chrome") or None


def launch_chrome_with_cdp(port: int = 9222, url: Optional[str] = None) -> bool:
    """
    Launches Chrome with remote debugging enabled.
    Uses the user's regular Chrome profile so all saved logins/cookies are available.
    """
    if is_cdp_available(port):
        return True

    exe = find_chrome_executable()
    if not exe:
        print("[ChromeLauncher] Chrome executable not found.")
        return False

    cmd = [
        exe,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--restore-last-session",
    ]
    if url:
        cmd.append(url)

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS if _OS == "Windows" else 0,
        )
        print(f"[ChromeLauncher] Started Chrome with CDP on port {port}.")
        return True
    except Exception as e:
        print(f"[ChromeLauncher] Failed to start Chrome: {e}")
        return False
