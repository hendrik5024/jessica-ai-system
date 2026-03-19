"""Phase 5.4 Recovery Option (data-only)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RecoveryOption:
    description: str
    suggested_manual_action: str
    risk_level: RecoveryRisk
    reversibility_score: float
    requires_new_intent: bool
