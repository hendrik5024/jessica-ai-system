"""Phase 9.3 — Cognitive Recall Bridge."""

from __future__ import annotations

from typing import Optional

from .knowledge_memory import KnowledgeMemory


class CognitiveRecallBridge:
    """Deterministic recall bridge for knowledge-augmented responses."""

    def __init__(self, memory: KnowledgeMemory):
        self.memory = memory

    def recall_or_search(self, query: str) -> Optional[str]:
        result = self.memory.recall(query)
        if result:
            return result
        return self.memory.search(query)

    def augment_response(self, query: str, base_response: str) -> str:
        recalled = self.recall_or_search(query)
        if recalled:
            return f"From what I have learned: {recalled}. {base_response}"
        return base_response
