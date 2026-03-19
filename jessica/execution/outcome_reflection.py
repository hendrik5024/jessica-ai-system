"""Phase 5.3 Outcome Reflection (read-only).

Read-only layer that explains and summarizes ExecutionOutcome data for human interpretation.
Constraints:
- No feedback loops
- No retries
- No learning or behavioral influence
- No execution or side effects
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .execution_tracker import ExecutionOutcome, ExecutionStatus


class OutcomeReflection:
    """Read-only summarizer for execution outcomes."""

    def summarize_outcome(self, outcome: ExecutionOutcome | Dict[str, Any]) -> Dict[str, Any]:
        """Summarize a single ExecutionOutcome or outcome dict.

        Args:
            outcome: ExecutionOutcome instance or dict with outcome fields

        Returns:
            Read-only summary dict suitable for human interpretation
        """
        data = self._normalize_outcome(outcome)

        summary = {
            "status": data.get("status"),
            "duration_ms": data.get("duration_ms"),
            "error_message": data.get("error_message"),
            "error_type": data.get("error_type"),
            "notes": data.get("notes"),
        }

        return summary

    def summarize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize a full execution record (dict) for human interpretation.

        Args:
            record: Execution record dict from ExecutionTracker

        Returns:
            Read-only summary dict
        """
        outcome = record.get("outcome", {})
        summary = {
            "execution_id": record.get("execution_id"),
            "intent_id": record.get("intent_id"),
            "action_type": record.get("action_type"),
            "action_params": record.get("action_params"),
            "approval_id": record.get("approval_id"),
            "timestamp": record.get("timestamp"),
            "reversible": record.get("reversible"),
            "undo_instructions": record.get("undo_instructions"),
            "status": outcome.get("status"),
            "duration_ms": outcome.get("duration_ms"),
            "error_message": outcome.get("error_message"),
            "error_type": outcome.get("error_type"),
            "notes": outcome.get("notes"),
        }

        return summary

    def summarize_outcomes(self, outcomes: Iterable[ExecutionOutcome | Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize a list of outcomes with aggregate statistics.

        Args:
            outcomes: Iterable of ExecutionOutcome or outcome dicts

        Returns:
            Summary with counts and simple stats
        """
        normalized: List[Dict[str, Any]] = [self._normalize_outcome(o) for o in outcomes]

        total = len(normalized)
        if total == 0:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "cancelled": 0,
                "average_duration_ms": 0,
            }

        success = sum(1 for o in normalized if o.get("status") == ExecutionStatus.SUCCESS.value)
        failed = sum(1 for o in normalized if o.get("status") == ExecutionStatus.FAILED.value)
        cancelled = sum(1 for o in normalized if o.get("status") == ExecutionStatus.CANCELLED.value)
        total_duration = sum(o.get("duration_ms") or 0 for o in normalized)

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "cancelled": cancelled,
            "average_duration_ms": total_duration / total if total else 0,
        }

    def to_text(self, summary: Dict[str, Any]) -> str:
        """Convert a summary dict into a human-readable string.

        Args:
            summary: Summary dict from summarize_outcome or summarize_record

        Returns:
            Readable text summary
        """
        parts = []
        if "status" in summary:
            parts.append(f"Status: {summary['status']}")
        if "duration_ms" in summary and summary["duration_ms"] is not None:
            parts.append(f"Duration: {summary['duration_ms']}ms")
        if summary.get("error_message"):
            parts.append(f"Error: {summary['error_message']}")
        if summary.get("notes"):
            parts.append(f"Notes: {summary['notes']}")

        return " | ".join(parts) if parts else "No outcome data available."

    @staticmethod
    def _normalize_outcome(outcome: ExecutionOutcome | Dict[str, Any]) -> Dict[str, Any]:
        """Normalize an outcome to dict form without mutation."""
        if isinstance(outcome, ExecutionOutcome):
            return {
                "status": outcome.status.value,
                "start_time": outcome.start_time,
                "end_time": outcome.end_time,
                "duration_ms": outcome.duration_ms,
                "error_message": outcome.error_message,
                "error_type": outcome.error_type,
                "system_state_before": outcome.system_state_before,
                "system_state_after": outcome.system_state_after,
                "side_effects": list(outcome.side_effects),
                "notes": outcome.notes,
            }

        # Assume dict-like
        return {
            "status": outcome.get("status"),
            "start_time": outcome.get("start_time"),
            "end_time": outcome.get("end_time"),
            "duration_ms": outcome.get("duration_ms"),
            "error_message": outcome.get("error_message"),
            "error_type": outcome.get("error_type"),
            "system_state_before": outcome.get("system_state_before"),
            "system_state_after": outcome.get("system_state_after"),
            "side_effects": list(outcome.get("side_effects") or []),
            "notes": outcome.get("notes"),
        }
