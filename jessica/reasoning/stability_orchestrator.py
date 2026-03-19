from .stability_checker import StabilityChecker
from .stability_record import StabilityRecord


class StabilityOrchestrator:

    def __init__(self):
        self.checker = StabilityChecker()

    def evaluate(
        self,
        stability_id: str,
        arbitration_id: str,
        previous_answer: str,
        current_answer: str,
    ) -> StabilityRecord:

        return self.checker.check(
            stability_id,
            arbitration_id,
            previous_answer,
            current_answer,
        )
