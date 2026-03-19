"""Phase 16 — Skill Acquisition Planning Layer: audit log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class SkillPlanRecord:
    skill_id: str
    plan_id: str
    timestamp: datetime


class SkillPlanningAudit:
    def __init__(self) -> None:
        self._records: List[SkillPlanRecord] = []

    def record_skill_plan(self, skill_id: str, plan_id: str, timestamp: datetime) -> None:
        self._records.append(
            SkillPlanRecord(skill_id=skill_id, plan_id=plan_id, timestamp=timestamp)
        )

    def get_skill_planning_history(self) -> List[SkillPlanRecord]:
        return list(self._records)

    def get_capability_gap_statistics(self) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        for record in self._records:
            stats[record.skill_id] = stats.get(record.skill_id, 0) + 1
        return stats

    def count(self) -> int:
        return len(self._records)
