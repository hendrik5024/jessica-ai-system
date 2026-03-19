from typing import Any
import re


class ResearchPlanner:
    """Generates hypotheses and experiment code for iterative research."""

    def __init__(self, model_connector: Any, knowledge_memory: Any) -> None:
        self.model = model_connector
        self.knowledge = knowledge_memory

    def generate_hypothesis(self, goal: str) -> str:
        """Generate one testable hypothesis sentence from a goal."""
        prior = self._knowledge_context(goal)

        prompt = f"""
You are an AI research planner.

Goal:
{goal}

Prior research context:
{prior}

Based on prior research knowledge, generate one testable hypothesis.
Return only the hypothesis sentence.
"""

        response = self.model.generate(prompt)

        return self._clean_hypothesis(str(response))

    def propose_hypotheses(self, goal: str, context: dict[str, Any] | None = None) -> list[str]:
        """Generate multiple hypotheses for orchestration modules."""
        context = context or {}
        count = int(context.get("count", 3))
        count = max(1, min(count, 5))

        hypotheses: list[str] = []
        for _ in range(count):
            hypotheses.append(self.generate_hypothesis(goal))

        return hypotheses

    def generate_experiment(self, hypothesis: str) -> str:
        """Generate executable Python code to test a hypothesis."""
        prompt = f"""
Design a Python experiment to test the following hypothesis:

{hypothesis}

Requirements:
- Return only executable Python code.
- Include any helper functions in the same snippet.
- Print measurable results.
"""

        code = self.model.generate(prompt)

        return self._extract_code(str(code))

    def _knowledge_context(self, goal: str) -> str:
        """Fetch top prior knowledge snippets; fallback to a safe default."""
        if self.knowledge is None or not hasattr(self.knowledge, "search"):
            return "No prior knowledge available."

        try:
            hits = self.knowledge.search(goal, top_k=3)
        except (OSError, RuntimeError, TypeError, ValueError):
            return "Knowledge lookup unavailable."

        if not hits:
            return "No prior knowledge available."

        return "\n".join(f"- {item}" for item in hits)

    @staticmethod
    def _clean_hypothesis(text: str) -> str:
        """Normalize model text into a single clean hypothesis sentence."""
        cleaned = text.strip()
        cleaned = cleaned.replace("[end of text]", "").strip()
        cleaned = re.sub(r"^hypothesis\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip().strip('"').strip("'").strip()

        first_line = cleaned.splitlines()[0].strip() if cleaned else ""
        return first_line or "No hypothesis generated."

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract executable Python from mixed prose/code LLM output."""
        cleaned = text.replace("[end of text]", "").strip()

        fenced = re.search(r"```(?:python)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            return fenced.group(1).strip() + "\n"

        lines = [ln.rstrip() for ln in cleaned.splitlines()]
        code_start_tokens = (
            "import ", "from ", "def ", "class ", "if ", "for ", "while ",
            "try:", "with ", "print(", "#", "result", "data", "benchmark",
        )

        start_idx = 0
        for i, ln in enumerate(lines):
            stripped = ln.strip()
            if not stripped:
                continue
            if stripped.startswith(code_start_tokens):
                start_idx = i
                break

        code_lines = lines[start_idx:]
        code = "\n".join(code_lines).strip()

        if not code:
            return "print('No executable code generated')\n"

        return code + "\n"
