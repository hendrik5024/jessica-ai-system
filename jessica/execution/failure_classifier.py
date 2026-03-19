"""Phase 5.4 Failure Classification (deterministic, read-only)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .execution_tracker import ExecutionOutcome, ExecutionStatus


class FailureCategory(Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    UI_MISMATCH = "ui_mismatch"
    FOCUS_LOST = "focus_lost"
    PERMISSION_DENIED = "permission_denied"
    INPUT_REJECTED = "input_rejected"
    SYSTEM_INTERRUPTION = "system_interruption"
    UNKNOWN_FAILURE = "unknown_failure"


@dataclass(frozen=True)
class ClassificationResult:
    category: FailureCategory
    reason: str
    confidence: float


class FailureClassifier:
    """Deterministic, stateless classifier for execution outcomes."""

    def classify(self, outcome: ExecutionOutcome | Dict[str, Any]) -> ClassificationResult:
        data = self._normalize(outcome)
        status = data.get("status")
        error_message = (data.get("error_message") or "").lower()
        error_type = (data.get("error_type") or "").lower()
        duration_ms = data.get("duration_ms") or 0

        if status == ExecutionStatus.SUCCESS.value:
            return ClassificationResult(FailureCategory.SUCCESS, "Execution succeeded.", 1.0)

        if "timeout" in error_message or "timed out" in error_message:
            return ClassificationResult(FailureCategory.TIMEOUT, "Execution timed out.", 0.9)

        if "ui" in error_message and "mismatch" in error_message:
            return ClassificationResult(FailureCategory.UI_MISMATCH, "UI mismatch detected.", 0.8)

        if "focus" in error_message or "window not active" in error_message:
            return ClassificationResult(FailureCategory.FOCUS_LOST, "Window focus lost.", 0.8)

        if "permission" in error_message or "access denied" in error_message or "denied" in error_message:
            return ClassificationResult(FailureCategory.PERMISSION_DENIED, "Permission denied.", 0.8)

        if "invalid" in error_message or "rejected" in error_message or "input" in error_message:
            return ClassificationResult(FailureCategory.INPUT_REJECTED, "Input was rejected.", 0.7)

        if "interrupt" in error_message or "interruption" in error_message:
            return ClassificationResult(FailureCategory.SYSTEM_INTERRUPTION, "System interruption occurred.", 0.7)

        if error_type in {"keyboardinterrupt", "systemexit"}:
            return ClassificationResult(FailureCategory.SYSTEM_INTERRUPTION, "Execution interrupted by system.", 0.8)

        if status == ExecutionStatus.CANCELLED.value:
            return ClassificationResult(FailureCategory.SYSTEM_INTERRUPTION, "Execution was cancelled.", 0.6)

        if duration_ms and duration_ms > 30000:
            return ClassificationResult(FailureCategory.TIMEOUT, "Execution exceeded expected duration.", 0.6)

        return ClassificationResult(FailureCategory.UNKNOWN_FAILURE, "Unknown failure.", 0.4)

    @staticmethod
    def _normalize(outcome: ExecutionOutcome | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(outcome, ExecutionOutcome):
            return {
                "status": outcome.status.value,
                "duration_ms": outcome.duration_ms,
                "error_message": outcome.error_message,
                "error_type": outcome.error_type,
            }

        return {
            "status": outcome.get("status"),
            "duration_ms": outcome.get("duration_ms"),
            "error_message": outcome.get("error_message"),
            "error_type": outcome.get("error_type"),
        }
