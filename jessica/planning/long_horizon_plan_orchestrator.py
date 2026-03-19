from .long_horizon_plan_engine import LongHorizonPlanEngine
from .long_horizon_plan_record import LongHorizonPlanRecord
from jessica.executive.oversight_record import ExecutiveOversightRecord


class LongHorizonPlanOrchestrator:

    def __init__(self):
        self.engine = LongHorizonPlanEngine()

    def generate(
        self,
        plan_id: str,
        oversight: ExecutiveOversightRecord,
    ) -> LongHorizonPlanRecord:

        return self.engine.generate(plan_id, oversight)
