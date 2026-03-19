"""Phase 7.2: Execution Audit - Append-only immutable execution log.

Records all executions:
- proposal_id
- execution_id
- timestamp
- action
- parameters
- outcome

Properties:
- Append-only (never delete, never modify)
- Immutable once written
- Full traceability
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from jessica.execution.execution_engine import ExecutionResult, ExecutionResultStatus
from jessica.execution.execution_request import ExecutionRequest


@dataclass(frozen=True)
class AuditEntry:
    """Immutable record of a single execution audit entry."""
    entry_id: str                           # UUID
    proposal_id: str                        # From proposal
    execution_id: str                       # From execution request
    execution_timestamp: datetime           # When execution occurred
    action: str                             # What was executed
    parameters: Dict[str, any]              # Parameters used (immutable)
    outcome_status: ExecutionResultStatus         # SUCCESS, FAILED, etc.
    outcome: Optional[Dict[str, any]] = None  # Execution result
    error: Optional[str] = None             # Error if failed
    notes: str = ""                         # Additional context


class ExecutionAudit:
    """Append-only immutable audit log for all executions.
    
    This audit maintains a complete, immutable record of all executions.
    Entries can never be modified or deleted.
    
    Key properties:
    - Write-once
    - Read-only
    - Chronologically ordered
    - Full traceability
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize audit log.
        
        Args:
            enabled: Whether audit is active (reversible disable flag)
        """
        self.enabled = enabled
        self._audit_entries: Dict[str, AuditEntry] = {}
        self._entry_order: List[str] = []  # Preserve insertion order
    
    def record_execution(
        self,
        execution_request: ExecutionRequest,
        execution_result: ExecutionResult,
        proposal_id: str,
    ) -> Optional[str]:
        """
        Record execution in audit log (append-only).
        
        Args:
            execution_request: The execution request
            execution_result: The execution result
            proposal_id: ID of the proposal (for traceability)
        
        Returns:
            None on success
            Error message on failure
        """
        if not self.enabled:
            return "Audit is disabled"
        
        if not execution_request or not execution_result:
            return "Execution request and result required"
        
        if not proposal_id:
            return "Proposal ID required"
        
        # Create immutable audit entry
        entry_id = f"audit_{execution_request.execution_id}"
        
        entry = AuditEntry(
            entry_id=entry_id,
            proposal_id=proposal_id,
            execution_id=execution_request.execution_id,
            execution_timestamp=execution_result.outcome_timestamp,
            action=execution_result.action,
            parameters=dict(execution_request.immutable_parameters),
            outcome_status=execution_result.status,
            outcome=dict(execution_result.result) if execution_result.result else None,
            error=execution_result.error,
            notes=f"Executed via proposal {proposal_id}",
        )
        
        # Append-only: add to audit log
        self._audit_entries[entry_id] = entry
        self._entry_order.append(entry_id)
        
        return None
    
    def get_audit_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """
        Retrieve audit entry by ID (read-only).
        
        Args:
            entry_id: ID of audit entry
        
        Returns:
            AuditEntry if found, None otherwise
        """
        if not self.enabled:
            return None
        
        return self._audit_entries.get(entry_id)
    
    def get_entries_for_execution(self, execution_id: str) -> List[AuditEntry]:
        """
        Get all audit entries for a given execution (read-only).
        
        Args:
            execution_id: ID of execution
        
        Returns:
            List of matching audit entries (in chronological order)
        """
        if not self.enabled:
            return []
        
        results = []
        for entry_id in self._entry_order:
            entry = self._audit_entries[entry_id]
            if entry.execution_id == execution_id:
                results.append(entry)
        
        return results
    
    def get_entries_for_proposal(self, proposal_id: str) -> List[AuditEntry]:
        """
        Get all audit entries for a given proposal (read-only).
        
        Args:
            proposal_id: ID of proposal
        
        Returns:
            List of matching audit entries (in chronological order)
        """
        if not self.enabled:
            return []
        
        results = []
        for entry_id in self._entry_order:
            entry = self._audit_entries[entry_id]
            if entry.proposal_id == proposal_id:
                results.append(entry)
        
        return results
    
    def get_entries_by_status(self, status: ExecutionResultStatus) -> List[AuditEntry]:
        """
        Get all audit entries with given outcome status (read-only).
        
        Args:
            status: ExecutionResultStatus to filter by
        
        Returns:
            List of matching audit entries (in chronological order)
        """
        if not self.enabled:
            return []
        
        results = []
        for entry_id in self._entry_order:
            entry = self._audit_entries[entry_id]
            if entry.outcome_status == status:
                results.append(entry)
        
        return results
    
    def get_all_entries(self) -> List[AuditEntry]:
        """
        Get all audit entries (read-only, chronological order).
        
        Args:
            None
        
        Returns:
            List of all audit entries in insertion order
        """
        if not self.enabled:
            return []
        
        return [
            self._audit_entries[entry_id]
            for entry_id in self._entry_order
        ]
    
    def count_by_status(self) -> Dict[ExecutionResultStatus, int]:
        """
        Count audit entries by outcome status (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary mapping status to count
        """
        if not self.enabled:
            return {}
        
        counts: Dict[ExecutionResultStatus, int] = {}
        
        for status in ExecutionResultStatus:
            count = len([
                e for e in self._audit_entries.values()
                if e.outcome_status == status
            ])
            if count > 0:
                counts[status] = count
        
        return counts
    
    def get_audit_stats(self) -> Dict[str, any]:
        """
        Get audit statistics (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary with audit statistics
        """
        if not self.enabled:
            return {}
        
        status_counts = self.count_by_status()
        
        return {
            "total_executions": len(self._audit_entries),
            "by_status": status_counts,
            "enabled": self.enabled,
        }
    
    def disable(self):
        """Disable audit (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable audit (reversible)."""
        self.enabled = True
