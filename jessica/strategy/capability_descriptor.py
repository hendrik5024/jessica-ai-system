from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    name: str
    description: str
    version: str
    inputs: Tuple[str, ...]
    outputs: Tuple[str, ...]
    risk_level: str
    registered_at: datetime
