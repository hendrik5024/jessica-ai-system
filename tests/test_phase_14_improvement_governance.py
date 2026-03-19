from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.improvement_proposal import ImprovementProposal
from jessica.improvement_registry import ImprovementRegistry
from jessica.improvement_audit import ImprovementAudit
from jessica.improvement_executor import ImprovementExecutor


def _proposal(pid: str, module: str, version: int = 1) -> ImprovementProposal:
    return ImprovementProposal(
        proposal_id=pid,
        target_module=module,
        description="desc",
        rationale="rationale",
        risk_level="low",
        proposed_changes={"version": version},
        created_at=datetime(2026, 2, 9, 12, 0, 0),
    )


def test_proposal_immutable():
    proposal = _proposal("p1", "mod")
    with pytest.raises(FrozenInstanceError):
        proposal.description = "new"


def test_registry_add_and_get():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    assert registry.get_proposal("p1") == proposal


def test_registry_append_only():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    with pytest.raises(ValueError):
        registry.add_proposal(proposal)


def test_registry_list_deterministic():
    registry = ImprovementRegistry()
    p1 = _proposal("p1", "mod")
    p2 = _proposal("p2", "mod")
    registry.add_proposal(p1)
    registry.add_proposal(p2)
    assert [p.proposal_id for p in registry.list_proposals()] == ["p1", "p2"]


def test_approve_proposal_sets_decision():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    assert registry.get_decision("p1") == "approved"


def test_reject_proposal_sets_decision():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.reject_proposal("p1")
    assert registry.get_decision("p1") == "rejected"


def test_cannot_approve_rejected():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.reject_proposal("p1")
    with pytest.raises(ValueError):
        registry.approve_proposal("p1")


def test_cannot_reject_approved():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    with pytest.raises(ValueError):
        registry.reject_proposal("p1")


def test_decision_log_append_only():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    assert registry.get_decision_log("p1") == ["approved"]


def test_executor_requires_approval():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    with pytest.raises(PermissionError):
        executor.apply_improvement("p1")


def test_executor_applies_after_approval():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    version = executor.apply_improvement("p1")
    assert version == 1


def test_version_increments():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    p1 = _proposal("p1", "mod")
    p2 = _proposal("p2", "mod")
    registry.add_proposal(p1)
    registry.add_proposal(p2)
    registry.approve_proposal("p1")
    registry.approve_proposal("p2")
    executor.apply_improvement("p1")
    version = executor.apply_improvement("p2")
    assert version == 2


def test_rollback_restores_previous_version():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    executor.apply_improvement("p1")
    rolled = executor.rollback_improvement("p1")
    assert rolled == 0


def test_rollback_without_apply_returns_none():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    assert executor.rollback_improvement("p1") is None


def test_audit_history_records_apply_and_rollback():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    executor.apply_improvement("p1")
    executor.rollback_improvement("p1")
    history = audit.get_change_history("mod")
    assert len(history) == 2


def test_audit_append_only():
    audit = ImprovementAudit()
    audit.record_change("p1", "mod", 1, datetime(2026, 2, 9, 12, 0, 0))
    audit.record_change("p1", "mod", 0, datetime(2026, 2, 9, 12, 1, 0))
    assert audit.count() == 2


def test_validate_improvement_false_when_missing():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    assert executor.validate_improvement("missing") is False


def test_validate_improvement_true_when_approved():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    assert executor.validate_improvement("p1") is True


def test_get_module_version_default_zero():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    assert executor.get_module_version("mod") == 0


def test_get_module_version_after_apply():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    registry.approve_proposal("p1")
    executor.apply_improvement("p1")
    assert executor.get_module_version("mod") == 1


def test_registry_decision_none_initially():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    assert registry.get_decision("p1") is None


def test_apply_improvement_missing_proposal_raises_value_error():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    with pytest.raises(PermissionError):
        executor.apply_improvement("missing")


def test_retrieving_decision_log_empty():
    registry = ImprovementRegistry()
    proposal = _proposal("p1", "mod")
    registry.add_proposal(proposal)
    assert registry.get_decision_log("p1") == []


def test_deterministic_proposal_handling():
    registry = ImprovementRegistry()
    p1 = _proposal("p1", "mod")
    p2 = _proposal("p2", "mod")
    registry.add_proposal(p1)
    registry.add_proposal(p2)
    assert [p.proposal_id for p in registry.list_proposals()] == ["p1", "p2"]


def test_approval_does_not_change_proposal():
    registry = ImprovementRegistry()
    p1 = _proposal("p1", "mod")
    registry.add_proposal(p1)
    registry.approve_proposal("p1")
    assert registry.get_proposal("p1").description == "desc"


def test_audit_history_correct_module():
    audit = ImprovementAudit()
    audit.record_change("p1", "mod", 1, datetime(2026, 2, 9, 12, 0, 0))
    audit.record_change("p2", "other", 1, datetime(2026, 2, 9, 12, 1, 0))
    history = audit.get_change_history("mod")
    assert len(history) == 1


def test_executor_deterministic_versioning():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    p1 = _proposal("p1", "mod")
    p2 = _proposal("p2", "mod")
    registry.add_proposal(p1)
    registry.add_proposal(p2)
    registry.approve_proposal("p1")
    registry.approve_proposal("p2")
    v1 = executor.apply_improvement("p1")
    v2 = executor.apply_improvement("p2")
    assert (v1, v2) == (1, 2)


def test_orchestrator_without_apply_keeps_version_zero():
    registry = ImprovementRegistry()
    audit = ImprovementAudit()
    executor = ImprovementExecutor(registry, audit)
    assert executor.get_module_version("mod") == 0
