from .integrity_record import IntegrityRecord


class IntegrityChecker:

    def check(
        self,
        integrity_id: str,
        reasoning_id: str,
        multi_reasoning_present: bool,
        arbitration_present: bool,
        final_answer_present: bool,
    ) -> IntegrityRecord:

        integrity_passed = (
            multi_reasoning_present
            and arbitration_present
            and final_answer_present
        )

        return IntegrityRecord(
            integrity_id=integrity_id,
            reasoning_id=reasoning_id,
            multi_reasoning_present=multi_reasoning_present,
            arbitration_present=arbitration_present,
            final_answer_present=final_answer_present,
            integrity_passed=integrity_passed,
        )
