from dataclasses import dataclass


@dataclass(frozen=True)
class PlanEvaluation:
    plan_id: str
    score: float
    reasoning: str
