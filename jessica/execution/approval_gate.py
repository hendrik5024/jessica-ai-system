"""Phase 7.1: Human Approval Gate - Explicit human authorization required.

Implements fail-safe approval pattern:
- Default DENY (nothing approved unless explicitly authorized)
- No implicit approvals
- Explicit human decision required
- Full audit trail
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from jessica.execution.action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
)


@dataclass(frozen=True)
class ApprovalDecision:
    """Immutable record of approval decision."""
    proposal_id: str
    approved: bool                  # True = approved, False = rejected
    decided_at: datetime
    decision_reason: str            # Why approved/rejected
    approved_by: str = "human"      # Who made decision (default: human)


class HumanApprovalGate:
    """Explicit human-controlled approval gate.
    
    Key principle: DEFAULT DENY
    - Nothing is approved unless human explicitly approves
    - Rejections are explicit
    - All decisions are audited
    - No implicit approvals or defaults
    
    This is the critical safety boundary between proposal (Phase 7.1)
    and execution (Phase 5.5).
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize approval gate.
        
        Args:
            enabled: Whether gate is active (reversible disable flag)
        """
        self.enabled = enabled
        self.decisions: dict[str, ApprovalDecision] = {}
    
    def approve_proposal(
        self,
        proposal: ActionProposal,
        decision_reason: str = "Approved by human",
    ) -> Tuple[ActionProposal, Optional[str]]:
        """
        Explicitly approve a proposal.
        
        Human must actively approve - there is no default approval.
        
        Args:
            proposal: ActionProposal to approve
            decision_reason: Reason for approval
        
        Returns:
            (Approved proposal copy, None) on success
            (None, error) on failure
        """
        if not self.enabled:
            return None, "Approval gate is disabled"
        
        if not proposal:
            return None, "Proposal required for approval"
        
        if not decision_reason:
            return None, "Approval reason required"
        
        # Record decision
        decision = ApprovalDecision(
            proposal_id=proposal.proposal_id,
            approved=True,
            decided_at=datetime.now(),
            decision_reason=decision_reason,
        )
        
        self.decisions[proposal.proposal_id] = decision
        
        # Create approved copy (new instance with updated status)
        approved_proposal = ActionProposal(
            proposal_id=proposal.proposal_id,
            intent_id=proposal.intent_id,
            intent_summary=proposal.intent_summary,
            proposed_action=proposal.proposed_action,
            required_permissions=proposal.required_permissions,
            risk_level=proposal.risk_level,
            rationale=proposal.rationale,
            reversible=proposal.reversible,
            created_at=proposal.created_at,
            status=ProposalStatus.APPROVED,
            approval_timestamp=decision.decided_at,
            approval_reason=decision_reason,
            notes=list(proposal.notes),
        )
        
        return approved_proposal, None
    
    def reject_proposal(
        self,
        proposal: ActionProposal,
        rejection_reason: str,
    ) -> Tuple[ActionProposal, Optional[str]]:
        """
        Explicitly reject a proposal.
        
        Args:
            proposal: ActionProposal to reject
            rejection_reason: Reason for rejection
        
        Returns:
            (Rejected proposal copy, None) on success
            (None, error) on failure
        """
        if not self.enabled:
            return None, "Approval gate is disabled"
        
        if not proposal:
            return None, "Proposal required for rejection"
        
        if not rejection_reason:
            return None, "Rejection reason required"
        
        # Record decision
        decision = ApprovalDecision(
            proposal_id=proposal.proposal_id,
            approved=False,
            decided_at=datetime.now(),
            decision_reason=rejection_reason,
        )
        
        self.decisions[proposal.proposal_id] = decision
        
        # Create rejected copy
        rejected_proposal = ActionProposal(
            proposal_id=proposal.proposal_id,
            intent_id=proposal.intent_id,
            intent_summary=proposal.intent_summary,
            proposed_action=proposal.proposed_action,
            required_permissions=proposal.required_permissions,
            risk_level=proposal.risk_level,
            rationale=proposal.rationale,
            reversible=proposal.reversible,
            created_at=proposal.created_at,
            status=ProposalStatus.REJECTED,
            approval_timestamp=datetime.now(),
            approval_reason=rejection_reason,
            notes=list(proposal.notes),
        )
        
        return rejected_proposal, None
    
    def get_approval_status(self, proposal_id: str) -> Optional[ApprovalDecision]:
        """
        Get approval decision for a proposal (read-only).
        
        Args:
            proposal_id: ID of proposal
        
        Returns:
            ApprovalDecision if decision made, None if no decision yet
        """
        if not self.enabled:
            return None
        
        return self.decisions.get(proposal_id)
    
    def is_approved(self, proposal_id: str) -> bool:
        """
        Check if proposal is explicitly approved.
        
        Args:
            proposal_id: ID of proposal
        
        Returns:
            True only if explicitly approved
            False for anything else (rejected, undecided, missing)
        """
        if not self.enabled:
            return False
        
        decision = self.decisions.get(proposal_id)
        
        # DEFAULT DENY: Only True if explicitly approved
        if decision is None:
            return False  # Not yet decided = not approved
        
        return decision.approved
    
    def is_rejected(self, proposal_id: str) -> bool:
        """
        Check if proposal is explicitly rejected.
        
        Args:
            proposal_id: ID of proposal
        
        Returns:
            True only if explicitly rejected
        """
        if not self.enabled:
            return False
        
        decision = self.decisions.get(proposal_id)
        
        if decision is None:
            return False  # Not yet decided = not rejected
        
        return not decision.approved
    
    def get_decision_trail(self) -> dict[str, ApprovalDecision]:
        """
        Get full decision trail (read-only audit log).
        
        Args:
            None
        
        Returns:
            Dictionary of all decisions made
        """
        if not self.enabled:
            return {}
        
        return dict(self.decisions)  # Return copy, not reference
    
    def disable(self):
        """Disable approval gate (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable approval gate (reversible)."""
        self.enabled = True
