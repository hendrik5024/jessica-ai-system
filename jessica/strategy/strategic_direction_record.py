from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class StrategicDirectionRecord:
    direction_id: str
    description: str
    priority_level: int
    created_at: datetime
    metadata: Dict[str, str]
