from jessica.strategy.strategic_drift_explainer import StrategicDriftExplainer
from jessica.strategy.strategic_coherence_record import StrategicCoherenceRecord


def test_explains_drift():

    explainer = StrategicDriftExplainer()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Expand aggressively")
    ]

    explanation = explainer.explain(history)

    assert explanation is not None
    assert "Strategic drift detected" in explanation


def test_no_explanation_when_stable():

    explainer = StrategicDriftExplainer()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Build stability")
    ]

    assert explainer.explain(history) is None
