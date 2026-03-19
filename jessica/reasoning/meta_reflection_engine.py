from .meta_reflection_record import MetaReflectionRecord


class MetaReflectionEngine:

    def evaluate(
        self,
        reflection_id: str,
        reasoning_id: str,
        reasoning_paths: int,
        integrity_passed: bool,
        stability_passed: bool,
        confidence_score: float,
    ) -> MetaReflectionRecord:

        quality = confidence_score

        if not integrity_passed:
            quality *= 0.7

        if not stability_passed:
            quality *= 0.8

        uncertainty = 1.0 - quality

        notes = "Reasoning evaluated deterministically."

        return MetaReflectionRecord(
            reflection_id=reflection_id,
            reasoning_id=reasoning_id,
            reasoning_paths=reasoning_paths,
            integrity_passed=integrity_passed,
            stability_passed=stability_passed,
            confidence_score=confidence_score,
            reasoning_quality=quality,
            uncertainty_level=uncertainty,
            notes=notes,
        )
