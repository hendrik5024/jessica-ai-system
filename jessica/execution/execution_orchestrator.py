"""Phase 7.2: Execution Orchestrator - Single execution entry point.

Orchestrates the complete execution flow:
1. Validate execution request
2. Lock execution window (prevent concurrent/repeated execution)
3. Execute action
4. Record audit entry
5. Close execution window permanently

This is the ONLY authorized entry point for executing proposals.
"""
from __future__ import annotations

from typing import Optional, Tuple

from jessica.execution.action_proposal_structures import ActionProposal
from jessica.execution.execution_audit import ExecutionAudit
from jessica.execution.execution_engine import ExecutionEngine, ExecutionResult
from jessica.execution.execution_request import ExecutionRequest
from jessica.execution.execution_validator import ExecutionValidator


class ExecutionOrchestrator:
    """Single execution entry point for Phase 7.1 approved proposals.
    
    This orchestrator ensures:
    - All executions are validated
    - All executions are audited
    - Execution windows are single-use
    - No concurrent execution
    - Human authority is preserved
    """
    
    def __init__(
        self,
        enabled: bool = True,
        validator: Optional[ExecutionValidator] = None,
        engine: Optional[ExecutionEngine] = None,
        audit: Optional[ExecutionAudit] = None,
    ):
        """Initialize execution orchestrator.
        
        Args:
            enabled: Whether orchestrator is active
            validator: ExecutionValidator instance (creates if None)
            engine: ExecutionEngine instance (creates if None)
            audit: ExecutionAudit instance (creates if None)
        """
        self.enabled = enabled
        self.validator = validator or ExecutionValidator(enabled=True)
        self.engine = engine or ExecutionEngine(enabled=True)
        self.audit = audit or ExecutionAudit(enabled=True)
        
        # Track executed requests (single-use enforcement)
        self._executed_requests: set[str] = set()
    
    def execute_proposal(
        self,
        execution_request: ExecutionRequest,
        proposal: ActionProposal,
    ) -> Tuple[Optional[ExecutionResult], Optional[str]]:
        """
        Execute an approved proposal (ONLY authorized entry point).
        
        This method implements the complete execution flow:
        1. Validate the request
        2. Check single-use enforcement
        3. Execute the action
        4. Record audit entry
        5. Mark as executed
        
        Args:
            execution_request: ExecutionRequest to execute
            proposal: Phase 7.1 ActionProposal (must be APPROVED)
        
        Returns:
            (ExecutionResult, None) on success
            (None, error) on failure
        """
        if not self.enabled:
            return None, "Orchestrator is disabled"
        
        if not execution_request or not proposal:
            return None, "Execution request and proposal required"
        
        # ============================================================
        # Step 1: Validate execution request against proposal
        # ============================================================
        
        validation_result = self.validator.validate_execution_request(
            execution_request,
            proposal,
        )
        
        if not validation_result.valid:
            return None, f"Validation failed: {validation_result.error}"
        
        # ============================================================
        # Step 2: Check single-use enforcement (prevent re-execution)
        # ============================================================
        
        if execution_request.execution_id in self._executed_requests:
            return None, "Execution window already used (single-use only)"
        
        # ============================================================
        # Step 3: Execute action
        # ============================================================
        
        outcome, error = self.engine.execute(execution_request)
        
        if error:
            return None, f"Execution failed: {error}"
        
        if not outcome:
            return None, "Execution returned no outcome"
        
        # ============================================================
        # Step 4: Record audit entry (append-only)
        # ============================================================
        
        audit_error = self.audit.record_execution(
            execution_request,
            outcome,
            proposal.proposal_id,
        )
        
        if audit_error:
            # Log audit failure but don't fail execution
            # (execution already occurred)
            print(f"Warning: Audit recording failed: {audit_error}")
        
        # ============================================================
        # Step 5: Mark execution window as used (close permanently)
        # ============================================================
        
        self._executed_requests.add(execution_request.execution_id)
        
        return outcome, None
    
    def can_execute(
        self,
        execution_request: ExecutionRequest,
        proposal: ActionProposal,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if proposal can be executed (without executing).
        
        This is a dry-run validation. Returns True if execution would
        be allowed, False otherwise with error reason.
        
        Args:
            execution_request: ExecutionRequest to check
            proposal: Phase 7.1 ActionProposal
        
        Returns:
            (True, None) if execution allowed
            (False, error) if execution would fail
        """
        if not self.enabled:
            return False, "Orchestrator is disabled"
        
        if not execution_request or not proposal:
            return False, "Execution request and proposal required"
        
        # Check validation
        validation_result = self.validator.validate_execution_request(
            execution_request,
            proposal,
        )
        
        if not validation_result.valid:
            return False, validation_result.error
        
        # Check single-use enforcement
        if execution_request.execution_id in self._executed_requests:
            return False, "Execution window already used"
        
        return True, None
    
    def has_executed(self, execution_id: str) -> bool:
        """
        Check if an execution has been completed.
        
        Args:
            execution_id: ID of execution to check
        
        Returns:
            True if execution has occurred, False otherwise
        """
        return execution_id in self._executed_requests
    
    def get_execution_audit(self, execution_id: str) -> Optional[dict]:
        """
        Get audit record for an execution (read-only).
        
        Args:
            execution_id: ID of execution
        
        Returns:
            Audit entry if found, None otherwise
        """
        entries = self.audit.get_entries_for_execution(execution_id)
        if entries:
            entry = entries[0]
            return {
                "entry_id": entry.entry_id,
                "proposal_id": entry.proposal_id,
                "execution_id": entry.execution_id,
                "timestamp": entry.execution_timestamp.isoformat(),
                "action": entry.action,
                "status": entry.outcome_status.value,
                "error": entry.error,
            }
        return None
    
    def get_audit_trail_for_proposal(self, proposal_id: str) -> list[dict]:
        """
        Get full audit trail for a proposal (read-only).
        
        Args:
            proposal_id: ID of proposal
        
        Returns:
            List of audit entries for this proposal
        """
        entries = self.audit.get_entries_for_proposal(proposal_id)
        return [
            {
                "entry_id": e.entry_id,
                "execution_id": e.execution_id,
                "timestamp": e.execution_timestamp.isoformat(),
                "action": e.action,
                "status": e.outcome_status.value,
                "error": e.error,
            }
            for e in entries
        ]
    
    def get_execution_stats(self) -> dict:
        """
        Get execution statistics (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary with execution statistics
        """
        return {
            "total_executed": len(self._executed_requests),
            "audit_stats": self.audit.get_audit_stats(),
            "enabled": self.enabled,
        }
    
    def disable(self):
        """Disable orchestrator (global safety switch)."""
        self.enabled = False
        self.validator.disable()
        self.engine.disable()
        self.audit.disable()
    
    def enable(self):
        """Enable orchestrator (reversible)."""
        self.enabled = True
        self.validator.enable()
        self.engine.enable()
        self.audit.enable()
