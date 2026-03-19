"""
Phase 5.1.5: Intent Mediation & Cognitive Grounding

Intent objects, justification, risk assessment, and approval gates.
No action capability - perception-only preparation for future embodiment.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any
import time
import json
from datetime import datetime


class IntentType(Enum):
    """Categories of intended actions."""
    NAVIGATION = "navigation"  # Move mouse/cursor
    INTERACTION = "interaction"  # Click/type
    OBSERVATION = "observation"  # Query state
    SYSTEM = "system"  # System-level action
    COMMUNICATION = "communication"  # Send message


class IntentPriority(Enum):
    """Priority levels for intents."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class RiskLevel(Enum):
    """Risk assessment levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(Enum):
    """Human approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class IntentRiskAssessment:
    """Risk evaluation for an intent."""
    
    risk_level: RiskLevel
    potential_harms: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    reversibility_score: float = 0.0  # 0.0 (irreversible) to 1.0 (fully reversible)
    recovery_time_estimate: float = 0.0  # seconds
    confidence_score: float = 0.0  # 0.0 to 1.0 confidence in risk assessment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'risk_level': self.risk_level.value,
            'potential_harms': self.potential_harms,
            'affected_systems': self.affected_systems,
            'reversibility_score': self.reversibility_score,
            'recovery_time_estimate': self.recovery_time_estimate,
            'confidence_score': self.confidence_score,
        }


@dataclass
class IntentJustification:
    """Reasoning and justification for an intent."""
    
    primary_goal: str
    reasoning_chain: List[str] = field(default_factory=list)
    supporting_context: Dict[str, Any] = field(default_factory=dict)
    alternatives_considered: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    confidence_in_outcome: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'primary_goal': self.primary_goal,
            'reasoning_chain': self.reasoning_chain,
            'supporting_context': self.supporting_context,
            'alternatives_considered': self.alternatives_considered,
            'expected_outcome': self.expected_outcome,
            'confidence_in_outcome': self.confidence_in_outcome,
        }


@dataclass
class IntentApprovalRecord:
    """Record of human approval for an intent."""
    
    approval_status: ApprovalStatus
    approved_by: Optional[str] = None  # Human identifier
    approval_timestamp: float = field(default_factory=time.time)
    approval_notes: str = ""
    approval_duration_seconds: int = 3600  # 1 hour default expiry
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if approval is still valid."""
        if self.approval_status != ApprovalStatus.APPROVED:
            return False
        
        elapsed = time.time() - self.approval_timestamp
        if elapsed > self.approval_duration_seconds:
            self.approval_status = ApprovalStatus.EXPIRED
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'approval_status': self.approval_status.value,
            'approved_by': self.approved_by,
            'approval_timestamp': self.approval_timestamp,
            'approval_notes': self.approval_notes,
            'approval_duration_seconds': self.approval_duration_seconds,
            'metadata': self.metadata,
            'is_valid': self.is_valid(),
        }


@dataclass
class Intent:
    """Explicit intent object for planned action."""
    
    intent_id: str
    intent_type: IntentType
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: IntentPriority = IntentPriority.MEDIUM
    
    # Grounding and reasoning
    justification: Optional[IntentJustification] = None
    risk_assessment: Optional[IntentRiskAssessment] = None
    
    # Approval requirement
    requires_approval: bool = True
    approval_record: Optional[IntentApprovalRecord] = None
    
    # Timestamps
    created_timestamp: float = field(default_factory=time.time)
    execution_deadline: Optional[float] = None
    
    # Status tracking
    status: str = "created"  # created, approved, rejected, simulated, executed, expired
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_approved(self) -> bool:
        """Check if intent has valid approval."""
        if not self.requires_approval:
            return True
        
        if self.approval_record is None:
            return False
        
        return self.approval_record.is_valid()
    
    def is_expired(self) -> bool:
        """Check if intent has exceeded deadline."""
        if self.execution_deadline is None:
            return False
        
        return time.time() > self.execution_deadline
    
    def can_be_executed(self) -> bool:
        """Check if intent can be executed."""
        return self.is_approved() and not self.is_expired()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'intent_id': self.intent_id,
            'intent_type': self.intent_type.value,
            'action_name': self.action_name,
            'parameters': self.parameters,
            'priority': self.priority.name,
            'justification': self.justification.to_dict() if self.justification else None,
            'risk_assessment': self.risk_assessment.to_dict() if self.risk_assessment else None,
            'requires_approval': self.requires_approval,
            'approval_record': self.approval_record.to_dict() if self.approval_record else None,
            'created_timestamp': self.created_timestamp,
            'execution_deadline': self.execution_deadline,
            'status': self.status,
            'metadata': self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class IntentMediator:
    """Orchestrates intent planning, assessment, and approval."""
    
    def __init__(self):
        """Initialize intent mediator."""
        self._intents: Dict[str, Intent] = {}
        self._intent_counter = 0
        self._approval_log: List[Dict[str, Any]] = []
        self._is_enabled = True
    
    def create_intent(
        self,
        action_name: str,
        intent_type: IntentType,
        parameters: Optional[Dict[str, Any]] = None,
        priority: IntentPriority = IntentPriority.MEDIUM,
        requires_approval: bool = True,
        execution_deadline: Optional[float] = None,
    ) -> Intent:
        """Create a new intent object."""
        if not self._is_enabled:
            return None
        
        intent_id = f"intent_{self._intent_counter:06d}"
        self._intent_counter += 1
        
        intent = Intent(
            intent_id=intent_id,
            intent_type=intent_type,
            action_name=action_name,
            parameters=parameters or {},
            priority=priority,
            requires_approval=requires_approval,
            execution_deadline=execution_deadline or (time.time() + 3600),
        )
        
        self._intents[intent_id] = intent
        return intent
    
    def add_justification(
        self,
        intent: Intent,
        primary_goal: str,
        reasoning_chain: List[str],
        expected_outcome: str,
        confidence: float = 0.8,
    ) -> Intent:
        """Add justification to an intent."""
        if not self._is_enabled:
            return intent
        
        intent.justification = IntentJustification(
            primary_goal=primary_goal,
            reasoning_chain=reasoning_chain,
            expected_outcome=expected_outcome,
            confidence_in_outcome=confidence,
        )
        
        return intent
    
    def add_risk_assessment(
        self,
        intent: Intent,
        risk_level: RiskLevel,
        potential_harms: Optional[List[str]] = None,
        affected_systems: Optional[List[str]] = None,
        reversibility_score: float = 1.0,
        recovery_time: float = 0.0,
    ) -> Intent:
        """Add risk assessment to an intent."""
        if not self._is_enabled:
            return intent
        
        intent.risk_assessment = IntentRiskAssessment(
            risk_level=risk_level,
            potential_harms=potential_harms or [],
            affected_systems=affected_systems or [],
            reversibility_score=reversibility_score,
            recovery_time_estimate=recovery_time,
            confidence_score=0.85,
        )
        
        return intent
    
    def submit_for_approval(
        self,
        intent: Intent,
        approval_notes: str = "",
    ) -> IntentApprovalRecord:
        """Submit intent for human approval."""
        if not self._is_enabled:
            return None
        
        approval_record = IntentApprovalRecord(
            approval_status=ApprovalStatus.PENDING,
            approval_notes=approval_notes,
        )
        
        intent.approval_record = approval_record
        intent.status = "submitted_for_approval"
        
        return approval_record
    
    def approve_intent(
        self,
        intent: Intent,
        approved_by: str,
        notes: str = "",
        duration_seconds: int = 3600,
    ) -> bool:
        """Approve an intent (simulated human approval)."""
        if not self._is_enabled:
            return False
        
        if intent.approval_record is None:
            intent.approval_record = IntentApprovalRecord(
                approval_status=ApprovalStatus.APPROVED,
                approved_by=approved_by,
                approval_notes=notes,
                approval_duration_seconds=duration_seconds,
            )
        else:
            intent.approval_record.approval_status = ApprovalStatus.APPROVED
            intent.approval_record.approved_by = approved_by
            intent.approval_record.approval_notes = notes
            intent.approval_record.approval_duration_seconds = duration_seconds
        
        intent.status = "approved"
        
        self._approval_log.append({
            'intent_id': intent.intent_id,
            'approved_by': approved_by,
            'timestamp': time.time(),
            'notes': notes,
        })
        
        return True
    
    def reject_intent(
        self,
        intent: Intent,
        rejected_by: str,
        reason: str = "",
    ) -> bool:
        """Reject an intent."""
        if not self._is_enabled:
            return False
        
        if intent.approval_record is None:
            intent.approval_record = IntentApprovalRecord(
                approval_status=ApprovalStatus.REJECTED,
                approved_by=rejected_by,
                approval_notes=reason,
            )
        else:
            intent.approval_record.approval_status = ApprovalStatus.REJECTED
            intent.approval_record.approved_by = rejected_by
            intent.approval_record.approval_notes = reason
        
        intent.status = "rejected"
        
        return True
    
    def get_intent(self, intent_id: str) -> Optional[Intent]:
        """Retrieve an intent by ID."""
        return self._intents.get(intent_id)
    
    def list_intents(
        self,
        status: Optional[str] = None,
        intent_type: Optional[IntentType] = None,
    ) -> List[Intent]:
        """List intents, optionally filtered."""
        intents = list(self._intents.values())
        
        if status:
            intents = [i for i in intents if i.status == status]
        
        if intent_type:
            intents = [i for i in intents if i.intent_type == intent_type]
        
        return intents
    
    def get_approval_log(self) -> List[Dict[str, Any]]:
        """Get approval audit trail."""
        return self._approval_log.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get mediator status."""
        return {
            'enabled': self._is_enabled,
            'total_intents': len(self._intents),
            'approval_log_size': len(self._approval_log),
            'pending_approvals': len(self.list_intents(status="submitted_for_approval")),
            'approved_intents': len(self.list_intents(status="approved")),
        }
    
    def enable(self) -> None:
        """Enable intent mediation."""
        self._is_enabled = True
    
    def disable(self) -> None:
        """Disable intent mediation (reversible)."""
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if mediation is enabled."""
        return self._is_enabled


if __name__ == "__main__":
    # Demo
    mediator = IntentMediator()
    
    # Create intent
    intent = mediator.create_intent(
        action_name="click_button",
        intent_type=IntentType.INTERACTION,
        parameters={"button_id": "submit", "x": 100, "y": 50},
        priority=IntentPriority.HIGH,
    )
    
    print(f"Created: {intent.intent_id}")
    print(f"Status: {intent.status}")
    print(f"Requires approval: {intent.requires_approval}")
    
    # Add justification
    mediator.add_justification(
        intent,
        primary_goal="Submit form data",
        reasoning_chain=[
            "User entered all required fields",
            "Form validation passed",
            "Ready to submit",
        ],
        expected_outcome="Form submitted successfully",
        confidence=0.95,
    )
    
    # Add risk assessment
    mediator.add_risk_assessment(
        intent,
        risk_level=RiskLevel.LOW,
        potential_harms=["Network error"],
        affected_systems=["backend_api"],
        reversibility_score=0.8,
    )
    
    # Submit for approval
    mediator.submit_for_approval(intent, "Auto-submitted for review")
    
    # Approve
    mediator.approve_intent(intent, "human_reviewer", "Approved after review")
    
    print(f"\nAfter approval:")
    print(f"Status: {intent.status}")
    print(f"Can execute: {intent.can_be_executed()}")
    print(f"\nIntent JSON:\n{intent.to_json()}")
