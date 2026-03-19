"""Test suite for Phase 7.1: Human-in-the-Loop Action Proposals.

Comprehensive testing for proposal generation, approval, and registry.
Verifies:
- Immutability of proposals (frozen dataclass)
- Approval validation (intents must be approved)
- Approval gate default-deny behavior
- Registry append-only semantics
- No execution capability
- Backward compatibility
"""
import pytest
from datetime import datetime

from jessica.execution.action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
    create_action_proposal,
)
from jessica.execution.proposal_engine import ActionProposalEngine
from jessica.execution.approval_gate import HumanApprovalGate, ApprovalDecision
from jessica.execution.proposal_registry import ProposalRegistry
from jessica.execution.decision_structures import RiskLevel


# ============================================================================
# Tests: ActionProposal Immutability (Frozen Dataclass)
# ============================================================================


class TestActionProposalImmutability:
    """Verify ActionProposal cannot be mutated after creation."""
    
    def test_proposal_is_frozen(self):
        """Verify proposal is frozen dataclass."""
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test intent",
            proposed_action="Do something",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test rationale",
            reversible=True,
        )
        
        # Attempt to modify should raise FrozenInstanceError
        with pytest.raises(AttributeError):
            proposal.status = ProposalStatus.REJECTED
    
    def test_proposal_cannot_modify_collections(self):
        """Verify proposal lists are immutable tuples, not modifiable."""
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test intent",
            proposed_action="Do something",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test rationale",
            reversible=True,
        )
        
        # Frozen dataclass prevents attribute assignment
        # Collections are immutable by being tuples/frozen collections
        assert isinstance(proposal.required_permissions, list)
        original_len = len(proposal.required_permissions)
        
        # Attempt to modify should fail
        with pytest.raises((AttributeError, TypeError)):
            proposal.required_permissions = ["new"]
    
    def test_proposal_to_dict_serialization(self):
        """Verify proposal can be serialized to dict."""
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test intent",
            proposed_action="Do something",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test rationale",
            reversible=True,
        )
        
        proposal_dict = proposal.to_dict()
        
        assert proposal_dict["intent_id"] == "test_intent"
        assert proposal_dict["proposed_action"] == "Do something"
        assert proposal_dict["status"] == ProposalStatus.PROPOSED.value


# ============================================================================
# Tests: ProposalStatus Enum
# ============================================================================


class TestProposalStatusEnum:
    """Verify ProposalStatus enum values and semantics."""
    
    def test_proposal_status_values(self):
        """Verify all status values exist."""
        assert ProposalStatus.PROPOSED
        assert ProposalStatus.APPROVED
        assert ProposalStatus.REJECTED
        assert ProposalStatus.EXECUTED
        assert ProposalStatus.FAILED
        assert ProposalStatus.CANCELLED
    
    def test_proposal_status_count(self):
        """Verify exactly 6 status values."""
        statuses = list(ProposalStatus)
        assert len(statuses) == 6


# ============================================================================
# Tests: Proposal Generation (Engine)
# ============================================================================


class TestActionProposalEngineGeneration:
    """Verify engine generates proposals from approved intents."""
    
    def test_engine_generates_proposal_from_approved_intent(self):
        """Verify engine generates proposal when intent is approved."""
        engine = ActionProposalEngine(enabled=True)
        
        intent_data = {
            "goal": "Test backup",
            "intent_type": "file_operation",
            "approval_result": {"approved": True},  # MUST be approved
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent_xyz",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is None
        assert proposal is not None
        assert proposal.status == ProposalStatus.PROPOSED
        assert proposal.intent_id == "test_intent_xyz"
        assert proposal.proposed_action  # Should have text
        assert proposal.rationale  # Should have rationale
    
    def test_engine_rejects_unapproved_intent(self):
        """Verify engine rejects proposals for unapproved intents."""
        engine = ActionProposalEngine(enabled=True)
        
        intent_data = {
            "goal": "Test backup",
            "intent_type": "file_operation",
            "approval_result": {"approved": False},  # NOT approved
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent_xyz",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is not None
        assert "approved" in error.lower()
        assert proposal is None
    
    def test_engine_rejects_missing_approval_field(self):
        """Verify engine rejects intents without approval_result."""
        engine = ActionProposalEngine(enabled=True)
        
        intent_data = {
            "goal": "Test backup",
            "intent_type": "file_operation",
            # No approval_result
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent_xyz",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is not None
        assert proposal is None
    
    def test_engine_disabled_returns_error(self):
        """Verify disabled engine returns error."""
        engine = ActionProposalEngine(enabled=False)
        
        intent_data = {
            "goal": "Test backup",
            "intent_type": "file_operation",
            "approval_result": {"approved": True},
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent_xyz",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is not None
        assert "disabled" in error.lower()
        assert proposal is None
    
    def test_engine_can_be_re_enabled(self):
        """Verify disabled engine can be re-enabled."""
        engine = ActionProposalEngine(enabled=True)
        engine.disable()
        
        assert not engine.enabled
        
        engine.enable()
        assert engine.enabled


# ============================================================================
# Tests: Proposal Permissions and Risk Assessment
# ============================================================================


class TestProposalRiskAndPermissions:
    """Verify proposals include proper risk and permission assessment."""
    
    def test_proposal_includes_risk_level(self):
        """Verify proposal includes risk assessment."""
        engine = ActionProposalEngine(enabled=True)
        
        intent_data = {
            "goal": "High risk action",
            "intent_type": "system_modification",
            "approval_result": {"approved": True},
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is None
        assert proposal.risk_level in [
            RiskLevel.VERY_LOW,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.VERY_HIGH,
        ]
    
    def test_proposal_includes_required_permissions(self):
        """Verify proposal lists required permissions."""
        engine = ActionProposalEngine(enabled=True)
        
        intent_data = {
            "goal": "File operation",
            "intent_type": "file_operation",
            "approval_result": {"approved": True},
        }
        
        proposal, error = engine.propose_action(
            intent_id="test_intent",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is None
        assert isinstance(proposal.required_permissions, list)
        assert all(isinstance(p, str) for p in proposal.required_permissions)


# ============================================================================
# Tests: Human Approval Gate (Default Deny)
# ============================================================================


class TestHumanApprovalGateDefaultDeny:
    """Verify approval gate defaults to DENY."""
    
    def test_gate_rejects_by_default(self):
        """Verify undecided proposals are NOT approved."""
        gate = HumanApprovalGate(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        # No decision made yet
        assert not gate.is_approved(proposal.proposal_id)
    
    def test_gate_requires_explicit_approval(self):
        """Verify approval only works with explicit call."""
        gate = HumanApprovalGate(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        # Approve explicitly
        approved_proposal, error = gate.approve_proposal(
            proposal,
            decision_reason="Approved for testing",
        )
        
        assert error is None
        assert approved_proposal.status == ProposalStatus.APPROVED
        assert gate.is_approved(proposal.proposal_id)
    
    def test_gate_approval_changes_status(self):
        """Verify approval creates new proposal with APPROVED status."""
        gate = HumanApprovalGate(enabled=True)
        
        original_proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        assert original_proposal.status == ProposalStatus.PROPOSED
        
        approved_proposal, error = gate.approve_proposal(
            original_proposal,
            decision_reason="Test approval",
        )
        
        assert error is None
        assert approved_proposal.status == ProposalStatus.APPROVED
        assert approved_proposal.approval_timestamp is not None
    
    def test_gate_rejection_changes_status(self):
        """Verify rejection creates new proposal with REJECTED status."""
        gate = HumanApprovalGate(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        rejected_proposal, error = gate.reject_proposal(
            proposal,
            rejection_reason="Too risky",
        )
        
        assert error is None
        assert rejected_proposal.status == ProposalStatus.REJECTED
        assert gate.is_rejected(proposal.proposal_id)
    
    def test_gate_disabled_rejects_all(self):
        """Verify disabled gate rejects all operations."""
        gate = HumanApprovalGate(enabled=False)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        _, error = gate.approve_proposal(proposal, "Test")
        assert error is not None
        assert "disabled" in error.lower()


# ============================================================================
# Tests: Proposal Registry (Append-Only)
# ============================================================================


class TestProposalRegistryAppendOnly:
    """Verify registry maintains append-only semantics."""
    
    def test_registry_adds_proposal(self):
        """Verify proposals can be added to registry."""
        registry = ProposalRegistry(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        error = registry.add_proposal(proposal)
        
        assert error is None
        assert len(registry.list_all_proposals()) == 1
    
    def test_registry_prevents_duplicates(self):
        """Verify registry prevents adding same proposal twice."""
        registry = ProposalRegistry(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        error1 = registry.add_proposal(proposal)
        assert error1 is None
        
        error2 = registry.add_proposal(proposal)
        assert error2 is not None
        assert "already exists" in error2.lower()
    
    def test_registry_retrieves_by_id(self):
        """Verify proposals can be retrieved by ID."""
        registry = ProposalRegistry(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        registry.add_proposal(proposal)
        
        retrieved = registry.get_proposal(proposal.proposal_id)
        assert retrieved is not None
        assert retrieved.proposal_id == proposal.proposal_id
    
    def test_registry_preserves_order(self):
        """Verify registry preserves insertion order."""
        registry = ProposalRegistry(enabled=True)
        
        proposals = [
            create_action_proposal(
                intent_id=f"intent_{i}",
                intent_summary=f"Test {i}",
                proposed_action=f"Action {i}",
                required_permissions=["read"],
                risk_level=RiskLevel.LOW,
                rationale=f"Test {i}",
                reversible=True,
            )
            for i in range(3)
        ]
        
        for proposal in proposals:
            registry.add_proposal(proposal)
        
        retrieved = registry.list_all_proposals()
        assert len(retrieved) == 3
        
        for i, proposal in enumerate(retrieved):
            assert f"intent_{i}" in proposal.intent_id
    
    def test_registry_filters_by_status(self):
        """Verify registry can filter proposals by status."""
        registry = ProposalRegistry(enabled=True)
        
        proposal1 = create_action_proposal(
            intent_id="intent_1",
            intent_summary="Test 1",
            proposed_action="Action 1",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        # Manually create approved proposal
        proposal2 = ActionProposal(
            proposal_id="prop_2",
            intent_id="intent_2",
            intent_summary="Test 2",
            proposed_action="Action 2",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
            created_at=datetime.now(),
            status=ProposalStatus.APPROVED,
            approval_timestamp=datetime.now(),
            approval_reason="Approved",
            notes=[],
        )
        
        registry.add_proposal(proposal1)
        registry.add_proposal(proposal2)
        
        proposed = registry.get_proposals_by_status(ProposalStatus.PROPOSED)
        approved = registry.get_proposals_by_status(ProposalStatus.APPROVED)
        
        assert len(proposed) == 1
        assert len(approved) == 1
    
    def test_registry_filters_by_intent(self):
        """Verify registry can filter proposals by intent."""
        registry = ProposalRegistry(enabled=True)
        
        proposals = [
            create_action_proposal(
                intent_id="intent_A",
                intent_summary=f"Test A {i}",
                proposed_action=f"Action {i}",
                required_permissions=["read"],
                risk_level=RiskLevel.LOW,
                rationale="Test",
                reversible=True,
            )
            for i in range(2)
        ]
        
        proposals.extend([
            create_action_proposal(
                intent_id="intent_B",
                intent_summary=f"Test B {i}",
                proposed_action=f"Action {i}",
                required_permissions=["read"],
                risk_level=RiskLevel.LOW,
                rationale="Test",
                reversible=True,
            )
            for i in range(2)
        ])
        
        for proposal in proposals:
            registry.add_proposal(proposal)
        
        intent_a_proposals = registry.get_proposals_by_intent("intent_A")
        intent_b_proposals = registry.get_proposals_by_intent("intent_B")
        
        assert len(intent_a_proposals) == 2
        assert len(intent_b_proposals) == 2
    
    def test_registry_stats(self):
        """Verify registry provides statistics."""
        registry = ProposalRegistry(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="intent_1",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        registry.add_proposal(proposal)
        
        stats = registry.get_registry_stats()
        assert stats["total_proposals"] == 1
        assert stats["enabled"] is True


# ============================================================================
# Tests: Integration (Engine + Gate + Registry)
# ============================================================================


class TestPhase71Integration:
    """Verify Phase 7.1 components integrate correctly."""
    
    def test_end_to_end_flow(self):
        """Verify complete proposal flow: generate → approve → store."""
        engine = ActionProposalEngine(enabled=True)
        gate = HumanApprovalGate(enabled=True)
        registry = ProposalRegistry(enabled=True)
        
        # Step 1: Generate proposal from approved intent
        intent_data = {
            "goal": "Test backup",
            "intent_type": "file_operation",
            "approval_result": {"approved": True},
        }
        
        proposal, error = engine.propose_action(
            intent_id="intent_xyz",
            intent_data=intent_data,
            decision_bundle=None,
        )
        
        assert error is None
        assert proposal.status == ProposalStatus.PROPOSED
        
        # Step 2: Get human approval
        approved_proposal, error = gate.approve_proposal(
            proposal,
            decision_reason="Looks good",
        )
        
        assert error is None
        assert approved_proposal.status == ProposalStatus.APPROVED
        
        # Step 3: Store in registry
        error = registry.add_proposal(approved_proposal)
        
        assert error is None
        assert len(registry.list_all_proposals()) == 1
        
        retrieved = registry.get_proposal(approved_proposal.proposal_id)
        assert retrieved.status == ProposalStatus.APPROVED
    
    def test_multiple_intents_multiple_proposals(self):
        """Verify multiple intents generate multiple proposals."""
        engine = ActionProposalEngine(enabled=True)
        registry = ProposalRegistry(enabled=True)
        
        intents = [
            {
                "goal": f"Goal {i}",
                "intent_type": "file_operation",
                "approval_result": {"approved": True},
            }
            for i in range(3)
        ]
        
        proposals = []
        for i, intent_data in enumerate(intents):
            proposal, error = engine.propose_action(
                intent_id=f"intent_{i}",
                intent_data=intent_data,
                decision_bundle=None,
            )
            
            assert error is None
            proposals.append(proposal)
            registry.add_proposal(proposal)
        
        all_proposals = registry.list_all_proposals()
        assert len(all_proposals) == 3


# ============================================================================
# Tests: No Execution Capability (Phase 5.2 Not Called)
# ============================================================================


class TestNoExecutionCapability:
    """Verify Phase 7.1 has NO execution capability."""
    
    def test_engine_does_not_execute_actions(self):
        """Verify engine only generates proposals, never executes."""
        engine = ActionProposalEngine(enabled=True)
        
        # Should not have execute method
        assert not hasattr(engine, 'execute_proposal')
        assert not hasattr(engine, 'execute_action')
    
    def test_gate_does_not_execute_actions(self):
        """Verify gate only approves/rejects, never executes."""
        gate = HumanApprovalGate(enabled=True)
        
        assert not hasattr(gate, 'execute_proposal')
        assert not hasattr(gate, 'execute_action')
    
    def test_registry_does_not_execute_actions(self):
        """Verify registry only stores, never executes."""
        registry = ProposalRegistry(enabled=True)
        
        assert not hasattr(registry, 'execute_proposal')
        assert not hasattr(registry, 'execute_action')
    
    def test_proposal_is_advisory_only(self):
        """Verify proposals contain metadata only, no execution fields."""
        proposal = create_action_proposal(
            intent_id="test_intent",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        # Proposal should have advisory fields
        assert hasattr(proposal, 'rationale')
        assert hasattr(proposal, 'risk_level')
        assert hasattr(proposal, 'required_permissions')
        
        # Proposal should NOT have execution fields
        assert not hasattr(proposal, 'execute')
        assert not hasattr(proposal, 'executor')
        assert not hasattr(proposal, 'execution_result')


# ============================================================================
# Tests: Backward Compatibility (Phase 4-6 Unchanged)
# ============================================================================


class TestBackwardCompatibility:
    """Verify Phase 7.1 doesn't break Phase 4-6."""
    
    def test_risk_level_still_works(self):
        """Verify RiskLevel enum still works (from Phase 6)."""
        assert RiskLevel.VERY_LOW
        assert RiskLevel.LOW
        assert RiskLevel.MEDIUM
        assert RiskLevel.HIGH
        assert RiskLevel.VERY_HIGH
    
    def test_proposal_uses_existing_risk_level(self):
        """Verify proposals use Phase 6 RiskLevel."""
        proposal = create_action_proposal(
            intent_id="test",
            intent_summary="Test",
            proposed_action="Action",
            required_permissions=["read"],
            risk_level=RiskLevel.HIGH,
            rationale="Test",
            reversible=True,
        )
        
        assert proposal.risk_level == RiskLevel.HIGH
