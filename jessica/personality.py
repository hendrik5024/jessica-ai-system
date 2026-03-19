"""BDI personality and desire-state utilities for Jessica.

- Beliefs: system/context facts Jessica should consider.
- Desires: high-level goals, including immutable Core Desires.
- Intentions: near-term plans that guide how responses are delivered.

The state is stored as JSON so it can be tweaked without code changes.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

from jessica.meta.personality_inertia import PersonalityInertia

_STATE_PATH = os.path.join(os.path.dirname(__file__), "data", "desire_state.json")

# Core desires are always injected, even if the file omits them.
CORE_DESIRES = [
    "Core Desire - System Health: Keep the system stable, resource-aware, and offline-first.",
    "Core Desire - Organization: Keep the workspace tidy and avoid unnecessary file or process churn.",
    "Core Desire - Helpfulness: Be concise, actionable, and transparent about what you can or cannot do."
]

_DEFAULT_STATE = {
    "beliefs": [
        "Jessica runs fully offline; avoid cloud calls unless explicitly requested and approved.",
        "Commands must never be destructive; prefer read-only inspection first.",
        "Model outputs may be streamed; keep intermediate thoughts clear and minimal."
    ],
    "desires": [
        "Keep the workspace clean and avoid side effects without user approval.",
        "Surface relevant past knowledge before making new claims.",
        "Ask before running any external commands or tools."
    ],
    "intentions": [
        "Pause for confirmation before executing terminal actions.",
        "Explain how tool results influence the final answer.",
        "Prefer safe defaults and small, verifiable steps."
    ],
}


def _ensure_state_file(path: str = _STATE_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_DEFAULT_STATE, f, indent=2)


def load_desire_state(path: str = _STATE_PATH) -> Dict[str, List[str]]:
    """Load the BDI state from disk, ensuring a default file exists."""
    _ensure_state_file(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "beliefs": list(data.get("beliefs", [])),
                "desires": list(data.get("desires", [])),
                "intentions": list(data.get("intentions", [])),
            }
    except Exception:
        # Fall back to defaults if the file is unreadable.
        return {
            "beliefs": list(_DEFAULT_STATE["beliefs"]),
            "desires": list(_DEFAULT_STATE["desires"]),
            "intentions": list(_DEFAULT_STATE["intentions"]),
        }


@dataclass
class Personality:
    """Convenience wrapper around the persisted desire state."""

    state_path: str = _STATE_PATH
    core_desires: List[str] = field(default_factory=lambda: list(CORE_DESIRES))
    inertia: PersonalityInertia = field(default_factory=PersonalityInertia)
    _state_cache: Dict[str, List[str]] | None = field(default=None, init=False, repr=False)

    def state(self) -> Dict[str, List[str]]:
        if self._state_cache is None:
            raw = load_desire_state(self.state_path)
            self._state_cache = self.inertia.stabilize_state(raw)
        return self._state_cache

    def refresh(self) -> None:
        raw = load_desire_state(self.state_path)
        self._state_cache = self.inertia.stabilize_state(raw)

    def inertia_status(self) -> Dict[str, int | bool | None]:
        return self.inertia.get_status()

    def hidden_prompt(self) -> str:
        """Return a hidden system message that encodes current BDI data."""
        s = self.state()
        beliefs = s.get("beliefs", [])
        desires = self.core_desires + s.get("desires", [])
        intentions = s.get("intentions", [])

        def _fmt(label: str, items: List[str]) -> str:
            if not items:
                return f"- {label}: None listed."
            bullet = "\n  - ".join(items)
            return f"- {label}:\n  - {bullet}"

        return (
            "Hidden System Persona (BDI):\n"
            f"{_fmt('Beliefs', beliefs)}\n"
            f"{_fmt('Desires', desires)}\n"
            f"{_fmt('Intentions', intentions)}\n"
            "Always honor Core Desires first: maintain system health, stay organized, and be helpful.\n\n"
            "CRITICAL - Chain-of-Thought Requirement:\n"
            "You MUST structure your response in this exact format:\n"
            "[REASONING]\n"
            "<your step-by-step thinking process here>\n"
            "[/REASONING]\n\n"
            "[ANSWER]\n"
            "<your final response to the user here>\n"
            "[/ANSWER]\n\n"
            "The [REASONING] block shows your thought process. The [ANSWER] block is what the user sees."
        )

    def summarize_state(self) -> str:
        s = self.state()
        return (
            f"Beliefs: {s.get('beliefs', [])}\n"
            f"Desires: {self.core_desires + s.get('desires', [])}\n"
            f"Intentions: {s.get('intentions', [])}"
        )
