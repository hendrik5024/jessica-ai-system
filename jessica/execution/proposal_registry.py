"""Phase 7.1: Proposal Registry - Append-only immutable proposal archive.

Implements immutable archive pattern:
- Append-only (never delete, never modify)
- Read-only access
- Full proposal history
- No side effects
"""
from __future__ import annotations

from typing import Dict, List, Optional

from jessica.execution.action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
)


class ProposalRegistry:
    """Append-only immutable storage for all action proposals.
    
    Key principle: WRITE-ONCE, READ-ONLY
    - Proposals added once and never modified
    - Full history preserved
    - Enables full audit trail
    - Read operations are safe (no mutations)
    
    This registry creates an authoritative record of all proposals
    that Jessica has generated, enabling accountability and review.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize proposal registry.
        
        Args:
            enabled: Whether registry is active (reversible disable flag)
        """
        self.enabled = enabled
        self._proposals: Dict[str, ActionProposal] = {}
        self._proposal_list: List[str] = []  # Preserve insertion order
    
    def add_proposal(
        self,
        proposal: ActionProposal,
    ) -> Optional[str]:
        """
        Add proposal to registry (append-only).
        
        Args:
            proposal: ActionProposal to store
        
        Returns:
            None on success
            Error message on failure
        """
        if not self.enabled:
            return "Registry is disabled"
        
        if not proposal:
            return "Proposal required"
        
        # Check if already exists (prevent duplicates)
        if proposal.proposal_id in self._proposals:
            return f"Proposal {proposal.proposal_id} already exists"
        
        # Add proposal (append-only)
        self._proposals[proposal.proposal_id] = proposal
        self._proposal_list.append(proposal.proposal_id)
        
        return None
    
    def get_proposal(self, proposal_id: str) -> Optional[ActionProposal]:
        """
        Retrieve proposal by ID (read-only).
        
        Args:
            proposal_id: ID of proposal to retrieve
        
        Returns:
            ActionProposal if found, None if not found
        """
        if not self.enabled:
            return None
        
        return self._proposals.get(proposal_id)
    
    def get_proposals_by_status(
        self,
        status: ProposalStatus,
    ) -> List[ActionProposal]:
        """
        Retrieve all proposals with given status (read-only).
        
        Args:
            status: ProposalStatus to filter by
        
        Returns:
            List of matching proposals (in chronological order)
        """
        if not self.enabled:
            return []
        
        results = []
        for proposal_id in self._proposal_list:
            proposal = self._proposals[proposal_id]
            if proposal.status == status:
                results.append(proposal)
        
        return results
    
    def get_proposals_by_intent(
        self,
        intent_id: str,
    ) -> List[ActionProposal]:
        """
        Retrieve all proposals for a given intent (read-only).
        
        Args:
            intent_id: ID of intent to filter by
        
        Returns:
            List of proposals for intent (in chronological order)
        """
        if not self.enabled:
            return []
        
        results = []
        for proposal_id in self._proposal_list:
            proposal = self._proposals[proposal_id]
            if proposal.intent_id == intent_id:
                results.append(proposal)
        
        return results
    
    def list_all_proposals(self) -> List[ActionProposal]:
        """
        List all proposals in registry (read-only, chronological order).
        
        Args:
            None
        
        Returns:
            List of all proposals in order added
        """
        if not self.enabled:
            return []
        
        return [
            self._proposals[proposal_id]
            for proposal_id in self._proposal_list
        ]
    
    def count_by_status(self) -> Dict[ProposalStatus, int]:
        """
        Count proposals by status (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary mapping status to count
        """
        if not self.enabled:
            return {}
        
        counts: Dict[ProposalStatus, int] = {}
        
        for status in ProposalStatus:
            count = len([
                p for p in self._proposals.values()
                if p.status == status
            ])
            if count > 0:
                counts[status] = count
        
        return counts
    
    def get_registry_stats(self) -> Dict[str, any]:
        """
        Get registry statistics (read-only).
        
        Args:
            None
        
        Returns:
            Dictionary with registry statistics
        """
        if not self.enabled:
            return {}
        
        status_counts = self.count_by_status()
        
        return {
            "total_proposals": len(self._proposals),
            "by_status": status_counts,
            "enabled": self.enabled,
        }
    
    def disable(self):
        """Disable registry (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable registry (reversible)."""
        self.enabled = True
