from dataclasses import dataclass
from statistics import mean, pvariance
from time import time
from typing import List

from jessica.planning.meta_planner import PlanEvaluation
from jessica.reasoning.goal_decomposer import Goal


@dataclass(frozen=True)
class PlanningRecord:
    record_id: str
    goal_id: str
    selected_plan_id: str
    predicted_score: float
    timestamp: float


@dataclass(frozen=True)
class PlanningMetrics:
    total_plans: int
    average_predicted_score: float
    reliability_index: float


class PlanningPerformanceMonitor:

    def __init__(self):
        self._records: List[PlanningRecord] = []

    def record_plan_selection(self, goal: Goal, evaluation: PlanEvaluation) -> PlanningRecord:
        record = PlanningRecord(
            record_id=f"record-{goal.goal_id}-{len(self._records) + 1}",
            goal_id=goal.goal_id,
            selected_plan_id=evaluation.selected_plan_id,
            predicted_score=evaluation.score,
            timestamp=time(),
        )
        self._records.append(record)
        return record

    def compute_metrics(self) -> PlanningMetrics:
        if not self._records:
            return PlanningMetrics(total_plans=0, average_predicted_score=0.0, reliability_index=0.0)

        scores = [record.predicted_score for record in self._records]
        avg = mean(scores)
        variance = pvariance(scores)
        reliability = avg / (1 + variance)

        return PlanningMetrics(
            total_plans=len(self._records),
            average_predicted_score=avg,
            reliability_index=reliability,
        )

    def history(self) -> List[PlanningRecord]:
        return list(self._records)
