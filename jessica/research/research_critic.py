from typing import Any


class ResearchCritic:
    """Evaluates experiment quality before knowledge is stored."""

    def __init__(self, knowledge_memory: Any) -> None:
        self.knowledge_memory = knowledge_memory

    def evaluate(self, experiment_record: dict[str, Any] | None) -> tuple[bool, str]:
        """Return (is_valid, reason) for experiment record quality."""
        if not experiment_record:
            return False, "Empty experiment record"

        if not experiment_record.get("success"):
            return False, "Experiment failed"

        summary = str(experiment_record.get("summary", "")).strip()
        if len(summary) < 10:
            return False, "Result summary too weak"

        return True, "Valid research result"
