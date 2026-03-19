"""Phase 15 — Cognitive Strategy Layer: audit log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class StrategyUse:
    task_id: str
    strategy_id: str
    timestamp: datetime


class StrategyAudit:
    def __init__(self) -> None:
        self._records: List[StrategyUse] = []

    def record_strategy_use(self, task_id: str, strategy_id: str, timestamp: datetime) -> None:
        self._records.append(StrategyUse(task_id=task_id, strategy_id=strategy_id, timestamp=timestamp))

    def get_strategy_history(self, task_id: str) -> List[StrategyUse]:
        return [r for r in self._records if r.task_id == task_id]

    def get_strategy_usage_statistics(self) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        for record in self._records:
            stats[record.strategy_id] = stats.get(record.strategy_id, 0) + 1
        return stats

    def count(self) -> int:
        return len(self._records)
