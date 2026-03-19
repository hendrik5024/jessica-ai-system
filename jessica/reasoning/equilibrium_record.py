from dataclasses import dataclass


@dataclass(frozen=True)
class CognitiveEquilibriumRecord:
    equilibrium_id: str
    equilibrium_state: str
    reasoning_balance_score: float
    advisory: str
