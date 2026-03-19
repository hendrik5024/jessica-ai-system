from .strategic_governance_engine import StrategicGovernanceEngine
from .strategic_governance_record import StrategicGovernanceRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicGovernanceOrchestrator:

    def __init__(self):
        self.engine = StrategicGovernanceEngine()

    def evaluate(
        self,
        governance_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicGovernanceRecord:

        return self.engine.evaluate(governance_id, plans)
