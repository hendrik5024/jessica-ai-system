from jessica.strategy.multi_horizon_consistency_engine import MultiHorizonConsistencyEngine


def test_detects_inconsistency():

    engine = MultiHorizonConsistencyEngine()

    warning = engine.evaluate(
        short_term="increase marketing spend",
        mid_term="cost reduction strategy",
        long_term="profit stability"
    )

    assert warning is not None


def test_no_warning_when_consistent():

    engine = MultiHorizonConsistencyEngine()

    warning = engine.evaluate(
        short_term="expand regional presence",
        mid_term="expand regional presence and partnerships",
        long_term="expand regional presence and partnerships globally"
    )

    assert warning is None
