from typing import Any, cast


class HypothesisEngine:
    """Generates hypotheses from goals and prepares experiment ideas."""

    def __init__(self, reasoning_engine: Any = None) -> None:
        self.reasoning_engine = reasoning_engine

    def generate_hypotheses(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> list[str]:
        """Generate possible hypotheses for a given goal."""

        hypotheses: list[str] = []

        if self.reasoning_engine is not None and hasattr(self.reasoning_engine, "propose_hypotheses"):
            try:
                proposed = self.reasoning_engine.propose_hypotheses(goal, context or {})
                if isinstance(proposed, list):
                    proposed_list = cast(list[Any], proposed)
                    hypotheses = []
                    for raw_item in proposed_list:
                        item = str(raw_item).strip()
                        if item:
                            hypotheses.append(item)
            except (RuntimeError, ValueError, TypeError, AttributeError):
                hypotheses = []

        # Fallback hypotheses if reasoning engine is unavailable.
        if not hypotheses:
            hypotheses = [
                f"Performance issue in {goal} may be caused by inefficient algorithm",
                f"Data processing bottleneck affecting {goal}",
                f"Resource utilization imbalance impacting {goal}",
            ]

        # Keep order while removing duplicates.
        unique: list[str] = []
        seen: set[str] = set()
        for hypothesis in hypotheses:
            if hypothesis not in seen:
                seen.add(hypothesis)
                unique.append(hypothesis)

        return unique

    def create_experiment_code(self, hypothesis: str) -> str:
        """Generate simple Python code that tests the hypothesis."""

        safe_hypothesis = hypothesis.replace("\\", "\\\\").replace('"', '\\"')

        code = (
            "print(\"Testing hypothesis:\")\n"
            f"print(\"{safe_hypothesis}\")\n\n"
            "# Example placeholder experiment\n"
            "result = sum(i * i for i in range(10000))\n\n"
            "print(\"Computation result:\", result)\n"
        )

        return code
