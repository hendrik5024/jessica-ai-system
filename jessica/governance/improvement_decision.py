from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ImprovementDecision:
    proposal_id: str
    approved: bool
    reviewer: str
    decision_reason: str
    decided_at: datetime
