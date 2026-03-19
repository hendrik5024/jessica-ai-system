"""Phase 9.2 — Cognitive Memory Learning Layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import json


KNOWLEDGE_FILE = "jessica/memory/knowledge_memory.json"


@dataclass(frozen=True)
class KnowledgeItem:
    question: str
    answer: str
    created_at: datetime
    confidence: float = 0.7


class KnowledgeMemory:
    """Persistent, deterministic knowledge memory."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or KNOWLEDGE_FILE)
        self._store: Dict[str, KnowledgeItem] = {}
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        if not self.storage_path.exists():
            self._store = {}
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        store: Dict[str, KnowledgeItem] = {}
        for question, payload in data.items():
            store[question] = KnowledgeItem(
                question=payload["question"],
                answer=payload["answer"],
                created_at=datetime.fromisoformat(payload["created_at"]),
                confidence=float(payload.get("confidence", 0.7)),
            )
        self._store = store

    def save_to_disk(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            q: {
                "question": item.question,
                "answer": item.answer,
                "created_at": item.created_at.isoformat(),
                "confidence": item.confidence,
            }
            for q, item in sorted(self._store.items(), key=lambda kv: kv[0])
        }
        self.storage_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def learn(self, question: str, answer: str, confidence: float = 0.7) -> None:
        if not question or not question.strip():
            return
        if not answer or not answer.strip():
            return
        question = question.strip()
        answer = answer.strip()
        confidence = float(confidence)

        existing = self._store.get(question)
        if existing and confidence <= existing.confidence:
            return

        self._store[question] = KnowledgeItem(
            question=question,
            answer=answer,
            created_at=datetime.now(),
            confidence=confidence,
        )
        self.save_to_disk()

    def recall(self, question: str) -> Optional[str]:
        if not question:
            return None
        item = self._store.get(question)
        return item.answer if item else None

    def search(self, query: str) -> Optional[str]:
        if not query:
            return None
        q = query.lower().strip()
        if not q:
            return None
        candidates = []
        for question, item in self._store.items():
            question_l = question.lower()
            if q in question_l:
                candidates.append((question, item))
        if not candidates:
            return None
        candidates.sort(key=lambda pair: pair[0])
        return candidates[0][1].answer

    def count(self) -> int:
        return len(self._store)

    def _normalize_user_id(self, user_id: Optional[str]) -> str:
        normalized = str(user_id or "default").strip()
        return normalized if normalized else "default"

    def _fact_key(self, key: str, user_id: Optional[str]) -> str:
        normalized_user = self._normalize_user_id(user_id)
        return f"fact:user:{normalized_user}:{key}"

    def store_fact(self, key: str, value: str, user_id: Optional[str] = "default") -> None:
        if not key or value is None:
            return
        fact_key = self._fact_key(str(key), user_id)
        self._store[fact_key] = KnowledgeItem(
            question=fact_key,
            answer=str(value),
            created_at=datetime.now(),
            confidence=1.0,
        )
        self.save_to_disk()

    def get_fact(self, key: str, user_id: Optional[str] = "default"):
        scoped_value = self.recall(self._fact_key(str(key), user_id))
        if scoped_value is not None:
            return scoped_value

        normalized_user = self._normalize_user_id(user_id)
        if normalized_user == "default":
            return self.recall(str(key))

        return None
