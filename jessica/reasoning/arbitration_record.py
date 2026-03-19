from dataclasses import dataclass


@dataclass(frozen=True)
class ArbitrationRecord:
    arbitration_id: str
    selected_answer: str
    competing_answers: int
    alignment_score: float
    confidence_score: float
    arbitration_reason: str
