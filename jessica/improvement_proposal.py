"""Phase 14 — Self-Improvement Governance: proposal structure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class ImprovementProposal:
    proposal_id: str
    target_module: str
    description: str
    rationale: str
    risk_level: str
    proposed_changes: Dict
    created_at: datetime
