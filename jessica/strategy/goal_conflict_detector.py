from typing import List, Tuple

from .active_goal_set import ActiveGoalSet
from .conflict_assessment import ConflictAssessment


class GoalConflictDetector:

    def __init__(self):
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def enable(self) -> None:
        self._enabled = True

    def detect_conflicts(self, active_set: ActiveGoalSet) -> ConflictAssessment:

        if not self._enabled:
            return ConflictAssessment(
                conflict_detected=False,
                conflicting_goal_pairs=(),
                explanation="Conflict detection disabled.",
                assessed_at=active_set.timestamp,
            )

        conflicts: List[Tuple[str, str]] = []
        goals = active_set.active_goals

        for i in range(len(goals)):
            for j in range(i + 1, len(goals)):
                resources_a = set(goals[i].required_resources)
                resources_b = set(goals[j].required_resources)
                if resources_a.intersection(resources_b):
                    conflicts.append((goals[i].goal_id, goals[j].goal_id))

        conflict_detected = len(conflicts) > 0
        explanation = (
            "Conflicts detected between goals."
            if conflict_detected
            else "No conflicts detected."
        )

        return ConflictAssessment(
            conflict_detected=conflict_detected,
            conflicting_goal_pairs=tuple(conflicts),
            explanation=explanation,
            assessed_at=active_set.timestamp,
        )
