"""Phase 16 — Skill Acquisition Planning Layer: skill definition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    name: str
    description: str
    capability_domain: str
    prerequisites: List[str]
    estimated_complexity: str
    created_at: datetime
