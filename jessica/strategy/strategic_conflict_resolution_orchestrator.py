from .strategic_conflict_resolution_engine import StrategicConflictResolutionEngine
from .strategic_conflict_resolution_record import StrategicConflictResolutionRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicConflictResolutionOrchestrator:

    def __init__(self):
        self.engine = StrategicConflictResolutionEngine()

    def resolve(
        self,
        resolution_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicConflictResolutionRecord:

        return self.engine.resolve(resolution_id, plans)
