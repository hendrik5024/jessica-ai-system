"""Decision support convenience wrapper for Phase 9.2 live loop."""

from __future__ import annotations

from jessica.execution.decision_orchestrator import DecisionOrchestrator as _DecisionOrchestrator


class DecisionOrchestrator(_DecisionOrchestrator):
    """Adds lightweight question answering for live conversations."""

    def answer_question(self, question: str) -> str | None:
        """
        Provide reasoning-based answers for simple math and knowledge queries.
        Returns None if unable to answer.
        """

        q = question.lower().strip()

        # simple math detection
        if "+" in q:
            try:
                parts = q.replace("what is", "").replace("?", "").split("+")
                numbers = [int(p.strip()) for p in parts]
                return str(sum(numbers))
            except Exception:
                pass

        # basic knowledge responses
        knowledge = {
            "capital of france": "The capital of France is Paris.",
            "how many days is there in a week": "There are seven days in a week.",
            "what is your name": "My name is Jessica.",
        }

        for k, v in knowledge.items():
            if k in q:
                return v

        return None
