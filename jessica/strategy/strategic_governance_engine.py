from .strategic_governance_record import StrategicGovernanceRecord
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


class StrategicGovernanceEngine:

    def evaluate(
        self,
        governance_id: str,
        plans: list[LongHorizonPlanRecord],
    ) -> StrategicGovernanceRecord:

        if len(plans) <= 1:
            state = "STABLE"
        else:
            state = "MULTI_PLAN_BALANCING"

        return StrategicGovernanceRecord(
            governance_id,
            len(plans),
            state,
            "Strategic governance advisory",
        )
