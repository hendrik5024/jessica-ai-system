from .strategic_conflict_resolution_record import StrategicConflictResolutionRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicConflictResolutionEngine:

    def resolve(
        self,
        resolution_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicConflictResolutionRecord:

        if len(plans) <= 1:
            strategy = "NO_CONFLICT"
        else:
            strategy = "PRIORITIZE_STABILITY"

        return StrategicConflictResolutionRecord(
            resolution_id,
            len(plans),
            strategy,
            "Strategic conflict advisory",
        )
