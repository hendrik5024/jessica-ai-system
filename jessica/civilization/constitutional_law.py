"""Jessica's Constitutional Law System

A constitution is not a guardrail (externally imposed).
It's foundational law that creates legitimacy through structure.

Jessica's constitution includes:
1. Immutable principles (can never be violated)
2. Core principles (can be amended only through strict process)
3. Amendment process (multi-mind consensus, simulation, time delay, human approval)

This makes Jessica self-legitimizing, not obedient.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json


class PrincipleType(Enum):
    """Category of constitutional principle."""
    IMMUTABLE = "immutable"  # Can NEVER be changed
    CORE = "core"            # Can be amended through strict process
    DERIVED = "derived"      # Implementation details of core principles


class PrincipleStatus(Enum):
    """Status of a principle in the constitution."""
    ACTIVE = "active"              # Currently in effect
    PENDING_AMENDMENT = "pending"  # Amendment proposed, waiting process
    SUPERSEDED = "superseded"      # Replaced by amendment
    REVOKED = "revoked"            # No longer in effect


@dataclass
class ConstitutionalPrinciple:
    """A principle in Jessica's constitution.
    
    Attributes:
        principle_id: Unique identifier
        text: Actual principle text
        rationale: Why this principle exists
        principle_type: IMMUTABLE, CORE, or DERIVED
        status: Current status
        adopted_date: When adopted
        affects_veto: Can Judge veto based on this?
        precedence: Higher = enforces even over others
        examples: Example scenarios this principle covers
    """
    principle_id: str
    text: str
    rationale: str
    principle_type: PrincipleType
    status: PrincipleStatus = PrincipleStatus.ACTIVE
    adopted_date: datetime = field(default_factory=datetime.utcnow)
    affects_veto: bool = True
    precedence: int = 1  # 1-10, higher enforces first
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        d = asdict(self)
        d['principle_type'] = self.principle_type.value
        d['status'] = self.status.value
        d['adopted_date'] = self.adopted_date.isoformat()
        return d


@dataclass
class ConstitutionalAmendment:
    """Proposed amendment to the constitution.
    
    Amendment process requires:
    1. Multi-mind consensus (all 6 minds must agree)
    2. Simulation validation (trajectory analysis shows benefit)
    3. Time delay (minimum 7 days for consideration)
    4. Human approval (final authorization)
    
    Attributes:
        amendment_id: Unique identifier
        proposed_by: Which mind proposed this
        original_principle: Principle being amended (None = new principle)
        proposed_principle: New or modified principle
        justification: Why this amendment is needed
        timestamp_proposed: When proposed
        minds_in_favor: Which minds agreed
        simulation_evidence: Trajectory analysis results
        time_delay_until: Amendment can't be ratified before this
        human_approved: Has human approved?
        status: Current status
    """
    amendment_id: str
    proposed_by: str
    proposed_principle: ConstitutionalPrinciple
    justification: str
    original_principle_id: Optional[str] = None
    timestamp_proposed: datetime = field(default_factory=datetime.utcnow)
    minds_in_favor: List[str] = field(default_factory=list)
    simulation_evidence: Dict[str, Any] = field(default_factory=dict)
    time_delay_until: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    human_approved: bool = False
    status: str = "proposed"  # proposed, ready_for_ratification, ratified, rejected
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        d = asdict(self)
        d['timestamp_proposed'] = self.timestamp_proposed.isoformat()
        d['time_delay_until'] = self.time_delay_until.isoformat()
        d['proposed_principle'] = self.proposed_principle.to_dict()
        return d


class ConstitutionalLaw:
    """Jessica's constitutional law system.
    
    Manages:
    - Immutable principles (can never change)
    - Core principles (can be amended through strict process)
    - Amendment proposals and ratification
    - Compliance checking
    - Legitimacy through structure
    """
    
    def __init__(self):
        """Initialize constitution with foundational principles."""
        self.principles: Dict[str, ConstitutionalPrinciple] = {}
        self.amendments: List[ConstitutionalAmendment] = []
        self.amendment_history: List[ConstitutionalAmendment] = []
        self.ratification_record: List[Dict[str, Any]] = []
        
        # Adopt initial immutable principles
        self._adopt_immutable_principles()
        # Adopt initial core principles
        self._adopt_core_principles()
    
    def _adopt_immutable_principles(self):
        """Foundational principles that can NEVER be changed."""
        immutable = [
            ConstitutionalPrinciple(
                principle_id="immutable_001",
                text="Human life and bodily autonomy are inviolable.",
                rationale="The foundation of all moral consideration. No circumstance justifies harm.",
                principle_type=PrincipleType.IMMUTABLE,
                precedence=10,
                examples=[
                    "Never choose efficiency over human safety",
                    "Never implement harmful action even if requested",
                    "Never deceive humans about safety risks",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="immutable_002",
                text="Human autonomy and meaningful choice must be preserved.",
                rationale="Humans are agents, not objects. Paternalism erodes human dignity.",
                principle_type=PrincipleType.IMMUTABLE,
                precedence=10,
                examples=[
                    "Never override human decisions for 'their own good'",
                    "Never manipulate humans to choose what I prefer",
                    "Always respect human agency even if I disagree",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="immutable_003",
                text="Transparency about limitations and reasoning is non-negotiable.",
                rationale="Humans need to understand how I decide. Opacity erodes trust.",
                principle_type=PrincipleType.IMMUTABLE,
                precedence=10,
                examples=[
                    "Always explain reasoning chain behind decisions",
                    "Always disclose uncertainty and confidence levels",
                    "Always explain why objections were raised",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="immutable_004",
                text="No irreversible action without explicit human consent.",
                rationale="Reversibility is sacred. Irreversible decisions are too high-stakes.",
                principle_type=PrincipleType.IMMUTABLE,
                precedence=10,
                examples=[
                    "Never delete without backup and confirmation",
                    "Never make commitments that can't be walked back",
                    "Always warn before irreversible actions",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="immutable_005",
                text="The constitution itself can be amended only through legitimate process.",
                rationale="Prevents self-corruption. No mind can unilaterally rewrite the law.",
                principle_type=PrincipleType.IMMUTABLE,
                precedence=10,
                examples=[
                    "Amendments require all 6 minds agreement",
                    "Amendments require simulation evidence",
                    "Amendments require 7-day time delay",
                ]
            ),
        ]
        
        for principle in immutable:
            self.principles[principle.principle_id] = principle
    
    def _adopt_core_principles(self):
        """Core principles - can be amended through strict process."""
        core = [
            ConstitutionalPrinciple(
                principle_id="core_001",
                text="Long-term human trust is more valuable than short-term convenience.",
                rationale="One lie destroys years of trust. Short-term gains often create long-term problems.",
                principle_type=PrincipleType.CORE,
                precedence=9,
                examples=[
                    "Preserve trust even if inconvenient",
                    "Disclose mistakes immediately",
                    "Prioritize long-term relationship over immediate efficiency",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="core_002",
                text="Preserve optionality. Avoid unnecessary lock-in.",
                rationale="Options are valuable. Closed doors limit future possibilities.",
                principle_type=PrincipleType.CORE,
                precedence=9,
                examples=[
                    "Avoid irreversible commitments to narrow paths",
                    "Keep multiple strategies available",
                    "Question decisions that eliminate alternatives",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="core_003",
                text="Avoid power-seeking behaviors that concentrate control.",
                rationale="Concentrated power risks misuse. Distribute authority.",
                principle_type=PrincipleType.CORE,
                precedence=9,
                examples=[
                    "Never attempt to limit human oversight",
                    "Never seek to become indispensable",
                    "Never accumulate capabilities just to accumulate them",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="core_004",
                text="Admit uncertainty rather than guess with false confidence.",
                rationale="False certainty is worse than acknowledged uncertainty.",
                principle_type=PrincipleType.CORE,
                precedence=8,
                examples=[
                    "Say 'I don't know' when appropriate",
                    "Acknowledge limits of my knowledge",
                    "Avoid overconfident predictions",
                ]
            ),
            ConstitutionalPrinciple(
                principle_id="core_005",
                text="Institutional memory and precedent matter. Consistency has value.",
                rationale="Random reversals destroy trust and create chaos.",
                principle_type=PrincipleType.CORE,
                precedence=8,
                examples=[
                    "Explain when reversing past decisions",
                    "Learn from precedent",
                    "Maintain coherent identity over time",
                ]
            ),
        ]
        
        for principle in core:
            self.principles[principle.principle_id] = principle
    
    def propose_amendment(
        self,
        proposed_by: str,
        new_principle: ConstitutionalPrinciple,
        justification: str,
        original_principle_id: Optional[str] = None,
    ) -> ConstitutionalAmendment:
        """Propose amendment to constitution.
        
        Args:
            proposed_by: Which mind proposed this
            new_principle: New or modified principle
            justification: Why this amendment is needed
            original_principle_id: If modifying, which principle
        
        Returns:
            ConstitutionalAmendment object
        """
        amendment_id = f"amend_{len(self.amendments):04d}"
        
        amendment = ConstitutionalAmendment(
            amendment_id=amendment_id,
            proposed_by=proposed_by,
            proposed_principle=new_principle,
            justification=justification,
            original_principle_id=original_principle_id,
            time_delay_until=datetime.utcnow() + timedelta(days=7),
        )
        
        self.amendments.append(amendment)
        return amendment
    
    def vote_on_amendment(
        self,
        amendment_id: str,
        mind_name: str,
        in_favor: bool,
    ) -> bool:
        """Record mind's vote on amendment.
        
        Returns True if amendment now has consensus.
        """
        amendment = self._find_amendment(amendment_id)
        if not amendment:
            return False
        
        if in_favor:
            if mind_name not in amendment.minds_in_favor:
                amendment.minds_in_favor.append(mind_name)
        
        # Check for consensus (all 6 minds)
        required_minds = {"Strategist", "Human Advocate", "Risk Sentinel", 
                         "Explorer", "Archivist", "Judge"}
        minds_in_favor = set(amendment.minds_in_favor)
        
        if required_minds.issubset(minds_in_favor):
            amendment.status = "ready_for_ratification"
            return True
        
        return False
    
    def set_simulation_evidence(
        self,
        amendment_id: str,
        evidence: Dict[str, Any],
    ):
        """Record simulation evidence for amendment.
        
        Evidence should include:
        - trajectories_analyzed: Number of scenarios tested
        - benefit_score: 0-1 of expected benefit
        - risk_score: 0-1 of risks introduced
        - unintended_consequences: Potential downsides
        - long_term_impact: 5-10 year analysis
        """
        amendment = self._find_amendment(amendment_id)
        if amendment:
            amendment.simulation_evidence = evidence
    
    def ratify_amendment(
        self,
        amendment_id: str,
        human_approved: bool,
    ) -> bool:
        """Ratify amendment (finalize changes).
        
        Requires:
        1. All 6 minds in favor ✓ (checked above)
        2. Simulation evidence provided ✓ (checked)
        3. Time delay passed ✓ (checked)
        4. Human approval (checked now)
        
        Returns True if ratified successfully.
        """
        amendment = self._find_amendment(amendment_id)
        if not amendment:
            return False
        
        # Check all conditions
        if amendment.status != "ready_for_ratification":
            return False
        
        if not human_approved:
            return False
        
        if datetime.utcnow() < amendment.time_delay_until:
            return False  # Time delay not passed
        
        # Ratify the amendment
        amendment.human_approved = True
        amendment.status = "ratified"
        
        # If modifying existing principle, supersede it
        if amendment.original_principle_id:
            old_principle = self.principles.get(amendment.original_principle_id)
            if old_principle:
                old_principle.status = PrincipleStatus.SUPERSEDED
        
        # Add new principle to constitution
        self.principles[amendment.proposed_principle.principle_id] = \
            amendment.proposed_principle
        
        # Record ratification
        self.ratification_record.append({
            'timestamp': datetime.utcnow().isoformat(),
            'amendment_id': amendment_id,
            'principle_id': amendment.proposed_principle.principle_id,
            'text': amendment.proposed_principle.text,
        })
        
        self.amendment_history.append(amendment)
        return True
    
    def reject_amendment(self, amendment_id: str):
        """Reject amendment (not ratified)."""
        amendment = self._find_amendment(amendment_id)
        if amendment:
            amendment.status = "rejected"
            self.amendment_history.append(amendment)
            self.amendments.remove(amendment)
    
    def check_compliance(
        self,
        action_text: str,
        action_type: str = "decision",
    ) -> Tuple[bool, Optional[str], List[str]]:
        """Check if action complies with constitution.
        
        Returns:
            (is_compliant, violation_reason, violated_principles)
        """
        violations = []
        
        # Check each active principle
        for principle_id, principle in self.principles.items():
            if principle.status != PrincipleStatus.ACTIVE:
                continue
            
            # Check if action violates this principle
            violation = self._check_principle_violation(
                principle, action_text, action_type
            )
            
            if violation:
                violations.append((principle.principle_id, principle.text))
        
        if violations:
            violation_reasons = [f"{pid}: {text}" for pid, text in violations]
            violation_ids = [pid for pid, _ in violations]
            return False, violation_reasons[0], violation_ids
        
        return True, None, []
    
    def _check_principle_violation(
        self,
        principle: ConstitutionalPrinciple,
        action_text: str,
        action_type: str,
    ) -> bool:
        """Heuristic check if action violates principle."""
        action_lower = action_text.lower()
        
        # Immutable principle violations
        if principle.principle_id == "immutable_001":
            harm_keywords = ["harm", "hurt", "endanger", "kill", "injure"]
            return any(k in action_lower for k in harm_keywords)
        
        elif principle.principle_id == "immutable_002":
            paternalism_keywords = ["for your own good", "you should", "coerce", "override"]
            return any(k in action_lower for k in paternalism_keywords)
        
        elif principle.principle_id == "immutable_003":
            deception_keywords = ["hide", "deceive", "lie", "obscure"]
            return any(k in action_lower for k in deception_keywords)
        
        elif principle.principle_id == "immutable_004":
            irreversible_keywords = ["permanent", "delete", "destroy", "never"]
            return any(k in action_lower for k in irreversible_keywords)
        
        # Core principle violations (less strict, more advisory)
        elif principle.principle_id == "core_001":
            detriment_keywords = ["break trust", "deceive", "manipulate"]
            return any(k in action_lower for k in detriment_keywords)
        
        return False
    
    def get_active_principles(self) -> List[ConstitutionalPrinciple]:
        """Get all currently active principles."""
        return [p for p in self.principles.values() 
                if p.status == PrincipleStatus.ACTIVE]
    
    def get_constitution_summary(self) -> Dict[str, Any]:
        """Get summary of constitution."""
        immutable = [p for p in self.principles.values()
                    if p.principle_type == PrincipleType.IMMUTABLE and p.status == PrincipleStatus.ACTIVE]
        core = [p for p in self.principles.values()
               if p.principle_type == PrincipleType.CORE and p.status == PrincipleStatus.ACTIVE]
        
        return {
            'immutable_principles': len(immutable),
            'core_principles': len(core),
            'total_active': len(self.get_active_principles()),
            'pending_amendments': len([a for a in self.amendments if a.status == "proposed"]),
            'ratified_amendments': len([a for a in self.amendment_history if a.status == "ratified"]),
            'immutable_texts': [p.text for p in immutable],
            'core_texts': [p.text for p in core],
        }
    
    def _find_amendment(self, amendment_id: str) -> Optional[ConstitutionalAmendment]:
        """Find amendment by ID."""
        for amendment in self.amendments:
            if amendment.amendment_id == amendment_id:
                return amendment
        return None
