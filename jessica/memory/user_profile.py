"""
User Profile & Entity Memory: Stores names, places, relationships, preferences.
Persists across sessions and grows with each interaction.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any

PROFILE_PATH = Path(__file__).resolve().parent.parent / "data" / "user_profile.json"

class UserProfile:
    def __init__(self):
        self.path = PROFILE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.load(open(self.path, "r", encoding="utf-8"))
            except Exception:
                return self._default()
        return self._default()

    def _default(self) -> dict:
        return {
            "user_name": None,
            "names_mentioned": {},  # {"John": {"context": "friend", "count": 2}, ...}
            "places": {},            # {"Paris": {"context": "visited", "count": 1}, ...}
            "preferences": {},       # {"likes": ["coffee"], "dislikes": [...]}
            "preferences_history": [],  # [{"ts": 123, "preferences": {...}}, ...]
            "relationships": {},     # {"Alice": "sister", "Bob": "coworker"}
            "last_update": None
        }

    def save(self):
        import time
        now = time.time()
        
        # Track preference changes in history
        if self.data.get("preferences"):
            history = self.data.get("preferences_history", [])
            if not history or history[-1].get("preferences") != self.data["preferences"]:
                history.append({
                    "ts": int(now),
                    "preferences": dict(self.data["preferences"])
                })
                self.data["preferences_history"] = history[-20:]  # Keep last 20 snapshots
        
        self.data["last_update"] = now
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_name(self, name: str, context: str = None):
        """Record a person mentioned."""
        if name and len(name) > 1:
            if name not in self.data["names_mentioned"]:
                self.data["names_mentioned"][name] = {"context": context or "", "count": 0}
            self.data["names_mentioned"][name]["count"] += 1
            if context:
                self.data["names_mentioned"][name]["context"] = context

    def add_place(self, place: str, context: str = None):
        """Record a place mentioned."""
        if place and len(place) > 1:
            if place not in self.data["places"]:
                self.data["places"][place] = {"context": context or "", "count": 0}
            self.data["places"][place]["count"] += 1
            if context:
                self.data["places"][place]["context"] = context

    def set_user_name(self, name: str):
        self.data["user_name"] = name

    def set_relationship(self, name: str, relation: str):
        self.data["relationships"][name] = relation

    def get_known_entities(self) -> str:
        """Return a formatted summary of known names/places for context."""
        lines = []
        if self.data["user_name"]:
            lines.append(f"User's name: {self.data['user_name']}")
        
        known_names = ", ".join(sorted(self.data["names_mentioned"].keys())[:10])
        if known_names:
            lines.append(f"People mentioned: {known_names}")
        
        known_places = ", ".join(sorted(self.data["places"].keys())[:5])
        if known_places:
            lines.append(f"Places mentioned: {known_places}")
        
        rels = ", ".join([f"{k} ({v})" for k, v in list(self.data["relationships"].items())[:5]])
        if rels:
            lines.append(f"Relationships: {rels}")
        
        return "\n".join(lines) if lines else "No entities recorded yet."

    def extract_entities(self, text: str):
        """Simple heuristic to extract names and places (can be enhanced with NER)."""
        import re
        # Capitalized words are likely names/places
        caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for token in caps:
            if len(token) > 2:
                # Very basic heuristic: if followed by "is" or "from", likely a name/relationship
                if f"{token} is" in text or f"{token}'s" in text:
                    self.add_name(token)
                elif f"in {token}" in text or f"to {token}" in text or f"from {token}" in text:
                    self.add_place(token)
