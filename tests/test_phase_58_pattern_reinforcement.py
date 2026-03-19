from jessica.strategy.strategic_pattern_reinforcer import StrategicPatternReinforcer


def test_pattern_reinforcement():

    reinforcer = StrategicPatternReinforcer()

    weights = reinforcer.reinforce_patterns(
        ["Strategic memory signal: Resource misalignment detected"]
    )

    assert weights != {}
