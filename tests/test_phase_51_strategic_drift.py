from jessica.strategy.strategic_drift_detector import StrategicDriftDetector
from jessica.strategy.strategic_coherence_record import StrategicCoherenceRecord


def test_drift_detected():

    detector = StrategicDriftDetector()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Expand aggressively")
    ]

    assert detector.detect(history) is True


def test_no_drift():

    detector = StrategicDriftDetector()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Build stability")
    ]

    assert detector.detect(history) is False
