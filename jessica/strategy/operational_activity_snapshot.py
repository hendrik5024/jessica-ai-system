from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class OperationalActivitySnapshot:
    snapshot_id: str
    current_focus: str
    active_goals: Tuple[str, ...]
    timestamp: datetime
