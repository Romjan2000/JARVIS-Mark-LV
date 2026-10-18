"""
system_command.py — Arbitrary system, shell, and PowerShell command execution.

Provides JARVIS with direct command-line interaction with the host PC.
Auto-discovered by core/action_loader.py.
"""
from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

_OS = platform.system()

def run_command(
    command: str,
    shell_type: str = "powershell",
    timeout: int = 30,
    working_dir: Optional[str] = None,
) -> str:
    """Execute a system shell command safely and return formatted output."""
    if not command or not command.strip():
        return "No command provided to execute."

    cmd = command.strip()
    timeout = max(1, min(int(timeout), 120))
    cwd = None

    if working_dir:
        try:
            cwd_path = Path(working_dir).expanduser().resolve()
            if cwd_path.exists() and cwd_path.is_dir():
                cwd = str(cwd_path)
        except Exception:
            pass

    st = (shell_type or "").lower().strip()
    creationflags = 0

    if _OS == "Windows":
        creationflags = subprocess.CREATE_NO_WINDOW
        if st in ("cmd", "batch"):
            args = ["cmd.exe", "/c", cmd]
        elif st in ("bash", "sh", "git-bash"):
            # Try git bash or wsl if explicitly requested
            git_bash = r"C:\Program Files\Git\bin\bash.exe"
            if os.path.exists(git_bash):
                args = [git_bash, "-c", cmd]
            else:
                args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd]
        else:
            # Default to PowerShell for Windows
            args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", cmd]
    else:
        # Linux / macOS
        shell_bin = "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"
        args = [shell_bin, "-c", cmd]

    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            creationflags=creationflags,
        )

        encoding = "utf-8"
        if _OS == "Windows":
            # Fall back through common Windows encodings
            out_bytes = proc.stdout
            err_bytes = proc.stderr
            stdout = out_bytes.decode("utf-8", errors="replace")
            stderr = err_bytes.decode("utf-8", errors="replace")
        else:
            stdout = proc.stdout.decode("utf-8", errors="replace")
            stderr = proc.stderr.decode("utf-8", errors="replace")

        output_parts = []
        if stdout.strip():
            output_parts.append(stdout.strip())
        if stderr.strip():
            output_parts.append(f"[STDERR]:\n{stderr.strip()}")

        result = "\n".join(output_parts) if output_parts else "Command executed successfully with no output."

        # Cap output length so it doesn't flood LLM token limits
        _MAX_LEN = 3500
        if len(result) > _MAX_LEN:
            result = result[:_MAX_LEN] + f"\n... [Output truncated. Total: {len(result)} chars]"

        status = f"(Exit code: {proc.returncode})" if proc.returncode != 0 else ""
        return f"{result}\n{status}".strip()

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds: '{cmd}'"
    except Exception as e:
        return f"Command execution failed: {e}"


def system_command(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    cmd = params.get("command", "").strip()
    shell_type = params.get("shell", "powershell").strip()
    timeout = int(params.get("timeout", 30))
    working_dir = params.get("working_dir")

    if not cmd:
        return "Please provide a command to run, sir."

    print(f"[SystemCommand] Running ({shell_type}): {cmd[:100]}")
    if player:
        player.write_log(f"[CLI]: {cmd[:60]}")

    result = run_command(cmd, shell_type=shell_type, timeout=timeout, working_dir=working_dir)
    return result


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "system_command",
    "description": (
        "Executes shell, PowerShell, or terminal commands directly on this computer and returns "
        "the output. Use whenever the user asks to run a command, check network/IP/system status via CLI, "
        "execute scripts, manage processes, check disk/RAM via command line, install packages, or perform "
        "any PC command-line operation."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "command": {
                "type": "STRING",
                "description": "The exact shell/PowerShell/CMD command to run (e.g. 'ipconfig', 'Get-Process', 'ping google.com', 'dir')."
            },
            "shell": {
                "type": "STRING",
                "description": "Shell type: 'powershell' (default on Windows), 'cmd', or 'bash'."
            },
            "timeout": {
                "type": "INTEGER",
                "description": "Timeout in seconds (default: 30)."
            },
            "working_dir": {
                "type": "STRING",
                "description": "Optional working directory path to run the command in."
            }
        },
        "required": [
            "command"
        ]
    },
    "handler": system_command,
}
