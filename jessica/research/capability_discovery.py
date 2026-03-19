from typing import Any
import re


class CapabilityDiscovery:
    """Detects whether a task needs a missing capability/tool."""

    def __init__(self, registry: Any, model_connector: Any) -> None:
        self.registry = registry
        self.model = model_connector

    def detect_missing_capability(self, task: str) -> str | None:

        agents = self.registry.list_agents()

        prompt = f"""
You are an AI system that determines if a new tool/agent is needed.

Task:
{task}

Existing agents:
{agents}

If an existing agent can solve the task return:
NONE

If not, return the missing capability name.
Return only the capability.
"""

        response = self.model.generate(prompt)
        capability = self._normalize_response(str(response))

        if capability.upper() == "NONE":
            return None

        return capability

    @staticmethod
    def _normalize_response(text: str) -> str:
        cleaned = text.strip().replace("[end of text]", "").strip()
        cleaned = cleaned.replace("```", "").strip()

        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if not lines:
            return "NONE"

        cleaned = lines[0]

        # If first line is a label (e.g., "Solution:"), try the second line.
        if cleaned.lower().rstrip(":") in {"solution", "answer", "task", "capability", "missing capability"}:
            if len(lines) > 1:
                cleaned = lines[1]

        # Accept prefixed forms like "Capability: heatmap visualization".
        prefixed = re.match(r"^(capability|missing capability)\s*:\s*(.+)$", cleaned, flags=re.IGNORECASE)
        if prefixed:
            cleaned = prefixed.group(2).strip()

        cleaned = cleaned.strip().strip('"').strip("'").strip()
        cleaned = cleaned.rstrip(".:").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)

        if not cleaned:
            return "NONE"

        lowered = cleaned.lower()
        if lowered in {"none", "n/a", "no", "no capability", "existing agent"}:
            return "NONE"

        # Reject generic answer wrappers that are not capabilities.
        blocked_prefixes = (
            "answer", "solution", "task", "goal", "hypothesis", "analysis", "response", "here",
        )
        if lowered.startswith(blocked_prefixes):
            return "NONE"

        # Capability names should be short and noun-like.
        if len(cleaned) > 48:
            return "NONE"

        words = cleaned.split()
        if len(words) > 5:
            return "NONE"

        if not all(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", w) for w in words):
            return "NONE"

        return lowered
