"""Phase 13 — Knowledge Integration Layer: orchestrator."""

from __future__ import annotations

import logging
from typing import Dict, Any, List

from jessica.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger("jessica.knowledge")


class KnowledgeOrchestrator:
    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self.retriever = retriever

    def answer_query(self, query: str) -> Dict[str, Any]:
        entry = self.retriever.retrieve_best_match(query)
        if not entry:
            return {"content": None, "confidence": 0.0, "entry_id": None}

        confidence = 0.9 if entry.topic.lower() == (query or "").strip().lower() else 0.7
        logger.info("knowledge.answer_query", extra={"entry_id": entry.entry_id})
        return {"content": entry.content, "confidence": confidence, "entry_id": entry.entry_id}

    def answer_topic(self, topic: str) -> Dict[str, Any]:
        entries = self.retriever.retrieve(topic)
        if not entries:
            return {"content": None, "confidence": 0.0, "entry_id": None}
        entry = entries[0]
        logger.info("knowledge.answer_topic", extra={"entry_id": entry.entry_id})
        return {"content": entry.content, "confidence": 0.9, "entry_id": entry.entry_id}

    def retrieve_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        entries = self.retriever.retrieve_by_tags(tags)
        return [
            {"content": entry.content, "confidence": 0.8, "entry_id": entry.entry_id}
            for entry in entries
        ]
