from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ImprovementProposal:
    proposal_id: str
    capability_name: str
    description: str
    expected_benefit: str
    potential_risk: str
    created_at: datetime
