from jessica.strategy.strategic_memory_consolidator import StrategicMemoryConsolidator


def test_memory_consolidation():

    consolidator = StrategicMemoryConsolidator()

    signals = consolidator.consolidate_patterns(
        ["Resource misalignment detected"]
    )

    assert len(signals) == 1
