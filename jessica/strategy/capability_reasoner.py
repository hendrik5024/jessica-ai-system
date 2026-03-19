from typing import List

from .capability_assessment import CapabilityAssessment
from .capability_descriptor import CapabilityDescriptor
from .capability_registry import CapabilityRegistry


class CapabilityReasoner:

    def __init__(self, registry: CapabilityRegistry):
        self._registry = registry

    def evaluate_goal(self, goal_description: str) -> CapabilityAssessment:
        required_names = self._extract_required_names(goal_description)
        matched = self.match_required_capabilities(goal_description)
        missing = self.detect_missing_capabilities(goal_description)
        achievable = len(missing) == 0

        summary = (
            "All required capabilities available."
            if achievable
            else "Missing required capabilities."
        )

        return CapabilityAssessment(
            goal=goal_description,
            achievable=achievable,
            required_capabilities=tuple(required_names),
            missing_capabilities=tuple(missing),
            reasoning_summary=summary,
        )

    def match_required_capabilities(self, goal_description: str) -> List[CapabilityDescriptor]:
        required_names = self._extract_required_names(goal_description)
        matched: List[CapabilityDescriptor] = []

        for name in required_names:
            descriptor = self._find_by_name(name)
            if descriptor:
                matched.append(descriptor)

        return matched

    def detect_missing_capabilities(self, goal_description: str) -> List[str]:
        required_names = self._extract_required_names(goal_description)
        missing: List[str] = []

        for name in required_names:
            if self._find_by_name(name) is None:
                missing.append(name)

        return missing

    def _find_by_name(self, name: str):
        for descriptor in self._registry.list_capabilities():
            if descriptor.name == name:
                return descriptor
        return None

    def _extract_required_names(self, goal_description: str) -> List[str]:
        lower = goal_description.lower()
        if "needs:" not in lower:
            return []

        _, tail = goal_description.split("needs:", 1)
        parts = [part.strip() for part in tail.split(",")]
        return [part for part in parts if part]
