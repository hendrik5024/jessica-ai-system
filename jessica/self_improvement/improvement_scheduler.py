from datetime import datetime
from typing import List

from .improvement_schedule_record import ImprovementScheduleRecord


class ImprovementScheduler:
    def __init__(self):
        self._schedule: List[ImprovementScheduleRecord] = []

    def schedule(self, proposal_id: str, when: datetime):
        record = ImprovementScheduleRecord(
            proposal_id=proposal_id,
            scheduled_for=when,
            created_at=datetime.utcnow(),
        )

        self._schedule.append(record)
        return record

    def list_schedule(self):
        return list(self._schedule)
