from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RepairRecommendation:
    issue_detected: str
    severity: float
    recommended_action: str
    expected_stability_gain: float


class SelfRepairAdvisor:
    """
    Generates repair recommendations based on detected reasoning drift.
    """

    def __init__(self):
        self.enabled = True

    def generate_recommendations(
        self,
        drift_signals: List[Dict],
    ) -> List[RepairRecommendation]:
        """
        Produce advisory-only repair suggestions.
        """
        if not self.enabled:
            return []

        recommendations = []

        for signal in drift_signals:
            severity = float(signal.get("severity", 0.0))

            recommendations.append(
                RepairRecommendation(
                    issue_detected=signal.get("issue", "unknown"),
                    severity=severity,
                    recommended_action="Recalibrate reasoning consistency parameters",
                    expected_stability_gain=min(1.0, severity * 0.6),
                )
            )

        return recommendations
