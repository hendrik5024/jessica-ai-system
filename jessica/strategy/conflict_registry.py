from typing import List

from .conflict_assessment import ConflictAssessment


class ConflictRegistry:

    def __init__(self):
        self._assessments: List[ConflictAssessment] = []

    def add(self, assessment: ConflictAssessment) -> None:
        self._assessments.append(assessment)

    def history(self) -> List[ConflictAssessment]:
        return list(self._assessments)
