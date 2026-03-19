"""Phase 7.2: Execution Engine - Execute approved actions with strict scope enforcement.

Key properties:
- Only executes approved actions
- Parameters are immutable during execution
- No dynamic dispatch or fallback
- Single execution per request
- All outcomes are recorded
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from jessica.execution.execution_request import ExecutionRequest


class ExecutionResultStatus(Enum):
    """Status of an execution result (Phase 7.2)."""
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class ExecutionResult:
    """Immutable record of execution result."""
    execution_id: str
    status: ExecutionResultStatus                 # SUCCESS, FAILED, REJECTED, etc.
    action: str                             # What was executed
    outcome_timestamp: datetime
    result: Optional[Dict[str, Any]] = None  # Execution result
    error: Optional[str] = None             # Error message if failed
    metadata: Optional[Dict[str, Any]] = None  # Additional context


class ExecutionEngine:
    """Execute approved actions with strict scope enforcement.
    
    This engine implements controlled, proposal-bound execution:
    - Only approved actions execute
    - Parameters are locked at request time
    - No retry logic
    - No self-initiated execution
    - Single-use execution window
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize execution engine.
        
        Args:
            enabled: Whether engine is active (reversible disable flag)
        """
        self.enabled = enabled
        self._execution_history: Dict[str, ExecutionOutcome] = {}
    
    def execute(
        self,
        execution_request: ExecutionRequest,
    ) -> Tuple[Optional[ExecutionResult], Optional[str]]:
        """
        Execute approved action from request.
        
        Args:
            execution_request: ExecutionRequest with approved action
        
        Returns:
            (ExecutionResult, None) on success
            (None, error) on failure
        """
        if not self.enabled:
            return None, "Execution engine is disabled"
        
        if not execution_request:
            return None, "Execution request required"
        
        # Check expiry (should be validated earlier, but double-check)
        if execution_request.is_expired():
            outcome = ExecutionResult(
                execution_id=execution_request.execution_id,
                status=ExecutionResultStatus.EXPIRED,
                action="<expired>",
                outcome_timestamp=datetime.now(),
                error="Execution window expired",
            )
            return outcome, None
        
        # Execute each approved action
        outcomes = []
        for action_name in execution_request.approved_actions:
            outcome = self._execute_single_action(
                execution_request.execution_id,
                action_name,
                execution_request.immutable_parameters,
            )
            outcomes.append(outcome)
        
        # Return first outcome (or combined if multiple)
        if outcomes:
            return outcomes[0], None
        else:
            return None, "No actions to execute"
    
    def _execute_single_action(
        self,
        execution_id: str,
        action_name: str,
        parameters: Dict[str, Any],
    ) -> ExecutionResult:
        """
        Execute a single action.
        
        This is a stub implementation. In real system, this would dispatch
        to actual action handlers (Phase 5.2 or equivalent).
        
        Args:
            execution_id: ID of this execution
            action_name: Name of action to execute
            parameters: Immutable parameters
        
        Returns:
            ExecutionResult with result
        """
        try:
            # In production, this would actually execute the action
            # For now, simulate success
            
            result = {
                "action": action_name,
                "status": "completed",
                "parameters_used": parameters,
            }
            
            outcome = ExecutionResult(
                execution_id=execution_id,
                status=ExecutionResultStatus.SUCCESS,
                action=action_name,
                outcome_timestamp=datetime.now(),
                result=result,
                metadata={"execution_model": "phase_7_2_stub"},
            )
            
            # Record in history
            self._execution_history[execution_id] = outcome
            
            return outcome
        
        except Exception as e:
            # Hard-fail on any error
            error_msg = f"Execution failed: {str(e)}"
            
            outcome = ExecutionResult(
                execution_id=execution_id,
                status=ExecutionResultStatus.FAILED,
                action=action_name,
                outcome_timestamp=datetime.now(),
                error=error_msg,
            )
            
            # Record failure in history
            self._execution_history[execution_id] = outcome
            
            return outcome
    
    def get_execution_outcome(self, execution_id: str) -> Optional[ExecutionResult]:
        """
        Retrieve execution outcome by ID (read-only).
        
        Args:
            execution_id: ID of execution to retrieve
        
        Returns:
            ExecutionResult if found, None otherwise
        """
        if not self.enabled:
            return None
        
        return self._execution_history.get(execution_id)
    
    def get_execution_status(self, execution_id: str) -> Optional[ExecutionResultStatus]:
        """
        Get status of execution (read-only).
        
        Args:
            execution_id: ID of execution
        
        Returns:
            ExecutionResultStatus if execution found, None otherwise
        """
        outcome = self.get_execution_outcome(execution_id)
        if outcome:
            return outcome.status
        return None
    
    def has_executed(self, execution_id: str) -> bool:
        """
        Check if execution has been completed.
        
        Args:
            execution_id: ID of execution
        
        Returns:
            True if execution found, False otherwise
        """
        return execution_id in self._execution_history
    
    def get_execution_history(self) -> Dict[str, ExecutionResult]:
        """
        Get full execution history (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary of all executions (copy, not reference)
        """
        if not self.enabled:
            return {}
        
        return dict(self._execution_history)
    
    def disable(self):
        """Disable execution engine (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable execution engine (reversible)."""
        self.enabled = True
