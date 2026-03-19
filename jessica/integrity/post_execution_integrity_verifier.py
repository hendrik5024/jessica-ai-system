from dataclasses import dataclass
from time import time
from typing import List


@dataclass(frozen=True)
class IntegrityVerificationResult:
    verification_id: str
    execution_id: str
    verification_timestamp: float
    integrity_passed: bool
    mismatches_detected: List[str]
    verification_notes: str


class PostExecutionIntegrityVerifier:

    def verify_execution(self, execution_result, expected_outcome) -> IntegrityVerificationResult:
        mismatches: List[str] = []

        if expected_outcome.get("require_success", True) and not execution_result.execution_success:
            mismatches.append("Execution not successful")

        if execution_result.sandbox_violations:
            mismatches.append("Sandbox violations detected")

        required_actions = expected_outcome.get("required_actions", [])
        executed_actions = self._extract_actions(execution_result.execution_log)

        for action in required_actions:
            if action not in executed_actions:
                mismatches.append(f"Missing required action: {action}")

        allowed_actions = expected_outcome.get("allowed_actions")
        if allowed_actions is not None:
            for action in executed_actions:
                if action not in allowed_actions:
                    mismatches.append(f"Unintended action: {action}")

        if expected_outcome.get("require_completion", True):
            if "Execution completed." not in execution_result.execution_log:
                mismatches.append("Execution did not complete")

        integrity_passed = len(mismatches) == 0
        notes = (
            "Verification passed."
            if integrity_passed
            else "Verification failed; governance review required."
        )

        return IntegrityVerificationResult(
            verification_id=f"verify-{execution_result.execution_id}",
            execution_id=execution_result.execution_id,
            verification_timestamp=time(),
            integrity_passed=integrity_passed,
            mismatches_detected=mismatches,
            verification_notes=notes,
        )

    def _extract_actions(self, execution_log: List[str]) -> List[str]:
        actions: List[str] = []
        for line in execution_log:
            if line.startswith("Executing: "):
                actions.append(line.replace("Executing: ", "", 1))
        return actions
