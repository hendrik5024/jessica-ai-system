"""
Phase 84.5 — Reasoning Orchestrator

Coordinates facts + inference.
"""

from .concept_registry import ConceptRegistry
from .inference_engine import InferenceEngine


class ReasoningOrchestrator:

    def __init__(self):
        self.registry = ConceptRegistry()
        self.engine = InferenceEngine()

    def add_fact(self, subject: str, relation: str, obj: str):
        self.registry.add_fact(subject, relation, obj)

    def infer_all(self):
        facts = self.registry.get_facts()
        inferred = self.engine.infer(facts)

        for f in inferred:
            self.registry.add_fact(f.subject, f.relation, f.object)

    def query_creator(self, obj: str):
        results = self.registry.find(relation="is_creator_of", obj=obj)
        if results:
            return results[0].subject
        return None
