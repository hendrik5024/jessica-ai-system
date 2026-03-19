"""Phase 15 — Cognitive Strategy Layer: strategy definition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class StrategyDefinition:
    strategy_id: str
    name: str
    description: str
    selection_rules: Dict
    reasoning_steps: List[str]
    created_at: datetime
