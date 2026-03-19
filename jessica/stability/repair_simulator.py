from dataclasses import dataclass
from typing import List

from .self_repair_advisor import RepairRecommendation


@dataclass(frozen=True)
class RepairSimulationResult:
    issue: str
    projected_stability_after: float
    confidence: float


class RepairSimulator:
    """
    Simulates projected stability impact of repair recommendations.
    """

    def __init__(self):
        self.enabled = True

    def simulate(
        self,
        current_stability: float,
        recommendations: List[RepairRecommendation],
    ) -> List[RepairSimulationResult]:

        if not self.enabled:
            return []

        results = []

        for rec in recommendations:
            projected = min(1.0, current_stability + rec.expected_stability_gain)

            results.append(
                RepairSimulationResult(
                    issue=rec.issue_detected,
                    projected_stability_after=projected,
                    confidence=0.85,
                )
            )

        return results
