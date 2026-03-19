from jessica.strategy.strategic_pattern_reinforcer import StrategicPatternReinforcer
from jessica.strategy.strategic_priority_stabilizer import StrategicPriorityStabilizer


def test_priority_stabilization():

    reinforcer = StrategicPatternReinforcer()
    stabilizer = StrategicPriorityStabilizer()

    weights = reinforcer.reinforce_patterns([
        "Strategic memory signal: Resource misalignment detected",
        "Strategic memory signal: Resource misalignment detected",
        "Strategic memory signal: Processing drift detected"
    ])

    priorities = stabilizer.stabilize_priorities(weights)

    assert priorities[0] == "Strategic memory signal: Resource misalignment detected"
