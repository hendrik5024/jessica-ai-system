from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CapabilityAssessment:
    goal: str
    achievable: bool
    required_capabilities: Tuple[str, ...]
    missing_capabilities: Tuple[str, ...]
    reasoning_summary: str
