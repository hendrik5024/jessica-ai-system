"""Safe, whitelisted terminal commands for Jessica's agency layer."""
from __future__ import annotations

import shlex
import subprocess
import sys
from typing import Tuple

# Strict whitelist of allowed commands.
ALLOWED_COMMANDS = {"ls", "dir", "echo", "date", "tasklist", "uptime"}


def confirm_and_run(command: str) -> Tuple[bool, str]:
    """Confirm with the user, then run a whitelisted command securely.

    Returns a tuple (ran, output). The command is only executed if it is
    explicitly allowed and the user confirms execution.
    """
    parts = shlex.split(command)
    if not parts:
        return False, "[tools] No command provided."

    base = parts[0]
    if base not in ALLOWED_COMMANDS:
        return False, f"[tools] Command '{base}' is not allowed. Allowed: {sorted(ALLOWED_COMMANDS)}"

    print(f"[tools] Requested command: {command}")

    if sys.stdin is None or not sys.stdin.isatty():
        return False, "[tools] Command requires interactive approval; denied (non-interactive session)."

    proceed = input("Approve command? [y/N]: ").strip().lower()
    if proceed not in {"y", "yes"}:
        return False, "[tools] Command was not approved."

    try:
        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"[tools] Failed to execute: {exc}"

    output = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if err:
        output = f"{output}\n[stderr]\n{err}".strip()

    return True, output or "(no output)"
