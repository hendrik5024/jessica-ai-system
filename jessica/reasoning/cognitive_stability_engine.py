from .cognitive_stability_record import CognitiveStabilityRecord


class CognitiveStabilityEngine:

    def evaluate(
        self,
        stability_id: str,
        reasoning_score: float,
        consistency_score: float,
    ) -> CognitiveStabilityRecord:

        combined = (reasoning_score + consistency_score) / 2

        if combined >= 0.8:
            level = "HIGH"
            unstable = False
        elif combined >= 0.5:
            level = "MODERATE"
            unstable = False
        else:
            level = "LOW"
            unstable = True

        return CognitiveStabilityRecord(
            stability_id,
            reasoning_score,
            consistency_score,
            level,
            unstable,
            "Deterministic stability evaluation",
        )
