from dataclasses import dataclass


@dataclass(frozen=True)
class LongHorizonPlanRecord:
    plan_id: str
    strategic_state: str
    planning_horizon: str
    advisory: str
