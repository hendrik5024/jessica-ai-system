"""Phase 8.1: Chat Interface - Test Suite

Tests the stateless chat_from_reflection interface.
"""

from jessica.execution import (
    create_reflection_record,
    SourceType,
    ConfidenceLevel,
)
from jessica.chat_interface import chat_from_reflection


def test_chat_from_reflection_basic():
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_1",
        summary="Email sent successfully",
        identified_risks=["Recipient address was not validated"],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
        notes="Add validation before sending",
    )

    response = chat_from_reflection(reflection)

    assert isinstance(response, str)
    assert len(response) > 0
    assert "i " in response.lower() or "i'm" in response.lower()


def test_chat_from_reflection_deterministic():
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_2",
        summary="Report generated",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.MEDIUM,
    )

    response1 = chat_from_reflection(reflection)
    response2 = chat_from_reflection(reflection)

    assert response1 == response2


def test_chat_from_reflection_no_internal_leakage():
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_3",
        summary="Settings updated",
        identified_risks=["Missing approval"],
        anomalies=[],
        confidence_level=ConfidenceLevel.MEDIUM,
    )

    response = chat_from_reflection(reflection)

    forbidden_terms = [
        "Phase",
        "ReflectionRecord",
        "execution_id",
        "proposal_id",
        "source_id",
        "reflection_id",
        "dataclass",
        "module",
        "orchestrator",
        "SourceType",
        "ConfidenceLevel",
        "jessica.execution",
    ]

    for term in forbidden_terms:
        assert term not in response


def test_chat_from_reflection_read_only():
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_4",
        summary="File scanned",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.LOW,
    )

    original_summary = reflection.summary
    _ = chat_from_reflection(reflection)

    assert reflection.summary == original_summary
