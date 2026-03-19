from __future__ import annotations

from jessica.meta.uncertainty_tokens import UncertaintyEngine


def test_disclosure_when_low_confidence():
    engine = UncertaintyEngine(disclose_threshold=0.8)
    report = engine.analyze(
        response_text="This might work, but I'm not sure about edge cases.",
        user_text="Should we deploy this?",
        confidence=0.62,
        allow_exploration=True,
    )

    assert report.should_disclose is True
    assert "I don't know" in report.disclosure
    assert report.known_unknowns


def test_no_disclosure_when_confident():
    engine = UncertaintyEngine(disclose_threshold=0.6)
    report = engine.analyze(
        response_text="Proceed with the refactor; it's safe.",
        user_text="Okay?",
        confidence=0.9,
        allow_exploration=True,
    )

    assert report.should_disclose is False
    assert report.disclosure == ""


def test_assumptions_extracted():
    engine = UncertaintyEngine()
    report = engine.analyze(
        response_text="Assuming the environment stays stable, this will hold.",
        user_text="What happens next?",
        confidence=0.7,
        allow_exploration=False,
    )

    assert report.assumptions
