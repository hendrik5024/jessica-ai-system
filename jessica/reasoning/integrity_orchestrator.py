from .integrity_checker import IntegrityChecker
from .integrity_record import IntegrityRecord


class IntegrityOrchestrator:

    def __init__(self):
        self.checker = IntegrityChecker()

    def verify(
        self,
        integrity_id: str,
        reasoning_id: str,
        multi_reasoning_present: bool,
        arbitration_present: bool,
        final_answer_present: bool,
    ) -> IntegrityRecord:

        return self.checker.check(
            integrity_id,
            reasoning_id,
            multi_reasoning_present,
            arbitration_present,
            final_answer_present,
        )
