"""Phase 13 — Knowledge Integration Layer: entry structure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class KnowledgeEntry:
    entry_id: str
    topic: str
    content: str
    tags: List[str]
    version: int
    created_at: datetime
