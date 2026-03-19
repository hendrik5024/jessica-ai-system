import re
from typing import Any


class ResearchPriorityManager:
    """Scores and ranks generated hypotheses for directed exploration."""

    def __init__(self, model_connector: Any) -> None:
        self.model = model_connector

    def score_hypothesis(self, hypothesis: str) -> int:

        prompt = f"""
Evaluate the research value of this hypothesis.

Hypothesis:
{hypothesis}

Score from 1-10 based on:
- potential impact
- feasibility
- novelty

Return only the number.
"""

        response = self.model.generate(prompt)
        return self._parse_score(str(response))

    def rank(self, hypotheses: list[str]) -> list[str]:

        scored: list[tuple[int, str]] = []

        for hypothesis in hypotheses:
            score = self.score_hypothesis(hypothesis)
            scored.append((score, hypothesis))

        scored.sort(reverse=True)

        return [hypothesis for _, hypothesis in scored]

    @staticmethod
    def _parse_score(response: str) -> int:
        """Parse score from free-form model output, defaulting safely to 5."""
        text = response.strip()
        match = re.search(r"\d+", text)
        if not match:
            return 5

        try:
            score = int(match.group(0))
        except ValueError:
            return 5

        if score < 1:
            return 1
        if score > 10:
            return 10

        return score
