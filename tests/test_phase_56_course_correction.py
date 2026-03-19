from jessica.strategy.strategic_course_correction_advisor import StrategicCourseCorrectionAdvisor


def test_high_risk_adjustment():

    advisor = StrategicCourseCorrectionAdvisor()

    msg = advisor.recommend_adjustment(
        "High long-term strategic risk if trajectory continues."
    )

    assert msg is not None


def test_no_risk():

    advisor = StrategicCourseCorrectionAdvisor()

    msg = advisor.recommend_adjustment(None)

    assert msg is None
