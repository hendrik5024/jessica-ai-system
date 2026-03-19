from typing import Dict
from datetime import datetime

from .improvement_governor import ImprovementGovernor
from .capability_installation_record import CapabilityInstallationRecord


class CapabilityInstaller:
    def __init__(self, governor: ImprovementGovernor):
        self.governor = governor
        self._installations: Dict[str, CapabilityInstallationRecord] = {}

    def install_capability(
        self,
        proposal_id: str,
        capability_name: str,
        installer: str,
    ) -> CapabilityInstallationRecord:
        decision = self.governor.get_decision(proposal_id)

        if decision is None or decision.approved is False:
            raise PermissionError("Capability installation not approved")

        record = CapabilityInstallationRecord(
            proposal_id=proposal_id,
            capability_name=capability_name,
            installed_by=installer,
            installed_at=datetime.utcnow(),
            success=True,
        )

        self._installations[proposal_id] = record
        return record

    def get_installation(self, proposal_id: str):
        return self._installations.get(proposal_id)
