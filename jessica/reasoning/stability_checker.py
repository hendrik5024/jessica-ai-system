from .stability_record import StabilityRecord


class StabilityChecker:

    def check(
        self,
        stability_id: str,
        arbitration_id: str,
        previous_answer: str,
        current_answer: str,
    ) -> StabilityRecord:

        consistent = previous_answer == current_answer

        return StabilityRecord(
            stability_id=stability_id,
            arbitration_id=arbitration_id,
            consistent=consistent,
            previous_answer=previous_answer,
            current_answer=current_answer,
            note="Deterministic comparison of reasoning outcome",
        )
