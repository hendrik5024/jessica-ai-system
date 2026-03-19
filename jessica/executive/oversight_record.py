from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveOversightRecord:
    oversight_id: str
    guardrail_state: str
    equilibrium_state: str
    strategy_state: str
    advisory: str
