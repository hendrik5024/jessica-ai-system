from .long_horizon_plan_record import LongHorizonPlanRecord
from jessica.executive.oversight_record import ExecutiveOversightRecord


class LongHorizonPlanEngine:

    def generate(
        self,
        plan_id: str,
        oversight: ExecutiveOversightRecord,
    ) -> LongHorizonPlanRecord:

        if oversight.guardrail_state == "ACTIVE":
            state = "STABILITY_PRIORITY"
        else:
            state = "NORMAL_STRATEGIC_FLOW"

        return LongHorizonPlanRecord(
            plan_id,
            state,
            "EXTENDED",
            "Long-horizon governance advisory",
        )
