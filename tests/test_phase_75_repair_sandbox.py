from dataclasses import FrozenInstanceError
from time import time

import pytest

from jessica.governance.repair_execution_contract import (
    RepairExecutionContract,
    RepairExecutionContractIssuer,
)
from jessica.sandbox.repair_sandbox_executor import RepairSandboxExecutor


def _proposal(expiry_offset: float):
    now = time()
    return {
        "proposal_id": "p1",
        "issued_timestamp": now,
        "expiry_timestamp": now + expiry_offset,
        "approved_actions": ("recalibrate",),
    }


def _plan(violations=None):
    return {
        "plan_id": "plan1",
        "actions": ["step1", "step2"],
        "sandbox_violations": violations or [],
    }


def test_execution_blocked_without_valid_contract():

    executor = RepairSandboxExecutor()
    contract = RepairExecutionContract(
        contract_id="c1",
        proposal_id="p1",
        issued_timestamp=time(),
        expiry_timestamp=time() + 10,
        approved_actions=("recalibrate",),
        governance_signature="",
        contract_valid=True,
    )

    result = executor.execute_repair(contract, _plan())

    assert result.execution_success is False


def test_expired_contract_rejected():

    executor = RepairSandboxExecutor()
    issuer = RepairExecutionContractIssuer()

    contract = issuer.issue_contract(_proposal(expiry_offset=-1), "sig")

    result = executor.execute_repair(contract, _plan())

    assert result.execution_success is False


def test_invalid_signature_rejected():

    executor = RepairSandboxExecutor()
    contract = RepairExecutionContract(
        contract_id="c1",
        proposal_id="p1",
        issued_timestamp=time(),
        expiry_timestamp=time() + 10,
        approved_actions=("recalibrate",),
        governance_signature="",
        contract_valid=True,
    )

    result = executor.execute_repair(contract, _plan())

    assert result.execution_success is False


def test_successful_execution_immutable_result():

    executor = RepairSandboxExecutor()
    issuer = RepairExecutionContractIssuer()

    contract = issuer.issue_contract(_proposal(expiry_offset=10), "sig")
    result = executor.execute_repair(contract, _plan())

    assert result.execution_success is True
    assert "Execution completed." in result.execution_log

    with pytest.raises(FrozenInstanceError):
        result.execution_success = False


def test_sandbox_violation_aborts_execution():

    executor = RepairSandboxExecutor()
    issuer = RepairExecutionContractIssuer()

    contract = issuer.issue_contract(_proposal(expiry_offset=10), "sig")
    result = executor.execute_repair(contract, _plan(violations=["violation"]))

    assert result.execution_success is False
    assert result.sandbox_violations == ["violation"]


def test_full_execution_log_recorded():

    executor = RepairSandboxExecutor()
    issuer = RepairExecutionContractIssuer()

    contract = issuer.issue_contract(_proposal(expiry_offset=10), "sig")
    result = executor.execute_repair(contract, _plan())

    assert len(result.execution_log) >= 3
