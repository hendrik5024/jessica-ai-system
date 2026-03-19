from jessica.jessica_presence import JessicaPresence
from jessica.execution import (
    create_reflection_record,
    SourceType,
    ConfidenceLevel,
)


def test_presence_response():
    presence = JessicaPresence()

    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_test",
        summary="Task completed successfully",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )

    response = presence.respond_from_reflection(reflection)

    assert isinstance(response, str)
    assert response.lower().startswith("i ")
