"""Execution tracking and audit trail for Phase 5.2 actions.

Maintains complete history of all executed actions with context, results, and reversibility.
- Immutable audit trail (append-only)
- Reversibility through action recording
- Outcome tracking (success/failure)
- Traceability for all executions
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionStatus(Enum):
    """Status of an executed action."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass
class ExecutionOutcome:
    """Result of action execution."""
    status: ExecutionStatus
    start_time: float
    end_time: float
    duration_ms: float
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    system_state_before: Optional[Dict[str, Any]] = None
    system_state_after: Optional[Dict[str, Any]] = None
    side_effects: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "system_state_before": self.system_state_before,
            "system_state_after": self.system_state_after,
            "side_effects": self.side_effects,
            "notes": self.notes,
        }


@dataclass
class ExecutionRecord:
    """Complete record of a single action execution."""
    execution_id: str
    intent_id: str
    action_type: str  # "keyboard" | "mouse" | "compound"
    action_params: Dict[str, Any]
    approval_id: Optional[str]
    timestamp: str
    executor_id: str
    outcome: ExecutionOutcome
    reversible: bool
    undo_instructions: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "execution_id": self.execution_id,
            "intent_id": self.intent_id,
            "action_type": self.action_type,
            "action_params": self.action_params,
            "approval_id": self.approval_id,
            "timestamp": self.timestamp,
            "executor_id": self.executor_id,
            "outcome": self.outcome.to_dict(),
            "reversible": self.reversible,
            "undo_instructions": self.undo_instructions,
            "context": self.context,
            "metadata": self.metadata,
        }


class ExecutionTracker:
    """Maintains immutable audit trail of all executions."""

    def __init__(self, data_dir: Optional[str] = None, enabled: bool = True):
        """Initialize execution tracker.

        Args:
            data_dir: Directory to store execution records (JSON)
            enabled: Whether execution tracking is enabled (reversible disable flag)
        """
        self.enabled = enabled
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(__file__), "..", "data", "executions"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self.audit_log_path = os.path.join(self.data_dir, "audit_trail.jsonl")
        self.execution_records: List[ExecutionRecord] = []
        self._execution_counter = 0

        # Load existing records
        self._load_audit_trail()

    def _load_audit_trail(self) -> None:
        """Load existing execution records from disk."""
        if not os.path.exists(self.audit_log_path):
            return

        try:
            with open(self.audit_log_path, "r") as f:
                for line in f:
                    if line.strip():
                        self.execution_records.append(json.loads(line))
                        self._execution_counter += 1
        except Exception as e:
            print(f"[ExecutionTracker] Failed to load audit trail: {e}")

    def record_execution(
        self,
        intent_id: str,
        action_type: str,
        action_params: Dict[str, Any],
        approval_id: Optional[str],
        outcome: ExecutionOutcome,
        reversible: bool = True,
        undo_instructions: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record a completed action execution (append-only, immutable).

        Args:
            intent_id: ID of the intent that triggered this action
            action_type: Type of action (keyboard, mouse, compound)
            action_params: Parameters passed to action (e.g., key, x, y)
            approval_id: ID of approval that authorized this action
            outcome: ExecutionOutcome with status and details
            reversible: Whether this action can be reversed
            undo_instructions: How to undo this action
            context: Context info (UI state, target app, etc.)
            metadata: Additional metadata

        Returns:
            ExecutionRecord dict for the recorded execution
        """
        if not self.enabled:
            return None

        self._execution_counter += 1
        execution_id = f"exec_{self._execution_counter:06d}"

        record = ExecutionRecord(
            execution_id=execution_id,
            intent_id=intent_id,
            action_type=action_type,
            action_params=action_params,
            approval_id=approval_id,
            timestamp=datetime.utcnow().isoformat(),
            executor_id="phase_5_2_minimal",
            outcome=outcome,
            reversible=reversible,
            undo_instructions=undo_instructions,
            context=context or {},
            metadata=metadata or {},
        )

        # Convert to dict
        record_dict = record.to_dict()

        # Append to audit trail (immutable append-only log)
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(record_dict) + "\n")
        except Exception as e:
            print(f"[ExecutionTracker] Failed to write audit trail: {e}")

        self.execution_records.append(record_dict)
        return record_dict

    def get_execution_history(
        self, intent_id: Optional[str] = None, limit: Optional[int] = None
    ) -> List[ExecutionRecord]:
        """Get execution history (optionally filtered by intent).

        Args:
            intent_id: Filter by specific intent (None = all)
            limit: Limit number of records (None = all)

        Returns:
            List of ExecutionRecord objects
        """
        if not self.enabled:
            return []

        records = self.execution_records

        if intent_id:
            records = [r for r in records if r["intent_id"] == intent_id]

        if limit:
            records = records[-limit:]

        return records

    def get_last_execution(self, action_type: Optional[str] = None) -> Optional[ExecutionRecord]:
        """Get the most recent execution (optionally filtered by action type).

        Args:
            action_type: Filter by action type (None = any type)

        Returns:
            Most recent ExecutionRecord or None
        """
        if not self.enabled or not self.execution_records:
            return None

        records = self.execution_records

        if action_type:
            records = [r for r in records if r["action_type"] == action_type]

        return records[-1] if records else None

    def is_reversible(self, execution_id: str) -> bool:
        """Check if an execution is reversible.

        Args:
            execution_id: ID of execution to check

        Returns:
            True if reversible, False otherwise
        """
        if not self.enabled:
            return False

        for record in self.execution_records:
            if record["execution_id"] == execution_id:
                return record.get("reversible", False)

        return False

    def get_undo_instructions(self, execution_id: str) -> Optional[str]:
        """Get undo instructions for an execution.

        Args:
            execution_id: ID of execution

        Returns:
            Undo instructions or None
        """
        if not self.enabled:
            return None

        for record in self.execution_records:
            if record["execution_id"] == execution_id:
                return record.get("undo_instructions")

        return None

    def get_success_rate(self) -> float:
        """Get success rate of all executions.

        Returns:
            Fraction of successful executions (0.0 to 1.0)
        """
        if not self.enabled or not self.execution_records:
            return 0.0

        successful = sum(
            1 for r in self.execution_records
            if isinstance(r, dict) and r.get("outcome", {}).get("status") == ExecutionStatus.SUCCESS.value
            or isinstance(r, ExecutionRecord) and r.outcome.status == ExecutionStatus.SUCCESS
        )

        return successful / len(self.execution_records)

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dict with execution stats
        """
        if not self.enabled:
            return {
                "enabled": False,
                "total_executions": 0,
            }

        status_counts = {}
        total_duration = 0
        reversible_count = 0

        for record in self.execution_records:
            if isinstance(record, dict):
                status = record.get("outcome", {}).get("status")
                total_duration += record.get("outcome", {}).get("duration_ms", 0)
                if record.get("reversible"):
                    reversible_count += 1
            else:
                status = record.outcome.status.value
                total_duration += record.outcome.duration_ms
                if record.reversible:
                    reversible_count += 1

            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "enabled": True,
            "total_executions": len(self.execution_records),
            "status_breakdown": status_counts,
            "success_rate": self.get_success_rate(),
            "reversible_count": reversible_count,
            "total_duration_ms": total_duration,
            "average_duration_ms": (
                total_duration / len(self.execution_records)
                if self.execution_records
                else 0
            ),
        }

    def enable(self) -> None:
        """Enable execution tracking."""
        self.enabled = True

    def disable(self) -> None:
        """Disable execution tracking (reversible disable flag)."""
        self.enabled = False

    def clear_history(self) -> None:
        """Clear execution history (CAUTION: irreversible if persisted)."""
        if self.enabled:
            self.execution_records = []
            self._execution_counter = 0
            # Note: audit trail file is NOT cleared (append-only design)
