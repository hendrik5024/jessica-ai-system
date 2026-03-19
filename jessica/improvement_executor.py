"""Phase 14 — Self-Improvement Governance: executor with approval and rollback."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from jessica.improvement_registry import ImprovementRegistry
from jessica.improvement_audit import ImprovementAudit


class ImprovementExecutor:
    def __init__(self, registry: ImprovementRegistry, audit: ImprovementAudit) -> None:
        self.registry = registry
        self.audit = audit
        self._module_versions: Dict[str, int] = {}
        self._applied: Dict[str, Dict[str, int]] = {}

    def validate_improvement(self, proposal_id: str) -> bool:
        proposal = self.registry.get_proposal(proposal_id)
        if not proposal:
            return False
        return self.registry.get_decision(proposal_id) == "approved"

    def apply_improvement(self, proposal_id: str) -> int:
        if not self.validate_improvement(proposal_id):
            raise PermissionError("Improvement not approved")
        proposal = self.registry.get_proposal(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        current_version = self._module_versions.get(proposal.target_module, 0)
        new_version = current_version + 1
        self._module_versions[proposal.target_module] = new_version
        self._applied[proposal_id] = {
            "module": proposal.target_module,
            "previous": current_version,
            "current": new_version,
        }
        self.audit.record_change(proposal_id, proposal.target_module, new_version, datetime.now())
        return new_version

    def rollback_improvement(self, proposal_id: str) -> Optional[int]:
        applied = self._applied.get(proposal_id)
        if not applied:
            return None
        module = applied["module"]
        previous = applied["previous"]
        self._module_versions[module] = previous
        self.audit.record_change(proposal_id, module, previous, datetime.now())
        return previous

    def get_module_version(self, module: str) -> int:
        return self._module_versions.get(module, 0)
