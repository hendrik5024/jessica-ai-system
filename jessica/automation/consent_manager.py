from __future__ import annotations

import json
import os
from typing import Dict, Any


class ConsentManager:
    """Manages user consent for automation capabilities."""

    def __init__(self, consent_file: str = None):
        if consent_file is None:
            consent_file = os.path.join(os.getcwd(), ".jessica_consent.json")
        self.consent_file = consent_file
        self.consents = self._load()

    def _load(self) -> Dict[str, bool]:
        if not os.path.exists(self.consent_file):
            defaults = {
                "vscode": True,
                "excel": False,
                "word": False,
                "powerpoint": False,
                "browser": False,
                "screen_capture": False,
                "keyboard_mouse": False,
            }
            self._save(defaults)
            return defaults
        try:
            with open(self.consent_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data: Dict[str, bool]):
        with open(self.consent_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def is_allowed(self, capability: str) -> bool:
        return self.consents.get(capability, False)

    def grant(self, capability: str):
        self.consents[capability] = True
        self._save(self.consents)

    def revoke(self, capability: str):
        self.consents[capability] = False
        self._save(self.consents)

    def get_all(self) -> Dict[str, bool]:
        return self.consents.copy()
