from jessica.strategy.strategic_alignment_recommender import StrategicAlignmentRecommender
from jessica.strategy.strategic_coherence_record import StrategicCoherenceRecord


def test_recommendation_generated():

    recommender = StrategicAlignmentRecommender()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Expand aggressively")
    ]

    recommendation = recommender.recommend(history)

    assert recommendation is not None
    assert "Recommendation" in recommendation


def test_no_recommendation_when_stable():

    recommender = StrategicAlignmentRecommender()

    history = [
        StrategicCoherenceRecord("c1", "Build stability"),
        StrategicCoherenceRecord("c2", "Build stability")
    ]

    assert recommender.recommend(history) is None
