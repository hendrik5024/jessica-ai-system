"""Phase 7.1: Action Proposal Engine - Generates proposals from approved intents.

Input: Approved intent (Phase 5.1.5) + decision context (Phase 6)
Output: ActionProposal (advisory, not executed)

This layer does NOT execute, approve, or trigger actions.
It only generates structured proposals for human review.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from jessica.execution.action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
    create_action_proposal,
)
from jessica.execution.decision_structures import RiskLevel, DecisionBundle


class ActionProposalEngine:
    """Generates action proposals from approved intents and decision context.
    
    Workflow:
    1. Receive approved intent (Phase 5.1.5)
    2. Consult decision context (Phase 6)
    3. Generate structured ActionProposal
    4. Return proposal (NOT executed)
    
    Key constraints:
    - Input must be from approved intent
    - Output is advisory-only
    - No execution hooks
    - No background processing
    - Fully reversible (disable flag)
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize proposal engine.
        
        Args:
            enabled: Whether engine is enabled (reversible disable flag)
        """
        self.enabled = enabled
    
    def propose_action(
        self,
        intent_id: str,
        intent_data: Dict[str, Any],
        decision_bundle: Optional[DecisionBundle] = None,
    ) -> Tuple[Optional[ActionProposal], Optional[str]]:
        """
        Generate action proposal from approved intent.
        
        Args:
            intent_id: ID of approved intent (from Phase 5.1.5)
            intent_data: Approved intent data including:
                - goal: Human goal/intent
                - intent_type: Type of action (e.g., "system_operation")
                - approval_result: Approval status (must be approved)
            decision_bundle: Optional decision context from Phase 6
        
        Returns:
            (ActionProposal, None) on success
            (None, error_message) on failure
        """
        if not self.enabled:
            return None, "Action proposal engine is disabled"
        
        # Validate inputs
        if not intent_id or not intent_data:
            return None, "Intent ID and data required"
        
        # CRITICAL: Verify intent is approved
        approval_result = intent_data.get("approval_result", {})
        if not approval_result.get("approved"):
            return None, "Intent must be approved before proposing action"
        
        # Extract intent information
        intent_summary = intent_data.get("goal", "Unknown intent")
        intent_type = intent_data.get("intent_type", "action")
        
        # Generate proposal based on intent
        proposed_action = self._generate_proposed_action(intent_type, intent_summary)
        required_permissions = self._determine_permissions(intent_type)
        risk_level = self._assess_risk(intent_type, decision_bundle)
        rationale = self._generate_rationale(intent_summary, decision_bundle)
        reversible = self._assess_reversibility(intent_type, decision_bundle)
        
        # Create proposal
        proposal = create_action_proposal(
            intent_id=intent_id,
            intent_summary=intent_summary,
            proposed_action=proposed_action,
            required_permissions=required_permissions,
            risk_level=risk_level,
            rationale=rationale,
            reversible=reversible,
        )
        
        return proposal, None
    
    def propose_actions_from_decision(
        self,
        intent_id: str,
        intent_data: Dict[str, Any],
        decision_bundle: DecisionBundle,
    ) -> Tuple[List[ActionProposal], Optional[str]]:
        """
        Generate multiple action proposals from decision bundle.
        
        If decision bundle contains multiple recommendations, generate
        proposal for each one.
        
        Args:
            intent_id: ID of approved intent
            intent_data: Approved intent data
            decision_bundle: Decision context with multiple options
        
        Returns:
            (List[ActionProposal], None) on success
            ([], error_message) on failure
        """
        if not self.enabled:
            return [], "Action proposal engine is disabled"
        
        proposals = []
        
        # Generate proposal for recommended option
        proposal, error = self.propose_action(intent_id, intent_data, decision_bundle)
        
        if error:
            return [], error
        
        if proposal:
            proposals.append(proposal)
        
        return proposals, None
    
    def _generate_proposed_action(self, intent_type: str, intent_summary: str) -> str:
        """Generate human-readable action description."""
        if intent_type == "system_operation":
            return f"Execute: {intent_summary}"
        elif intent_type == "file_operation":
            return f"File operation: {intent_summary}"
        elif intent_type == "network_operation":
            return f"Network operation: {intent_summary}"
        else:
            return f"Proposed action: {intent_summary}"
    
    def _determine_permissions(self, intent_type: str) -> List[str]:
        """Determine required permissions for action."""
        permissions = []
        
        if intent_type == "system_operation":
            permissions.extend(["system_read", "system_execute"])
        elif intent_type == "file_operation":
            permissions.extend(["file_read", "file_write"])
        elif intent_type == "network_operation":
            permissions.extend(["network_read", "network_write"])
        
        return permissions
    
    def _assess_risk(
        self,
        intent_type: str,
        decision_bundle: Optional[DecisionBundle],
    ) -> RiskLevel:
        """Assess risk level of proposed action."""
        # Default assessment based on intent type
        risk_map = {
            "file_operation": RiskLevel.LOW,
            "network_operation": RiskLevel.MEDIUM,
            "system_operation": RiskLevel.HIGH,
        }
        
        base_risk = risk_map.get(intent_type, RiskLevel.MEDIUM)
        
        # Adjust if decision bundle provides risk context
        if decision_bundle and decision_bundle.evaluations:
            # If any evaluation shows high risk, escalate
            for evaluation in decision_bundle.evaluations.values():
                if evaluation.risk_level == RiskLevel.VERY_HIGH:
                    return RiskLevel.HIGH
                if evaluation.risk_level == RiskLevel.HIGH:
                    base_risk = RiskLevel.MEDIUM if base_risk == RiskLevel.LOW else base_risk
        
        return base_risk
    
    def _generate_rationale(
        self,
        intent_summary: str,
        decision_bundle: Optional[DecisionBundle],
    ) -> str:
        """Generate rationale for proposal."""
        rationale = f"Proposed to fulfill: {intent_summary}"
        
        if decision_bundle and decision_bundle.recommendation_rationale:
            rationale += f". {decision_bundle.recommendation_rationale}"
        
        return rationale
    
    def _assess_reversibility(
        self,
        intent_type: str,
        decision_bundle: Optional[DecisionBundle],
    ) -> bool:
        """Assess whether action can be reversed."""
        # Most operations are reversible unless they're destructive
        reversible_types = {"system_operation", "file_operation", "network_operation"}
        
        if intent_type not in reversible_types:
            return True
        
        # File operations are generally reversible
        if intent_type == "file_operation":
            return True
        
        # System operations might not be reversible
        if intent_type == "system_operation":
            return False
        
        return True
    
    def validate_proposal(self, proposal: ActionProposal) -> Tuple[bool, Optional[str]]:
        """
        Validate proposal structure and constraints.
        
        Args:
            proposal: ActionProposal to validate
        
        Returns:
            (True, None) if valid
            (False, error_message) if invalid
        """
        if not proposal.intent_id:
            return False, "Proposal must reference an intent"
        
        if not proposal.proposed_action:
            return False, "Proposal must describe an action"
        
        if not proposal.required_permissions:
            return False, "Proposal must list required permissions"
        
        if not proposal.rationale:
            return False, "Proposal must include rationale"
        
        return True, None
    
    def disable(self):
        """Disable proposal engine (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable proposal engine (reversible)."""
        self.enabled = True
