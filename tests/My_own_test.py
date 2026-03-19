import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from jessica.execution import (
    create_reflection_record,
    SourceType,
    ConfidenceLevel,
)
from jessica.chat_interface import chat_from_reflection

reflection = create_reflection_record(
    source_type=SourceType.EXECUTION,
    source_id="demo_001",
    summary="Email sent successfully",
    identified_risks=["Recipient address was not validated"],
    anomalies=[],
    confidence_level=ConfidenceLevel.HIGH,
    notes="Add validation before sending",
)

response = chat_from_reflection(reflection)
print(response)
