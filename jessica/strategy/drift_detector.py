from .drift_assessment import DriftAssessment
from .operational_activity_snapshot import OperationalActivitySnapshot
from .strategic_direction_record import StrategicDirectionRecord


class DriftDetector:

    def __init__(self):
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def enable(self) -> None:
        self._enabled = True

    def detect_drift(
        self,
        direction: StrategicDirectionRecord,
        activity: OperationalActivitySnapshot,
    ) -> DriftAssessment:

        if not self._enabled:
            return DriftAssessment(
                drift_detected=False,
                drift_score=0.0,
                explanation="Drift detection disabled.",
                assessed_at=activity.timestamp,
            )

        direction_text = direction.description.strip().lower()
        focus_text = activity.current_focus.strip().lower()
        goals_text = [goal.strip().lower() for goal in activity.active_goals]

        aligned = (
            direction_text in focus_text
            or focus_text in direction_text
            or direction_text in goals_text
        )

        drift_score = 0.0 if aligned else 1.0
        drift_detected = drift_score > 0.0

        explanation = (
            "Operational activity aligns with strategic direction."
            if aligned
            else "Operational activity diverges from strategic direction."
        )

        return DriftAssessment(
            drift_detected=drift_detected,
            drift_score=drift_score,
            explanation=explanation,
            assessed_at=activity.timestamp,
        )
