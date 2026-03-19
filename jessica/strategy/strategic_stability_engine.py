from .strategic_stability_record import StrategicStabilityRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicStabilityEngine:

    def evaluate(
        self,
        stability_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicStabilityRecord:

        count = len(plans)

        if count < 5:
            level = "STABLE"
        elif count < 15:
            level = "MODERATE_LOAD"
        else:
            level = "HIGH_LOAD"

        return StrategicStabilityRecord(
            stability_id,
            count,
            level,
            "Strategic stability advisory",
        )
