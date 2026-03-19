from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailReflexRecord:
    guardrail_id: str
    reflex_state: str
    advisory: str
