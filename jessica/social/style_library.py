"""
Style Library captures user linguistic tics to mirror tone.
Stores a few lightweight stats and surfaces a style hint for prompts.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from typing import Dict, List


def _tokenize(text: str) -> List[str]:
    return [t.strip(".,!?;:") for t in text.lower().split() if t]


class StyleLibrary:
    def __init__(self, state_path: str | None = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(os.path.dirname(base_dir), "data", "style_state.json")
        self.state_path = state_path or default_path
        self.state = {
            "adjectives": Counter(),
            "closures": Counter(),
            "formality": 0.5,  # 0 informal, 1 formal
            "seen": 0,
        }
        self._load()

    # -------------------------------------------------
    # Persistence
    # -------------------------------------------------
    def _load(self):
        try:
            if os.path.isfile(self.state_path):
                with open(self.state_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.state["adjectives"] = Counter(raw.get("adjectives", {}))
                    self.state["closures"] = Counter(raw.get("closures", {}))
                    self.state["formality"] = raw.get("formality", 0.5)
                    self.state["seen"] = raw.get("seen", 0)
        except Exception:
            pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "adjectives": dict(self.state["adjectives"]),
                        "closures": dict(self.state["closures"]),
                        "formality": self.state["formality"],
                        "seen": self.state["seen"],
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

    # -------------------------------------------------
    # Updates
    # -------------------------------------------------
    def update_from_user(self, text: str):
        tokens = _tokenize(text)
        self.state["seen"] += 1

        # Heuristic: adjectives end with 'y' or common casual words
        for t in tokens:
            if len(t) >= 4 and (t.endswith("y") or t in {"cool", "nice", "great", "solid", "quick"}):
                self.state["adjectives"][t] += 1

        # Closures / discourse markers
        for marker in ["thanks", "thx", "cheers", "appreciate", "cool", "done", "ok"]:
            if marker in tokens:
                self.state["closures"][marker] += 1

        # Formality: presence of contractions vs. formal starts
        contractions = sum(1 for t in tokens if "'" in t)
        capitals = 1 if text[:1].isupper() else 0
        formality_score = 0.5
        if contractions > 0:
            formality_score -= 0.1
        if capitals:
            formality_score += 0.05
        self.state["formality"] = min(1.0, max(0.0, (self.state["formality"] * 0.9) + formality_score * 0.1))

        self._save()

    # -------------------------------------------------
    # Hints
    # -------------------------------------------------
    def style_hint(self) -> str:
        top_adj = ""
        if self.state["adjectives"]:
            top_adj = max(self.state["adjectives"].items(), key=lambda x: x[1])[0]
        top_closure = ""
        if self.state["closures"]:
            top_closure = max(self.state["closures"].items(), key=lambda x: x[1])[0]

        tone = "casual" if self.state["formality"] < 0.5 else "neutral"
        parts: List[str] = []
        parts.append(f"Tone: {tone}")
        if top_adj:
            parts.append(f"Adjective: {top_adj}")
        if top_closure:
            parts.append(f"Closure: use '{top_closure}' optionally")
        return " | ".join(parts)
