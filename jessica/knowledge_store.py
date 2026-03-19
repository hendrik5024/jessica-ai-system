"""Phase 13 — Knowledge Integration Layer: append-only knowledge store."""

from __future__ import annotations

import logging
from typing import Dict, List

from jessica.knowledge_entry import KnowledgeEntry

logger = logging.getLogger("jessica.knowledge")


class KnowledgeStore:
    def __init__(self) -> None:
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._order: List[str] = []

    def add_entry(self, entry: KnowledgeEntry) -> None:
        if entry.entry_id in self._entries:
            raise ValueError("Entry already exists")
        self._entries[entry.entry_id] = entry
        self._order.append(entry.entry_id)
        logger.info("knowledge.add_entry", extra={"entry_id": entry.entry_id})

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        entry = self._entries.get(entry_id)
        logger.info("knowledge.get_entry", extra={"entry_id": entry_id})
        return entry

    def search_by_topic(self, topic: str) -> List[KnowledgeEntry]:
        topic_l = (topic or "").strip().lower()
        results = [
            entry for entry in self._entries.values()
            if entry.topic.lower() == topic_l
        ]
        results.sort(key=lambda e: (-e.version, e.entry_id))
        logger.info("knowledge.search_by_topic", extra={"topic": topic})
        return results

    def search_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        tag_l = (tag or "").strip().lower()
        results = [
            entry for entry in self._entries.values()
            if any(t.lower() == tag_l for t in entry.tags)
        ]
        results.sort(key=lambda e: (-e.version, e.entry_id))
        logger.info("knowledge.search_by_tag", extra={"tag": tag})
        return results

    def list_topics(self) -> List[str]:
        topics = sorted({entry.topic for entry in self._entries.values()})
        logger.info("knowledge.list_topics")
        return topics

    def count(self) -> int:
        return len(self._entries)
