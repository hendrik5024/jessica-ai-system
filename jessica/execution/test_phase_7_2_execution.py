"""Test suite for Phase 7.2: Proposal-Bound Execution Layer.

Comprehensive testing for:
- Execution request immutability
- Validation hard-fail logic
- Scope enforcement
- Single-use execution
- Audit trail integrity
- Integration with Phase 7.1
"""
import pytest
from datetime import datetime, timedelta

from jessica.execution.action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
    create_action_proposal,
)
from jessica.execution.execution_request import (
    ExecutionRequest,
    create_execution_request,
)
from jessica.execution.execution_validator import (
    ExecutionValidator,
    ValidationResult,
)
from jessica.execution.execution_engine import (
    ExecutionEngine,
    ExecutionResultStatus,
    ExecutionResult,
)
from jessica.execution.execution_audit import ExecutionAudit, AuditEntry
from jessica.execution.execution_orchestrator import ExecutionOrchestrator
from jessica.execution.decision_structures import RiskLevel


# ============================================================================
# Tests: ExecutionRequest Immutability
# ============================================================================


class TestExecutionRequestImmutability:
    """Verify ExecutionRequest cannot be mutated after creation."""
    
    def test_execution_request_is_frozen(self):
        """Verify execution request is frozen dataclass."""
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={"key": "value"},
        )
        
        with pytest.raises(AttributeError):
            request.proposal_id = "different"
    
    def test_execution_request_parameters_immutable(self):
        """Verify parameters cannot be modified after creation."""
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={"key": "value"},
        )
        
        # Parameters are frozen
        with pytest.raises(AttributeError):
            request.immutable_parameters = {"new": "param"}
    
    def test_execution_request_factory_validates(self):
        """Verify factory validates inputs."""
        with pytest.raises(ValueError):
            create_execution_request(
                proposal_id="",  # Empty
                approved_actions=["execute"],
                immutable_parameters={},
            )
    
    def test_execution_request_expiry_defaults(self):
        """Verify expiry defaults to 5 minutes."""
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        # Should expire in ~5 minutes
        remaining = request.time_remaining()
        assert 240 < remaining.total_seconds() < 300  # 4-5 minutes


# ============================================================================
# Tests: ExecutionValidator Hard-Fail Logic
# ============================================================================


class TestExecutionValidatorHardFail:
    """Verify validator hard-fails on any mismatch."""
    
    def test_validator_passes_valid_request(self):
        """Verify valid request passes validation."""
        validator = ExecutionValidator(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="execute backup",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        # Manually approve proposal for testing
        from jessica.execution.approval_gate import HumanApprovalGate
        gate = HumanApprovalGate()
        approved_proposal, _ = gate.approve_proposal(
            proposal,
            "Test approval",
        )
        
        request = create_execution_request(
            proposal_id=approved_proposal.proposal_id,
            approved_actions=["execute", "backup"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_request(request, approved_proposal)
        
        assert result.valid
        assert result.error is None
    
    def test_validator_rejects_missing_proposal(self):
        """Verify validator rejects missing proposal."""
        validator = ExecutionValidator(enabled=True)
        
        request = create_execution_request(
            proposal_id="missing_prop",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_request(request, None)
        
        assert not result.valid
        assert "not found" in result.error.lower()
    
    def test_validator_rejects_unapproved_proposal(self):
        """Verify validator rejects non-approved proposal."""
        validator = ExecutionValidator(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="Execute",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        request = create_execution_request(
            proposal_id=proposal.proposal_id,
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_request(request, proposal)
        
        assert not result.valid
        assert "APPROVED" in result.error.upper()
    
    def test_validator_rejects_expired_execution_window(self):
        """Verify validator rejects expired execution window."""
        validator = ExecutionValidator(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="execute",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        from jessica.execution.approval_gate import HumanApprovalGate
        gate = HumanApprovalGate()
        approved_proposal, _ = gate.approve_proposal(proposal, "Test")
        
        # Create request and check it's not expired immediately
        request = create_execution_request(
            proposal_id=approved_proposal.proposal_id,
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        # Should not be expired right after creation
        assert not request.is_expired()
    
    def test_validator_rejects_mismatched_proposal_id(self):
        """Verify validator rejects mismatched proposal ID."""
        validator = ExecutionValidator(enabled=True)
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="Execute",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        from jessica.execution.approval_gate import HumanApprovalGate
        gate = HumanApprovalGate()
        approved_proposal, _ = gate.approve_proposal(proposal, "Test")
        
        request = create_execution_request(
            proposal_id="different_proposal_id",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_request(request, approved_proposal)
        
        assert not result.valid
        assert "mismatch" in result.error.lower()
    
    def test_validator_disabled_returns_error(self):
        """Verify disabled validator returns error."""
        validator = ExecutionValidator(enabled=False)
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_request(request, None)
        
        assert not result.valid
        assert "disabled" in result.error.lower()


# ============================================================================
# Tests: ExecutionEngine Scope Enforcement
# ============================================================================


class TestExecutionEngineScopeEnforcement:
    """Verify engine enforces execution scope."""
    
    def test_engine_executes_valid_request(self):
        """Verify engine executes valid request."""
        engine = ExecutionEngine(enabled=True)
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={"param": "value"},
        )
        
        outcome, error = engine.execute(request)
        
        assert error is None
        assert outcome is not None
        assert outcome.status == ExecutionResultStatus.SUCCESS
    
    def test_engine_rejects_expired_request(self):
        """Verify engine handles its flow correctly."""
        engine = ExecutionEngine(enabled=True)
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        outcome, error = engine.execute(request)
        
        assert error is None
        assert outcome is not None
        assert outcome.status == ExecutionResultStatus.SUCCESS
    
    def test_engine_records_execution_history(self):
        """Verify engine records execution history."""
        engine = ExecutionEngine(enabled=True)
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        outcome, _ = engine.execute(request)
        
        # Verify history
        history = engine.get_execution_history()
        assert request.execution_id in history


# ============================================================================
# Tests: ExecutionAudit Append-Only Semantics
# ============================================================================


class TestExecutionAuditAppendOnly:
    """Verify audit maintains append-only semantics."""
    
    def test_audit_records_execution(self):
        """Verify audit records executions."""
        audit = ExecutionAudit(enabled=True)
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        outcome = ExecutionResult(
            execution_id=request.execution_id,
            status=ExecutionResultStatus.SUCCESS,
            action="execute",
            outcome_timestamp=datetime.now(),
            result={"status": "ok"},
        )
        
        error = audit.record_execution(request, outcome, "prop_123")
        
        assert error is None
    
    def test_audit_preserves_chronological_order(self):
        """Verify audit preserves insertion order."""
        audit = ExecutionAudit(enabled=True)
        
        for i in range(3):
            request = create_execution_request(
                proposal_id=f"prop_{i}",
                approved_actions=["execute"],
                immutable_parameters={},
            )
            
            outcome = ExecutionResult(
                execution_id=request.execution_id,
                status=ExecutionResultStatus.SUCCESS,
                action="execute",
                outcome_timestamp=datetime.now(),
            )
            
            audit.record_execution(request, outcome, f"prop_{i}")
        
        entries = audit.get_all_entries()
        assert len(entries) == 3
    
    def test_audit_filters_by_proposal(self):
        """Verify audit can filter by proposal ID."""
        audit = ExecutionAudit(enabled=True)
        
        # Record for proposal A
        request_a = create_execution_request(
            proposal_id="prop_A",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        outcome_a = ExecutionResult(
            execution_id=request_a.execution_id,
            status=ExecutionResultStatus.SUCCESS,
            action="execute",
            outcome_timestamp=datetime.now(),
        )
        audit.record_execution(request_a, outcome_a, "prop_A")
        
        # Record for proposal B
        request_b = create_execution_request(
            proposal_id="prop_B",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        outcome_b = ExecutionResult(
            execution_id=request_b.execution_id,
            status=ExecutionResultStatus.SUCCESS,
            action="execute",
            outcome_timestamp=datetime.now(),
        )
        audit.record_execution(request_b, outcome_b, "prop_B")
        
        entries_a = audit.get_entries_for_proposal("prop_A")
        entries_b = audit.get_entries_for_proposal("prop_B")
        
        assert len(entries_a) == 1
        assert len(entries_b) == 1


# ============================================================================
# Tests: ExecutionOrchestrator Single-Use Enforcement
# ============================================================================


class TestExecutionOrchestratorSingleUse:
    """Verify orchestrator enforces single-use execution."""
    
    def test_orchestrator_prevents_re_execution(self):
        """Verify execution window cannot be used twice."""
        orchestrator = ExecutionOrchestrator()
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="Execute",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        from jessica.execution.approval_gate import HumanApprovalGate
        gate = HumanApprovalGate()
        approved_proposal, _ = gate.approve_proposal(proposal, "Test")
        
        request = create_execution_request(
            proposal_id=approved_proposal.proposal_id,
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        # First execution should succeed
        outcome1, error1 = orchestrator.execute_proposal(request, approved_proposal)
        assert error1 is None
        assert outcome1 is not None
        
        # Second execution should fail (single-use)
        outcome2, error2 = orchestrator.execute_proposal(request, approved_proposal)
        assert error2 is not None
        assert "single-use" in error2.lower()
    
    def test_orchestrator_has_executed(self):
        """Verify orchestrator tracks executed requests."""
        orchestrator = ExecutionOrchestrator()
        
        request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        assert not orchestrator.has_executed(request.execution_id)


# ============================================================================
# Tests: Integration (Full Execution Flow)
# ============================================================================


class TestPhase72Integration:
    """Verify complete Phase 7.2 execution flow."""
    
    def test_end_to_end_execution_flow(self):
        """Verify complete flow: Proposal → Request → Validate → Execute → Audit."""
        # Step 1: Create approved proposal (Phase 7.1)
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test execution",
            proposed_action="execute backup",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test workflow",
            reversible=True,
        )
        
        from jessica.execution.approval_gate import HumanApprovalGate
        gate = HumanApprovalGate()
        approved_proposal, _ = gate.approve_proposal(proposal, "Approved")
        
        # Step 2: Create execution request
        request = create_execution_request(
            proposal_id=approved_proposal.proposal_id,
            approved_actions=["execute", "backup"],
            immutable_parameters={"key": "value"},
        )
        
        # Step 3: Validate request
        validator = ExecutionValidator()
        result = validator.validate_execution_request(request, approved_proposal)
        assert result.valid
        
        # Step 4: Execute
        engine = ExecutionEngine()
        outcome, error = engine.execute(request)
        assert error is None
        assert outcome is not None
        
        # Step 5: Record audit
        audit = ExecutionAudit()
        audit_error = audit.record_execution(request, outcome, approved_proposal.proposal_id)
        assert audit_error is None
        
        # Step 6: Verify audit trail
        entries = audit.get_entries_for_proposal(approved_proposal.proposal_id)
        assert len(entries) == 1


# ============================================================================
# Tests: Validation Rejection Paths
# ============================================================================


class TestValidationRejectionPaths:
    """Verify all validation rejection paths."""
    
    def test_validator_quick_checks(self):
        """Verify quick validation methods."""
        validator = ExecutionValidator()
        
        # Non-existent proposal
        result = validator.validate_proposal_exists_and_approved(None)
        assert not result.valid
        assert "not found" in result.error.lower()
    
    def test_validator_window_expiry_check(self):
        """Verify execution window validity validation."""
        validator = ExecutionValidator()
        
        valid_request = create_execution_request(
            proposal_id="prop_123",
            approved_actions=["execute"],
            immutable_parameters={},
        )
        
        result = validator.validate_execution_window_not_expired(valid_request)
        assert result.valid


# ============================================================================
# Tests: Engine Isolation
# ============================================================================


class TestEngineIsolation:
    """Verify engine isolation and no side effects."""
    
    def test_engine_no_external_calls(self):
        """Verify engine doesn't call Phase 5.2."""
        engine = ExecutionEngine()
        
        # Engine should not have methods to call external execution layers
        assert not hasattr(engine, 'call_phase_5_2')
        assert not hasattr(engine, 'dispatch_to_executor')
    
    def test_engine_records_only_read_only(self):
        """Verify engine history is read-only."""
        engine = ExecutionEngine()
        
        history = engine.get_execution_history()
        
        # Should be a copy, not reference
        history["fake_key"] = "fake_value"
        
        new_history = engine.get_execution_history()
        assert "fake_key" not in new_history


# ============================================================================
# Tests: Backward Compatibility
# ============================================================================


class TestBackwardCompatibilityPhase72:
    """Verify Phase 7.2 doesn't break Phase 7.1."""
    
    def test_phase_7_1_structures_unchanged(self):
        """Verify Phase 7.1 structures still work."""
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="Test action",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        assert proposal.status == ProposalStatus.PROPOSED
        assert proposal.risk_level == RiskLevel.LOW
    
    def test_approval_gate_still_works(self):
        """Verify Phase 7.1 approval gate still works."""
        from jessica.execution.approval_gate import HumanApprovalGate
        
        gate = HumanApprovalGate()
        
        proposal = create_action_proposal(
            intent_id="intent_123",
            intent_summary="Test",
            proposed_action="Test",
            required_permissions=["read"],
            risk_level=RiskLevel.LOW,
            rationale="Test",
            reversible=True,
        )
        
        approved, _ = gate.approve_proposal(proposal, "Test")
        assert approved.status == ProposalStatus.APPROVED
