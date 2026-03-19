from .capability_assessment import CapabilityAssessment
from .capability_reasoner import CapabilityReasoner
from .capability_registry import CapabilityRegistry


class CapabilityReasoningOrchestrator:

    def __init__(self, registry: CapabilityRegistry):
        self._reasoner = CapabilityReasoner(registry)

    def evaluate(self, goal: str) -> CapabilityAssessment:
        return self._reasoner.evaluate_goal(goal)
