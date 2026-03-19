from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class IntrospectionRecord:
    input_text: str
    intent: Optional[str]
    decision: Optional[str]
    response: str
    reasoning: str
    created_at: datetime
