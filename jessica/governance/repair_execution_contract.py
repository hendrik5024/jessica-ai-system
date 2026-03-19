from dataclasses import dataclass
from time import time
from typing import Iterable


@dataclass(frozen=True)
class RepairExecutionContract:
    contract_id: str
    proposal_id: str
    issued_timestamp: float
    expiry_timestamp: float
    approved_actions: tuple[str, ...]
    governance_signature: str
    contract_valid: bool


class RepairExecutionContractIssuer:

    def issue_contract(self, proposal, governance_signature: str) -> RepairExecutionContract:
        if not governance_signature:
            raise ValueError("Governance signature required")

        proposal_id = proposal["proposal_id"]
        issued = proposal["issued_timestamp"]
        expiry = proposal["expiry_timestamp"]
        actions = tuple(proposal.get("approved_actions", ()))

        contract_valid = expiry > issued

        return RepairExecutionContract(
            contract_id=f"contract-{proposal_id}",
            proposal_id=proposal_id,
            issued_timestamp=issued,
            expiry_timestamp=expiry,
            approved_actions=actions,
            governance_signature=governance_signature,
            contract_valid=contract_valid,
        )


class RepairExecutionContractValidator:

    def validate(self, contract: RepairExecutionContract) -> bool:
        if contract is None:
            return False
        if not contract.contract_valid:
            return False
        if self.check_expired(contract):
            return False
        if not self.check_signature(contract):
            return False
        return True

    def check_expired(self, contract: RepairExecutionContract) -> bool:
        return time() > contract.expiry_timestamp

    def check_signature(self, contract: RepairExecutionContract) -> bool:
        return bool(contract.governance_signature)
