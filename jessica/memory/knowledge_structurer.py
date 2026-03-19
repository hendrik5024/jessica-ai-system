"""Phase 9.4 — Structured Knowledge Formation."""

from __future__ import annotations

import re
from typing import Optional, Tuple

from .knowledge_memory import KnowledgeMemory


class KnowledgeStructurer:
    """Rule-based structured fact extractor and storer."""

    def __init__(self, memory: KnowledgeMemory):
        self.memory = memory

    def extract_fact(self, user_input: str) -> Optional[Tuple[str, str]]:
        if not user_input:
            return None
        text = user_input.strip()
        lowered = text.lower()

        patterns = [
            (r"^my name is\s+(.+)$", "user_name"),
            (r"^your name is\s+(.+)$", "assistant_name"),
            (r"^i live in\s+(.+)$", "user_location"),
            (r"^i work as\s+(.+)$", "user_profession"),
        ]

        for pattern, key in patterns:
            match = re.match(pattern, lowered, flags=re.IGNORECASE)
            if match:
                value = match.group(1).strip().rstrip(".")
                return key, value

        return None

    def store_fact(self, key: str, value: str) -> None:
        if not key or not value:
            return
        self.memory.learn(f"fact:{key}", value)

    def process_input(self, user_input: str) -> None:
        fact = self.extract_fact(user_input)
        if fact:
            self.store_fact(*fact)
