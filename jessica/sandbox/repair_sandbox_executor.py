from dataclasses import dataclass
from time import time
from typing import List

from jessica.governance.repair_execution_contract import RepairExecutionContractValidator


@dataclass(frozen=True)
class SandboxExecutionResult:
    execution_id: str
    contract_id: str
    repair_plan_id: str
    start_timestamp: float
    end_timestamp: float
    execution_success: bool
    execution_log: List[str]
    sandbox_violations: List[str]


class RepairSandboxExecutor:

    def __init__(self):
        self._validator = RepairExecutionContractValidator()

    def execute_repair(self, contract, repair_plan) -> SandboxExecutionResult:
        start = time()
        log: List[str] = ["Sandbox context initialized."]
        violations = list(repair_plan.get("sandbox_violations", []))

        if not self._validator.validate(contract):
            log.append("Execution denied: invalid or expired contract.")
            return SandboxExecutionResult(
                execution_id=f"exec-{contract.contract_id}",
                contract_id=contract.contract_id,
                repair_plan_id=repair_plan.get("plan_id", "unknown"),
                start_timestamp=start,
                end_timestamp=time(),
                execution_success=False,
                execution_log=log,
                sandbox_violations=violations,
            )

        if violations:
            log.append("Sandbox violation detected. Execution aborted.")
            return SandboxExecutionResult(
                execution_id=f"exec-{contract.contract_id}",
                contract_id=contract.contract_id,
                repair_plan_id=repair_plan.get("plan_id", "unknown"),
                start_timestamp=start,
                end_timestamp=time(),
                execution_success=False,
                execution_log=log,
                sandbox_violations=violations,
            )

        for action in repair_plan.get("actions", []):
            log.append(f"Executing: {action}")

        log.append("Execution completed.")

        return SandboxExecutionResult(
            execution_id=f"exec-{contract.contract_id}",
            contract_id=contract.contract_id,
            repair_plan_id=repair_plan.get("plan_id", "unknown"),
            start_timestamp=start,
            end_timestamp=time(),
            execution_success=True,
            execution_log=log,
            sandbox_violations=violations,
        )
