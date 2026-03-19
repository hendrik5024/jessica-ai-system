"""Phase 14 — Self-Improvement Governance: audit log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class AuditEntry:
    proposal_id: str
    module: str
    version: int
    timestamp: datetime


class ImprovementAudit:
    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    def record_change(self, proposal_id: str, module: str, version: int, timestamp: datetime) -> None:
        self._entries.append(
            AuditEntry(
                proposal_id=proposal_id,
                module=module,
                version=version,
                timestamp=timestamp,
            )
        )

    def get_change_history(self, module: str) -> List[AuditEntry]:
        return [entry for entry in self._entries if entry.module == module]

    def count(self) -> int:
        return len(self._entries)
