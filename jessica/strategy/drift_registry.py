from typing import List

from .drift_assessment import DriftAssessment


class DriftRegistry:

    def __init__(self):
        self._assessments: List[DriftAssessment] = []

    def add(self, assessment: DriftAssessment) -> None:
        self._assessments.append(assessment)

    def history(self) -> List[DriftAssessment]:
        return list(self._assessments)
