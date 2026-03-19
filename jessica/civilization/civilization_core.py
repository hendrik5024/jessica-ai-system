"""Core structures for Jessica's internal civilization

Classes:
- Mind: Base class for all specialized minds
- Viewpoint: A mind's position on a decision
- Objection: Formal disagreement with rationale
- CouncilSession: Decision-making session with debate
- InstitutionalMemory: Persistent history of civilization decisions
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class ObjectionSeverity(Enum):
    """Severity levels for objections."""
    WEAK = "weak"  # Minor concern, negotiable
    MODERATE = "moderate"  # Significant concern, requires discussion
    STRONG = "strong"  # Major objection, blocks consensus
    VETO = "veto"  # Fundamental opposition, escalates to Judge


@dataclass
class Viewpoint:
    """A mind's viewpoint on a decision.
    
    Attributes:
        mind_name: Name of the mind expressing this viewpoint
        decision_domain: What decision is this about (e.g., "respond_to_user")
        recommendation: What this mind recommends
        confidence: 0.0-1.0 confidence in this recommendation
        rationale: Detailed reasoning
        tradeoffs: Dict of {factor: impact} this decision involves
        timestamp: When this viewpoint was formed
    """
    mind_name: str
    decision_domain: str
    recommendation: str
    confidence: float
    rationale: str
    tradeoffs: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage."""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d


@dataclass
class Objection:
    """Formal disagreement with rationale.
    
    Attributes:
        objecting_mind: Name of mind raising objection
        target_viewpoint_mind: Which mind's viewpoint is being objected to
        severity: How serious is this objection
        reason: Why this viewpoint is problematic
        alternative: What this mind would prefer instead
        precedent_cited: Any relevant precedent from institutional memory
        timestamp: When objection was raised
    """
    objecting_mind: str
    target_viewpoint_mind: str
    severity: ObjectionSeverity
    reason: str
    alternative: str
    precedent_cited: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage."""
        d = asdict(self)
        d['severity'] = self.severity.value
        d['timestamp'] = self.timestamp.isoformat()
        return d


@dataclass
class CouncilSession:
    """Decision-making session with debate.
    
    Attributes:
        session_id: Unique identifier for this session
        decision_domain: What decision is being made
        context: Brief context for the decision
        viewpoints: List of viewpoints from all minds
        objections: List of objections raised
        consensus_reached: Whether consensus was achieved
        final_decision: The arbitrated decision
        rationale: Why this decision was made
        dissenting_voices: Minds that objected to final decision
        timestamp: When session was conducted
    """
    session_id: str
    decision_domain: str
    context: str
    viewpoints: List[Viewpoint] = field(default_factory=list)
    objections: List[Objection] = field(default_factory=list)
    consensus_reached: bool = False
    final_decision: Optional[str] = None
    rationale: Optional[str] = None
    dissenting_voices: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def add_viewpoint(self, viewpoint: Viewpoint):
        """Add a mind's viewpoint to the session."""
        self.viewpoints.append(viewpoint)
    
    def add_objection(self, objection: Objection):
        """Record an objection."""
        self.objections.append(objection)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage."""
        d = asdict(self)
        d['viewpoints'] = [v.to_dict() for v in self.viewpoints]
        d['objections'] = [o.to_dict() for o in self.objections]
        d['timestamp'] = self.timestamp.isoformat()
        return d


class InstitutionalMemory:
    """Persistent record of civilization decisions.
    
    Stores:
    - Council sessions (who said what, disagreements, arbitration)
    - Precedents (similar past decisions)
    - Objection patterns (recurring concerns from specific minds)
    - Evolution (how civilization's thinking changed over time)
    """
    
    def __init__(self):
        """Initialize institutional memory."""
        self.sessions: List[CouncilSession] = []
        self.veto_records: List[Dict[str, Any]] = []  # Times Judge used veto power
        self.precedents: Dict[str, List[CouncilSession]] = {}  # domain -> sessions
        self.objection_patterns: Dict[str, List[Objection]] = {}  # mind -> objections
    
    def record_session(self, session: CouncilSession):
        """Record a council session in permanent memory."""
        self.sessions.append(session)
        
        # Index by domain for precedent lookup
        domain = session.decision_domain
        if domain not in self.precedents:
            self.precedents[domain] = []
        self.precedents[domain].append(session)
        
        # Track objections by mind
        for objection in session.objections:
            objecting_mind = objection.objecting_mind
            if objecting_mind not in self.objection_patterns:
                self.objection_patterns[objecting_mind] = []
            self.objection_patterns[objecting_mind].append(objection)
    
    def record_veto(self, judge_rationale: str, session_id: str, context: Dict[str, Any]):
        """Record when Judge uses veto power."""
        self.veto_records.append({
            'timestamp': datetime.utcnow().isoformat(),
            'judge_rationale': judge_rationale,
            'session_id': session_id,
            'context': context,
        })
    
    def get_precedent(self, domain: str, limit: int = 3) -> List[CouncilSession]:
        """Retrieve relevant precedent for a decision domain."""
        if domain in self.precedents:
            return self.precedents[domain][-limit:]
        return []
    
    def get_objection_pattern(self, mind_name: str) -> List[Objection]:
        """Get all objections from a specific mind."""
        return self.objection_patterns.get(mind_name, [])
    
    def summarize_conflicts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most significant disagreements."""
        objections = []
        for mind_objections in self.objection_patterns.values():
            objections.extend(mind_objections)
        
        # Sort by severity: VETO > STRONG > MODERATE > WEAK
        severity_order = {'veto': 0, 'strong': 1, 'moderate': 2, 'weak': 3}
        objections.sort(key=lambda x: severity_order.get(x.severity.value, 4))
        
        return [o.to_dict() for o in objections[:limit]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire memory to dict."""
        return {
            'sessions': [s.to_dict() for s in self.sessions],
            'veto_records': self.veto_records,
            'objection_count': sum(len(v) for v in self.objection_patterns.values()),
            'domains_debated': list(self.precedents.keys()),
        }


class Mind(ABC):
    """Base class for specialized minds in Jessica's civilization.
    
    Each mind has:
    - A name and purpose
    - A viewpoint() method that returns its position on decisions
    - An objection_to() method to raise concerns about other viewpoints
    - Rights to escalate conflicts to Judge
    """
    
    def __init__(self, name: str, purpose: str):
        """Initialize a mind.
        
        Args:
            name: Identifier (e.g., "Strategist", "Risk Sentinel")
            purpose: What this mind is responsible for
        """
        self.name = name
        self.purpose = purpose
        self.objections_raised: List[Objection] = []
        self.viewpoints_given: List[Viewpoint] = []
    
    @abstractmethod
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Form a viewpoint on a decision.
        
        Args:
            decision_domain: What type of decision (e.g., "respond_to_user")
            context: Contextual information
            user_text: What user said
            current_draft: Current draft response being considered
        
        Returns:
            Viewpoint representing this mind's position
        """
        pass
    
    @abstractmethod
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Raise objection to another mind's viewpoint.
        
        Returns None if no objection.
        Returns Objection if this mind disagrees.
        """
        pass
    
    def escalate_to_judge(self, objection: Objection, urgency_reason: str) -> bool:
        """Request Judge arbitration on an objection.
        
        Returns True if escalation was honored.
        """
        # This will be called by InternalCourt's escalation mechanism
        pass
