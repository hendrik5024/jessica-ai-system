"""Phase 13 — Knowledge Integration Layer: retriever."""

from __future__ import annotations

import logging
from typing import List

from jessica.knowledge_entry import KnowledgeEntry
from jessica.knowledge_store import KnowledgeStore

logger = logging.getLogger("jessica.knowledge")


class KnowledgeRetriever:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store

    def retrieve(self, topic: str) -> List[KnowledgeEntry]:
        results = self.store.search_by_topic(topic)
        logger.info("knowledge.retrieve", extra={"topic": topic})
        return results

    def retrieve_best_match(self, query: str) -> KnowledgeEntry | None:
        q = (query or "").strip().lower()
        if not q:
            return None

        exact = self.store.search_by_topic(q)
        if exact:
            logger.info("knowledge.retrieve_best_match", extra={"mode": "exact"})
            return exact[0]

        candidates = []
        for entry in self.store._entries.values():
            topic_l = entry.topic.lower()
            content_l = entry.content.lower()
            if q in topic_l or q in content_l:
                candidates.append(entry)
        candidates.sort(key=lambda e: (-e.version, e.entry_id))
        logger.info("knowledge.retrieve_best_match", extra={"mode": "substring"})
        return candidates[0] if candidates else None

    def retrieve_by_tags(self, tags: List[str]) -> List[KnowledgeEntry]:
        tags_l = [t.lower() for t in tags]
        results = []
        for entry in self.store._entries.values():
            entry_tags = [t.lower() for t in entry.tags]
            if any(tag in entry_tags for tag in tags_l):
                results.append(entry)
        results.sort(key=lambda e: (-e.version, e.entry_id))
        logger.info("knowledge.retrieve_by_tags", extra={"tags": tags})
        return results
