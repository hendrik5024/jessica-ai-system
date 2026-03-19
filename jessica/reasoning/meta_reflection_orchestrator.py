from .meta_reflection_engine import MetaReflectionEngine
from .meta_reflection_record import MetaReflectionRecord


class MetaReflectionOrchestrator:

    def __init__(self):
        self.engine = MetaReflectionEngine()

    def reflect(
        self,
        reflection_id: str,
        reasoning_id: str,
        reasoning_paths: int,
        integrity_passed: bool,
        stability_passed: bool,
        confidence_score: float,
    ) -> MetaReflectionRecord:

        return self.engine.evaluate(
            reflection_id,
            reasoning_id,
            reasoning_paths,
            integrity_passed,
            stability_passed,
            confidence_score,
        )
