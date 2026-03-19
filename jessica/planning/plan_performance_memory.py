from typing import Dict, List

from jessica.planning.plan_evaluation import PlanEvaluation


class PlanPerformanceMemory:
    """
    Stores historical plan evaluations for analysis and ranking.
    Advisory-only memory (no execution).
    """

    def __init__(self):
        self._records: Dict[str, List[PlanEvaluation]] = {}

    def record(self, goal_id: str, evaluation: PlanEvaluation):

        if goal_id not in self._records:
            self._records[goal_id] = []

        self._records[goal_id].append(evaluation)

    def get_records(self, goal_id: str) -> List[PlanEvaluation]:

        return list(self._records.get(goal_id, []))

    def best_plan(self, goal_id: str):

        records = self.get_records(goal_id)

        if not records:
            return None

        return sorted(records, key=lambda r: r.score, reverse=True)[0]
