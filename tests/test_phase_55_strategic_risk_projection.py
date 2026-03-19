from jessica.strategy.strategic_risk_projection_engine import StrategicRiskProjectionEngine


def test_high_risk():

    engine = StrategicRiskProjectionEngine()

    msg = engine.project_risk(0.8)

    assert msg is not None


def test_low_risk():

    engine = StrategicRiskProjectionEngine()

    msg = engine.project_risk(0.1)

    assert msg is None
