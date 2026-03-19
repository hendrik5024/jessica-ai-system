from .metacognition_record import MetaCognitionRecord


class MetaCognitionEngine:

    def evaluate(
        self,
        record_id: str,
        reasoning_score: float,
        consistency_score: float,
        stability_level: str,
        drift_detected: bool,
    ) -> MetaCognitionRecord:

        if drift_detected or stability_level == "LOW":
            status = "ATTENTION_REQUIRED"
        elif reasoning_score > 0.8 and consistency_score > 0.8:
            status = "OPTIMAL"
        else:
            status = "STABLE"

        return MetaCognitionRecord(
            record_id,
            reasoning_score,
            consistency_score,
            stability_level,
            drift_detected,
            status,
            "Deterministic meta-cognition evaluation",
        )
