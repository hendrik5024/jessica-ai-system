from .strategic_stability_engine import StrategicStabilityEngine
from .strategic_stability_record import StrategicStabilityRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicStabilityOrchestrator:

    def __init__(self):
        self.engine = StrategicStabilityEngine()

    def evaluate(
        self,
        stability_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicStabilityRecord:

        return self.engine.evaluate(stability_id, plans)
