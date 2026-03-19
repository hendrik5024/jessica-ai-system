from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ImprovementScheduleRecord:
    proposal_id: str
    scheduled_for: datetime
    created_at: datetime
