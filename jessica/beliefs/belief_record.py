"""
Phase 91: Belief Record

Represents a single belief about the world or Jessica's identity.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BeliefRecord:
    """
    Immutable belief record with grounding in memory.
    
    Attributes:
        belief_id: Unique identifier for this belief
        subject: What the belief is about (e.g., "user", "system", "world")
        predicate: The property being asserted (e.g., "name", "creator")
        value: The actual value (e.g., "Hendrik")
        confidence: Certainty level (0.0 to 1.0)
        source: Where this belief came from (e.g., "memory", "reasoning", "interaction")
        created_at: ISO timestamp when belief was created
    """
    belief_id: str
    subject: str
    predicate: str
    value: str
    confidence: float
    source: str
    created_at: str
    
    def __post_init__(self):
        """Validate belief record."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not self.subject or not self.predicate or not self.value:
            raise ValueError("Subject, predicate, and value must be non-empty")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "belief_id": self.belief_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create BeliefRecord from dictionary."""
        return BeliefRecord(
            belief_id=data["belief_id"],
            subject=data["subject"],
            predicate=data["predicate"],
            value=data["value"],
            confidence=data["confidence"],
            source=data["source"],
            created_at=data["created_at"]
        )
