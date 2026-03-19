from jessica.stability.self_repair_advisor import SelfRepairAdvisor


def test_self_repair_advisor_outputs_recommendations():
    advisor = SelfRepairAdvisor()

    signals = [
        {"issue": "reasoning_drift", "severity": 0.7}
    ]

    recs = advisor.generate_recommendations(signals)

    assert len(recs) == 1
    assert recs[0].expected_stability_gain > 0
