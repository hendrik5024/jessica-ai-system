from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ConsistencyRecord:
    reasoning_id: str
    contradictions_found: bool
    contradiction_descriptions: List[str]
    confidence_score: float
