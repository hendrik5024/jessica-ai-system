from .strategic_correction_record import StrategicCorrectionRecord


class StrategicCorrectionEngine:

    def recommend(
        self,
        correction_id: str,
        stability_level: str,
    ) -> StrategicCorrectionRecord:

        if stability_level == "STABLE":
            rec = "No stabilization required"
        elif stability_level == "MODERATE_LOAD":
            rec = "Consider consolidating overlapping long-horizon plans"
        else:
            rec = "Recommend reducing concurrent long-horizon plans"

        return StrategicCorrectionRecord(
            correction_id,
            stability_level,
            rec,
        )
