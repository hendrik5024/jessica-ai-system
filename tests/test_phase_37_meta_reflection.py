from jessica.reasoning.meta_reflection_orchestrator import MetaReflectionOrchestrator


def test_meta_reflection_basic():

    orch = MetaReflectionOrchestrator()

    rec = orch.reflect("m1", "r1", 3, True, True, 0.9)

    assert rec.reasoning_quality > 0.8
    assert rec.uncertainty_level < 0.2


def test_meta_reflection_penalty():

    orch = MetaReflectionOrchestrator()

    rec = orch.reflect("m2", "r2", 2, False, True, 0.9)

    assert rec.reasoning_quality < 0.9
