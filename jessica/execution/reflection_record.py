"""
Phase 7.3: Reflective Intelligence Layer — Reflection Record

This module defines the immutable ReflectionRecord structure for Phase 7.3.

ReflectionRecords are strictly read-only, advisory-only outputs that reflect on
completed executions and proposals. They do NOT influence decisions, trigger
actions, or modify system behavior.

CRITICAL CONSTRAINTS:
- Immutable (frozen dataclass)
- Advisory-only (human-consumable)
- No execution capability
- No proposal generation
- No learning or memory mutation
- No feedback loops
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class SourceType(Enum):
    """Type of source being reflected upon."""
    PROPOSAL = "proposal"
    EXECUTION = "execution"


class ConfidenceLevel(Enum):
    """Confidence level of reflection analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ReflectionRecord:
    """
    Immutable record of a reflection on a completed action or proposal.
    
    This is a read-only, advisory-only record that exists solely for:
    - Human understanding
    - Debugging
    - System transparency
    
    It does NOT:
    - Influence decisions
    - Trigger actions
    - Modify behavior
    - Learn or adapt
    
    All fields are immutable after creation.
    
    Fields:
        reflection_id: Unique identifier for this reflection (UUID)
        source_type: Type of source (PROPOSAL or EXECUTION)
        source_id: ID of the proposal or execution being reflected upon
        summary: Human-readable summary of what happened
        identified_risks: List of risks identified (empty if none)
        anomalies: List of anomalies detected (empty if none)
        confidence_level: Confidence in this reflection (LOW/MEDIUM/HIGH)
        created_at: When this reflection was created
        notes: Optional additional human-readable notes
    
    Example:
        >>> record = ReflectionRecord(
        ...     reflection_id="refl_123",
        ...     source_type=SourceType.EXECUTION,
        ...     source_id="exec_456",
        ...     summary="Email sent successfully to user@example.com",
        ...     identified_risks=["No email validation performed"],
        ...     anomalies=[],
        ...     confidence_level=ConfidenceLevel.HIGH,
        ...     created_at=datetime.now(),
        ...     notes="Consider adding email validation in future",
        ... )
        >>> record.summary
        'Email sent successfully to user@example.com'
        >>> record.identified_risks
        ['No email validation performed']
        
        # Immutability enforced
        >>> record.summary = "New summary"  # Raises FrozenInstanceError
    """
    
    reflection_id: str              # Unique identifier (UUID string)
    source_type: SourceType         # PROPOSAL or EXECUTION
    source_id: str                  # ID of source being reflected upon
    summary: str                    # Human-readable summary
    identified_risks: List[str]     # Risks identified (empty list if none)
    anomalies: List[str]            # Anomalies detected (empty list if none)
    confidence_level: ConfidenceLevel  # Confidence in reflection
    created_at: datetime            # Creation timestamp
    notes: Optional[str] = None     # Optional additional notes
    
    def to_dict(self) -> dict:
        """
        Convert reflection record to dictionary (read-only).
        
        Returns:
            Dictionary representation of this reflection
        """
        return {
            "reflection_id": self.reflection_id,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "summary": self.summary,
            "identified_risks": list(self.identified_risks),  # Copy
            "anomalies": list(self.anomalies),  # Copy
            "confidence_level": self.confidence_level.value,
            "created_at": self.created_at.isoformat(),
            "notes": self.notes,
        }
    
    def has_risks(self) -> bool:
        """Check if any risks were identified."""
        return len(self.identified_risks) > 0
    
    def has_anomalies(self) -> bool:
        """Check if any anomalies were detected."""
        return len(self.anomalies) > 0
    
    def risk_count(self) -> int:
        """Count of identified risks."""
        return len(self.identified_risks)
    
    def anomaly_count(self) -> int:
        """Count of detected anomalies."""
        return len(self.anomalies)


def create_reflection_record(
    source_type: SourceType,
    source_id: str,
    summary: str,
    identified_risks: Optional[List[str]] = None,
    anomalies: Optional[List[str]] = None,
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM,
    notes: Optional[str] = None,
) -> ReflectionRecord:
    """
    Factory function to create a ReflectionRecord with validation.
    
    This is the recommended way to create ReflectionRecords, as it validates
    inputs and generates a unique reflection_id.
    
    Args:
        source_type: Type of source (PROPOSAL or EXECUTION)
        source_id: ID of source being reflected upon (must not be empty)
        summary: Human-readable summary (must not be empty)
        identified_risks: List of risks (defaults to empty list)
        anomalies: List of anomalies (defaults to empty list)
        confidence_level: Confidence level (defaults to MEDIUM)
        notes: Optional additional notes
    
    Returns:
        Immutable ReflectionRecord
    
    Raises:
        ValueError: If validation fails
    
    Example:
        >>> record = create_reflection_record(
        ...     source_type=SourceType.EXECUTION,
        ...     source_id="exec_123",
        ...     summary="Action completed successfully",
        ... )
        >>> record.reflection_id  # Auto-generated UUID
        'refl_a1b2c3...'
    """
    # Validation
    if not source_id or not source_id.strip():
        raise ValueError("source_id cannot be empty")
    
    if not summary or not summary.strip():
        raise ValueError("summary cannot be empty")
    
    # Generate unique reflection ID
    reflection_id = f"refl_{uuid.uuid4().hex[:12]}"
    
    # Default empty lists
    if identified_risks is None:
        identified_risks = []
    if anomalies is None:
        anomalies = []
    
    # Create immutable record
    return ReflectionRecord(
        reflection_id=reflection_id,
        source_type=source_type,
        source_id=source_id,
        summary=summary,
        identified_risks=identified_risks,
        anomalies=anomalies,
        confidence_level=confidence_level,
        created_at=datetime.now(),
        notes=notes,
    )
