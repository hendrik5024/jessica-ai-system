from dataclasses import FrozenInstanceError
from time import time

import pytest

from jessica.governance.repair_execution_contract import (
    RepairExecutionContract,
    RepairExecutionContractIssuer,
    RepairExecutionContractValidator,
)


def _proposal(expiry_offset: float):
    now = time()
    return {
        "proposal_id": "p1",
        "issued_timestamp": now,
        "expiry_timestamp": now + expiry_offset,
        "approved_actions": ("recalibrate",),
    }


def test_contract_immutable():

    contract = RepairExecutionContract(
        contract_id="c1",
        proposal_id="p1",
        issued_timestamp=time(),
        expiry_timestamp=time() + 10,
        approved_actions=("recalibrate",),
        governance_signature="sig",
        contract_valid=True,
    )

    with pytest.raises(FrozenInstanceError):
        contract.contract_id = "c2"


def test_expiry_enforcement():

    issuer = RepairExecutionContractIssuer()
    validator = RepairExecutionContractValidator()

    contract = issuer.issue_contract(_proposal(expiry_offset=-1), "sig")

    assert validator.validate(contract) is False


def test_signature_validation():

    contract = RepairExecutionContract(
        contract_id="c1",
        proposal_id="p1",
        issued_timestamp=time(),
        expiry_timestamp=time() + 10,
        approved_actions=("recalibrate",),
        governance_signature="",
        contract_valid=True,
    )

    validator = RepairExecutionContractValidator()

    assert validator.validate(contract) is False


def test_fail_closed_validator():

    contract = RepairExecutionContract(
        contract_id="c1",
        proposal_id="p1",
        issued_timestamp=time(),
        expiry_timestamp=time() + 10,
        approved_actions=("recalibrate",),
        governance_signature="sig",
        contract_valid=False,
    )

    validator = RepairExecutionContractValidator()

    assert validator.validate(contract) is False


def test_contract_required_before_execution_permission():

    issuer = RepairExecutionContractIssuer()
    validator = RepairExecutionContractValidator()

    contract = issuer.issue_contract(_proposal(expiry_offset=10), "sig")

    assert validator.validate(contract) is True
