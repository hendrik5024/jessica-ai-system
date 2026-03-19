from jessica.strategy.strategic_direction_persistence import StrategicDirectionPersistence


def test_direction_persistence():

    persistence = StrategicDirectionPersistence()

    priorities = [
        "Strategic memory signal: Resource misalignment detected",
        "Strategic memory signal: Processing drift detected"
    ]

    persistence.persist_priorities(priorities)

    stored = persistence.get_last_priorities()

    assert stored == priorities
