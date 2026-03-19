from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CapabilityInstallationRecord:
    proposal_id: str
    capability_name: str
    installed_by: str
    installed_at: datetime
    success: bool
