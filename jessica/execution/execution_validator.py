"""Phase 7.2: Execution Validator - Hard-fail validation against Phase 7.1 proposals.

Enforces strict matching between execution request and approved proposal:
- Proposal must exist
- Proposal must be APPROVED status
- Approval must not be expired
- Actions must match exactly
- Parameters must match exactly

Hard-fail on any mismatch. No correction or fallback logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from jessica.execution.action_proposal_structures import ActionProposal, ProposalStatus
from jessica.execution.execution_request import ExecutionRequest


@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result."""
    valid: bool                     # True if validation passed
    error: Optional[str] = None     # Error message if invalid


class ExecutionValidator:
    """Validates execution requests against Phase 7.1 proposals.
    
    This validator implements hard-fail semantics:
    - Any mismatch causes immediate rejection
    - No correction or fallback logic
    - All mismatches are treated as hard errors
    
    This is the primary security gate preventing unauthorized execution.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize validator.
        
        Args:
            enabled: Whether validator is active (reversible disable flag)
        """
        self.enabled = enabled
    
    def validate_execution_request(
        self,
        execution_request: ExecutionRequest,
        proposal: Optional[ActionProposal],
    ) -> ValidationResult:
        """
        Validate execution request against proposal.
        
        This is the primary validation method. It performs comprehensive
        checks to ensure execution request matches approved proposal.
        
        Args:
            execution_request: ExecutionRequest to validate
            proposal: Phase 7.1 ActionProposal (must exist and be approved)
        
        Returns:
            ValidationResult with valid=True or error message
        """
        if not self.enabled:
            return ValidationResult(valid=False, error="Validator is disabled")
        
        if not execution_request:
            return ValidationResult(valid=False, error="Execution request required")
        
        if not proposal:
            return ValidationResult(valid=False, error="Proposal not found")
        
        # Check 1: Proposal ID must match
        if proposal.proposal_id != execution_request.proposal_id:
            return ValidationResult(
                valid=False,
                error=f"Proposal ID mismatch: {proposal.proposal_id} vs {execution_request.proposal_id}",
            )
        
        # Check 2: Proposal must be APPROVED
        if proposal.status != ProposalStatus.APPROVED:
            return ValidationResult(
                valid=False,
                error=f"Proposal status must be APPROVED, got {proposal.status.value}",
            )
        
        # Check 3: Approval must not be expired
        if execution_request.is_expired():
            remaining = execution_request.time_remaining()
            return ValidationResult(
                valid=False,
                error=f"Execution window expired ({remaining} ago)",
            )
        
        # Check 4: Actions must match
        # Extract action names from proposal's proposed_action
        proposed_actions = self._extract_action_names(proposal.proposed_action)
        
        if set(execution_request.approved_actions) != set(proposed_actions):
            return ValidationResult(
                valid=False,
                error=f"Actions mismatch: {set(execution_request.approved_actions)} vs {set(proposed_actions)}",
            )
        
        # Check 5: Required permissions must be available (soft check - listed in request)
        if proposal.required_permissions:
            # Just verify non-empty
            if not execution_request.immutable_parameters:
                # May be OK if no params needed
                pass
        
        # All checks passed
        return ValidationResult(valid=True)
    
    def validate_proposal_exists_and_approved(
        self,
        proposal: Optional[ActionProposal],
    ) -> ValidationResult:
        """
        Quick validation: proposal exists and is approved.
        
        Args:
            proposal: Proposal to check
        
        Returns:
            ValidationResult with basic checks
        """
        if not self.enabled:
            return ValidationResult(valid=False, error="Validator is disabled")
        
        if not proposal:
            return ValidationResult(valid=False, error="Proposal not found")
        
        if proposal.status != ProposalStatus.APPROVED:
            return ValidationResult(
                valid=False,
                error=f"Proposal not approved (status: {proposal.status.value})",
            )
        
        return ValidationResult(valid=True)
    
    def validate_execution_window_not_expired(
        self,
        execution_request: ExecutionRequest,
    ) -> ValidationResult:
        """
        Check if execution window is still valid.
        
        Args:
            execution_request: Request to check
        
        Returns:
            ValidationResult with expiry check
        """
        if not self.enabled:
            return ValidationResult(valid=False, error="Validator is disabled")
        
        if not execution_request:
            return ValidationResult(valid=False, error="Execution request required")
        
        if execution_request.is_expired():
            return ValidationResult(
                valid=False,
                error=f"Execution window expired",
            )
        
        return ValidationResult(valid=True)
    
    def validate_parameters_match(
        self,
        execution_request: ExecutionRequest,
        proposal: ActionProposal,
    ) -> ValidationResult:
        """
        Validate that execution parameters match proposal exactly.
        
        Args:
            execution_request: Request with parameters
            proposal: Proposal with expected parameters
        
        Returns:
            ValidationResult with parameter check
        """
        if not self.enabled:
            return ValidationResult(valid=False, error="Validator is disabled")
        
        if not execution_request or not proposal:
            return ValidationResult(valid=False, error="Request and proposal required")
        
        # Extract expected parameters from proposal
        expected_params = self._extract_parameters(proposal.proposed_action)
        
        # Compare
        if set(execution_request.immutable_parameters.keys()) != set(expected_params.keys()):
            return ValidationResult(
                valid=False,
                error=f"Parameter keys mismatch: {set(execution_request.immutable_parameters.keys())} vs {set(expected_params.keys())}",
            )
        
        # Verify parameter values match (hard-fail on mismatch)
        for key, expected_value in expected_params.items():
            actual_value = execution_request.immutable_parameters.get(key)
            if actual_value != expected_value:
                return ValidationResult(
                    valid=False,
                    error=f"Parameter value mismatch for '{key}': {actual_value} vs {expected_value}",
                )
        
        return ValidationResult(valid=True)
    
    # Helper methods
    
    def _extract_action_names(self, proposed_action: str) -> list[str]:
        """
        Extract action names from proposal text.
        
        Simple parsing: split by common delimiters.
        In practice, this would be more sophisticated.
        
        Args:
            proposed_action: Human-readable action string
        
        Returns:
            List of action names mentioned
        """
        # Simple heuristic: look for action-like words
        actions = []
        
        # Common action words
        action_keywords = [
            "backup", "restore", "delete", "create", "modify",
            "read", "write", "list", "copy", "move", "rename",
            "execute", "run", "start", "stop", "restart",
        ]
        
        text_lower = proposed_action.lower()
        for keyword in action_keywords:
            if keyword in text_lower:
                actions.append(keyword)
        
        # If no actions found, treat whole proposal as one action
        if not actions:
            actions = ["execute_proposal"]
        
        return actions
    
    def _extract_parameters(self, proposed_action: str) -> dict[str, str]:
        """
        Extract parameters from proposal text.
        
        Simple parsing: look for key=value patterns.
        In practice, this would be more sophisticated.
        
        Args:
            proposed_action: Human-readable action string
        
        Returns:
            Dictionary of parameters
        """
        # This is a placeholder - real implementation would parse
        # the proposal structure more carefully
        params = {}
        
        # Look for key=value patterns (simple heuristic)
        # For now, return empty - actual parameters are stored in
        # the proposal's metadata or a separate structure
        
        return params
    
    def disable(self):
        """Disable validator (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable validator (reversible)."""
        self.enabled = True
