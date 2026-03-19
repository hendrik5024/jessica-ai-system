from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailRecord:
    guardrail_id: str
    reflex_level: str
    verification_required: bool
    monitoring_escalated: bool
    advisory: str
