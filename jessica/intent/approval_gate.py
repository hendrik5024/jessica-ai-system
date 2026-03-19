"""
Phase 5.1.5: Human Approval Gate

Human approval workflows and decision tracking.
Ensures human-in-the-loop for all future actions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import time
import json
from datetime import datetime


class ApprovalMethod(Enum):
    """Methods for human approval."""
    AUTOMATIC = "automatic"  # Auto-approved (low risk)
    REVIEW = "review"  # Manual review required
    CONFIRMATION = "confirmation"  # User confirmation
    ESCALATION = "escalation"  # Escalated to supervisor


class ApprovalDecision(Enum):
    """Human decision on approval."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    ESCALATED = "escalated"


@dataclass
class ApprovalCriteria:
    """Decision criteria for approval."""
    
    min_success_probability: float = 0.7
    max_risk_level: str = "moderate"  # minimal, low, moderate, high, critical
    require_simulation: bool = True
    require_justification: bool = True
    require_ui_inspection: bool = True
    auto_approve_minimal_risk: bool = True


@dataclass
class ApprovalDecisionRecord:
    """Record of approval decision."""
    
    decision_id: str
    decision: ApprovalDecision
    intent_id: str
    
    # Who decided
    decided_by: str = "system"  # System or human identifier
    decision_method: ApprovalMethod = ApprovalMethod.AUTOMATIC
    
    # Timing
    decision_timestamp: float = field(default_factory=time.time)
    reasoning: str = ""
    
    # Decision metadata
    criteria_met: Dict[str, bool] = field(default_factory=dict)
    review_notes: str = ""
    alternative_suggestions: List[str] = field(default_factory=list)
    
    # Audit trail
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'decision_id': self.decision_id,
            'decision': self.decision.value,
            'intent_id': self.intent_id,
            'decided_by': self.decided_by,
            'decision_method': self.decision_method.value,
            'decision_timestamp': self.decision_timestamp,
            'reasoning': self.reasoning,
            'criteria_met': self.criteria_met,
            'review_notes': self.review_notes,
            'alternative_suggestions': self.alternative_suggestions,
            'metadata': self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ApprovalGate:
    """Human approval gate for intents."""
    
    def __init__(self):
        """Initialize approval gate."""
        self._decision_records: Dict[str, ApprovalDecisionRecord] = {}
        self._decision_counter = 0
        self._approval_criteria = ApprovalCriteria()
        self._is_enabled = True
        self._approval_callbacks: List[Callable] = []
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}
    
    def set_approval_criteria(self, criteria: ApprovalCriteria) -> None:
        """Set approval criteria."""
        self._approval_criteria = criteria
    
    def register_approval_callback(self, callback: Callable) -> None:
        """Register callback for approval decisions."""
        self._approval_callbacks.append(callback)
    
    def _notify_callbacks(self, decision_record: ApprovalDecisionRecord) -> None:
        """Notify all registered callbacks."""
        for callback in self._approval_callbacks:
            try:
                callback(decision_record)
            except:
                pass
    
    def evaluate_for_approval(
        self,
        intent: Any,  # Intent object
        simulation_result: Optional[Any] = None,  # SimulationResult
    ) -> ApprovalMethod:
        """Evaluate if intent requires human approval."""
        if not self._is_enabled:
            return ApprovalMethod.AUTOMATIC
        
        # Extract risk level from intent
        risk_level = "low"
        if intent.risk_assessment:
            risk_level = intent.risk_assessment.risk_level.value
        
        # Extract success probability from simulation
        success_prob = 0.9
        if simulation_result and simulation_result.predicted_outcome:
            success_prob = simulation_result.predicted_outcome.success_probability
        
        # Determine approval method
        if risk_level == "minimal" and self._approval_criteria.auto_approve_minimal_risk:
            return ApprovalMethod.AUTOMATIC
        
        if risk_level in ["critical", "high"]:
            return ApprovalMethod.ESCALATION
        
        if success_prob < self._approval_criteria.min_success_probability:
            return ApprovalMethod.REVIEW
        
        return ApprovalMethod.CONFIRMATION
    
    def request_approval(
        self,
        intent: Any,
        approval_method: ApprovalMethod,
        simulation_result: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request human approval for an intent."""
        if not self._is_enabled:
            return {}
        
        approval_id = f"approval_{self._decision_counter:06d}"
        self._decision_counter += 1
        
        approval_request = {
            'approval_id': approval_id,
            'intent_id': intent.intent_id,
            'action_name': intent.action_name,
            'approval_method': approval_method.value,
            'timestamp': time.time(),
            'requires_response': approval_method != ApprovalMethod.AUTOMATIC,
            'intent_data': intent.to_dict(),
            'simulation_data': simulation_result.to_dict() if simulation_result else None,
            'metadata': metadata or {},
        }
        
        self._pending_approvals[approval_id] = approval_request
        return approval_request
    
    def approve(
        self,
        approval_id: str,
        approved_by: str,
        reasoning: str = "",
        notes: str = "",
    ) -> ApprovalDecisionRecord:
        """Approve an intent."""
        if not self._is_enabled:
            return None
        
        if approval_id not in self._pending_approvals:
            return None
        
        approval_request = self._pending_approvals[approval_id]
        
        decision = ApprovalDecisionRecord(
            decision_id=approval_id,
            decision=ApprovalDecision.APPROVED,
            intent_id=approval_request['intent_id'],
            decided_by=approved_by,
            decision_method=ApprovalMethod(approval_request['approval_method']),
            reasoning=reasoning,
            review_notes=notes,
        )
        
        self._decision_records[approval_id] = decision
        del self._pending_approvals[approval_id]
        
        self._notify_callbacks(decision)
        return decision
    
    def reject(
        self,
        approval_id: str,
        rejected_by: str,
        reason: str = "",
        suggestions: Optional[List[str]] = None,
    ) -> ApprovalDecisionRecord:
        """Reject an intent."""
        if not self._is_enabled:
            return None
        
        if approval_id not in self._pending_approvals:
            return None
        
        approval_request = self._pending_approvals[approval_id]
        
        decision = ApprovalDecisionRecord(
            decision_id=approval_id,
            decision=ApprovalDecision.REJECTED,
            intent_id=approval_request['intent_id'],
            decided_by=rejected_by,
            decision_method=ApprovalMethod(approval_request['approval_method']),
            reasoning=reason,
            alternative_suggestions=suggestions or [],
        )
        
        self._decision_records[approval_id] = decision
        del self._pending_approvals[approval_id]
        
        self._notify_callbacks(decision)
        return decision
    
    def conditionally_approve(
        self,
        approval_id: str,
        approved_by: str,
        conditions: List[str],
        notes: str = "",
    ) -> ApprovalDecisionRecord:
        """Conditionally approve an intent."""
        if not self._is_enabled:
            return None
        
        if approval_id not in self._pending_approvals:
            return None
        
        approval_request = self._pending_approvals[approval_id]
        
        decision = ApprovalDecisionRecord(
            decision_id=approval_id,
            decision=ApprovalDecision.CONDITIONAL,
            intent_id=approval_request['intent_id'],
            decided_by=approved_by,
            decision_method=ApprovalMethod(approval_request['approval_method']),
            reasoning=f"Approved with conditions: {', '.join(conditions)}",
            review_notes=notes,
            metadata={'conditions': conditions},
        )
        
        self._decision_records[approval_id] = decision
        del self._pending_approvals[approval_id]
        
        self._notify_callbacks(decision)
        return decision
    
    def escalate(
        self,
        approval_id: str,
        escalated_by: str,
        reason: str = "",
    ) -> ApprovalDecisionRecord:
        """Escalate an approval to supervisor."""
        if not self._is_enabled:
            return None
        
        if approval_id not in self._pending_approvals:
            return None
        
        approval_request = self._pending_approvals[approval_id]
        
        decision = ApprovalDecisionRecord(
            decision_id=approval_id,
            decision=ApprovalDecision.ESCALATED,
            intent_id=approval_request['intent_id'],
            decided_by=escalated_by,
            decision_method=ApprovalMethod.ESCALATION,
            reasoning=reason,
        )
        
        # Keep in pending but mark as escalated
        self._decision_records[approval_id] = decision
        
        self._notify_callbacks(decision)
        return decision
    
    def get_decision(self, approval_id: str) -> Optional[ApprovalDecisionRecord]:
        """Retrieve a decision record."""
        return self._decision_records.get(approval_id)
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approvals."""
        return list(self._pending_approvals.values())
    
    def list_decisions(
        self,
        intent_id: Optional[str] = None,
        decision: Optional[ApprovalDecision] = None,
    ) -> List[ApprovalDecisionRecord]:
        """List decision records."""
        records = list(self._decision_records.values())
        
        if intent_id:
            records = [r for r in records if r.intent_id == intent_id]
        
        if decision:
            records = [r for r in records if r.decision == decision]
        
        return records
    
    def get_status(self) -> Dict[str, Any]:
        """Get approval gate status."""
        return {
            'enabled': self._is_enabled,
            'pending_approvals': len(self._pending_approvals),
            'total_decisions': len(self._decision_records),
            'approved': len(self.list_decisions(decision=ApprovalDecision.APPROVED)),
            'rejected': len(self.list_decisions(decision=ApprovalDecision.REJECTED)),
        }
    
    def enable(self) -> None:
        """Enable approval gate."""
        self._is_enabled = True
    
    def disable(self) -> None:
        """Disable approval gate (reversible)."""
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self._is_enabled


if __name__ == "__main__":
    # Demo
    gate = ApprovalGate()
    
    # Set criteria
    criteria = ApprovalCriteria(
        min_success_probability=0.8,
        auto_approve_minimal_risk=True,
    )
    gate.set_approval_criteria(criteria)
    
    print(f"Approval gate enabled: {gate.is_enabled()}")
    print(f"Status: {gate.get_status()}")
    print(f"\nApproval gate ready for use")
