from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AlignmentRecord:
    analysis_id: str
    answers_compared: int
    aligned: bool
    divergence_notes: List[str]
    alignment_score: float
