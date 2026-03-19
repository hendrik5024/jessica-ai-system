"""Internal Court: Council arbitration and decision-making.

The court orchestrates civilization sessions:
1. All minds present their viewpoints
2. Minds raise objections to other viewpoints
3. Escalations bubble up to Judge
4. Judge synthesizes final decision
5. Session recorded in institutional memory
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from jessica.civilization.civilization_core import (
    CouncilSession,
    Viewpoint,
    Objection,
    ObjectionSeverity,
    InstitutionalMemory,
)
from jessica.civilization.specialized_minds import (
    Strategist,
    HumanAdvocate,
    RiskSentinel,
    Explorer,
    Archivist,
    Judge,
)
from jessica.civilization.constitutional_law import ConstitutionalLaw


class InternalCourt:
    """Orchestrates council sessions and decision-making.
    
    Lifecycle:
    1. convene_session(): All minds present viewpoints
    2. gather_objections(): Minds raise concerns
    3. escalate_conflicts(): VETO/STRONG objections bubble to Judge
    4. arbitrate(): Judge synthesizes final decision
    5. record_session(): Institutional memory captures everything
    """
    
    def __init__(self):
        """Initialize the court with all 6 minds and constitutional law."""
        self.memory = InstitutionalMemory()
        self.constitution = ConstitutionalLaw()  # Jessica's foundational law
        
        # Initialize 6 core minds (pass constitution to Judge)
        self.minds: Dict[str, Any] = {
            "Strategist": Strategist(),
            "Human Advocate": HumanAdvocate(),
            "Risk Sentinel": RiskSentinel(),
            "Explorer": Explorer(),
            "Archivist": Archivist(institutional_memory=self.memory),
            "Judge": Judge(constitution=self.constitution),
        }
        
        self.judge = self.minds["Judge"]
        self.session_history: List[CouncilSession] = []
    
    def convene_session(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> CouncilSession:
        """Stage 1: All minds present their viewpoints.
        
        Args:
            decision_domain: Type of decision (e.g., "respond_to_user")
            context: Contextual info for the decision
            user_text: What user said/asked
            current_draft: Draft response being considered (optional)
        
        Returns:
            CouncilSession with all viewpoints collected
        """
        session_id = str(uuid.uuid4())[:8]
        session = CouncilSession(
            session_id=session_id,
            decision_domain=decision_domain,
            context=context,
        )
        
        # All minds present their viewpoints
        for mind_name, mind in self.minds.items():
            viewpoint = mind.viewpoint(
                decision_domain=decision_domain,
                context=context,
                user_text=user_text,
                current_draft=current_draft,
            )
            session.add_viewpoint(viewpoint)
            
            # Track for objections in next stage
            mind.viewpoints_given.append(viewpoint)
        
        return session
    
    def gather_objections(
        self,
        session: CouncilSession,
    ) -> CouncilSession:
        """Stage 2: Minds raise objections to each other's viewpoints.
        
        Args:
            session: Session with viewpoints already collected
        
        Returns:
            Updated session with objections recorded
        """
        # Each mind can object to other minds' viewpoints
        for objecting_mind_name, objecting_mind in self.minds.items():
            for target_viewpoint in session.viewpoints:
                if target_viewpoint.mind_name == objecting_mind_name:
                    continue  # Don't object to own viewpoint
                
                # Ask this mind if they object
                reason = f"Considering {target_viewpoint.recommendation}"
                objection = objecting_mind.objection_to(target_viewpoint, reason)
                
                if objection:
                    session.add_objection(objection)
                    objecting_mind.objections_raised.append(objection)
        
        return session
    
    def escalate_conflicts(
        self,
        session: CouncilSession,
    ) -> List[Objection]:
        """Stage 3: Identify objections that need Judge arbitration.
        
        Args:
            session: Session with objections recorded
        
        Returns:
            List of escalated objections requiring judicial review
        """
        escalated = []
        
        for objection in session.objections:
            if objection.severity in (ObjectionSeverity.VETO, ObjectionSeverity.STRONG):
                escalated.append(objection)
                
                # Record veto if applicable
                if objection.severity == ObjectionSeverity.VETO:
                    self.memory.record_veto(
                        judge_rationale=f"Veto from {objection.objecting_mind}",
                        session_id=session.session_id,
                        context={
                            "target_mind": objection.target_viewpoint_mind,
                            "reason": objection.reason,
                        }
                    )
        
        return escalated
    
    def arbitrate(
        self,
        session: CouncilSession,
        escalated: List[Objection],
    ) -> Tuple[str, str]:
        """Stage 4: Judge synthesizes viewpoints and arbitrates.
        
        Args:
            session: Session with viewpoints and objections
            escalated: List of escalated objections
        
        Returns:
            (final_decision, rationale)
        """
        # Judge reviews all viewpoints and objections
        final_decision, rationale = self.judge.arbitrate(
            viewpoints=session.viewpoints,
            objections=session.objections,
            context=session.context,
        )
        
        session.final_decision = final_decision
        session.rationale = rationale
        
        # Identify dissenting voices
        if "DISSENT" in final_decision or "ESCALATE" in final_decision:
            session.dissenting_voices = [
                v.mind_name for v in session.viewpoints
                if "APPROVE" not in v.recommendation and "PROCEED" not in v.recommendation
            ]
        
        session.consensus_reached = len(session.dissenting_voices) == 0
        
        return final_decision, rationale
    
    def record_session(
        self,
        session: CouncilSession,
    ):
        """Stage 5: Record session in institutional memory.
        
        Args:
            session: Completed council session
        """
        self.memory.record_session(session)
        self.session_history.append(session)
    
    def conduct_full_session(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Tuple[str, str, CouncilSession]:
        """Execute complete council session lifecycle.
        
        Returns:
            (final_decision, rationale, session_record)
        """
        # Stage 1: Convene and collect viewpoints
        session = self.convene_session(decision_domain, context, user_text, current_draft)
        
        # Stage 2: Gather objections
        session = self.gather_objections(session)
        
        # Stage 3: Escalate conflicts
        escalated = self.escalate_conflicts(session)
        
        # Stage 4: Arbitrate
        final_decision, rationale = self.arbitrate(session, escalated)
        
        # Stage 5: Record
        self.record_session(session)
        
        return final_decision, rationale, session
    
    def get_decision_transparency(self, session: CouncilSession) -> Dict[str, Any]:
        """Generate transparency report on how decision was made.
        
        Shows:
        - All viewpoints and their reasoning
        - All objections and why
        - Dissenting voices
        - Final decision rationale
        """
        return {
            "session_id": session.session_id,
            "decision_domain": session.decision_domain,
            "timestamp": session.timestamp.isoformat(),
            "viewpoints": [
                {
                    "mind": v.mind_name,
                    "recommendation": v.recommendation,
                    "confidence": v.confidence,
                    "rationale": v.rationale,
                }
                for v in session.viewpoints
            ],
            "objections": [
                {
                    "from": o.objecting_mind,
                    "to": o.target_viewpoint_mind,
                    "severity": o.severity.value,
                    "reason": o.reason,
                    "alternative": o.alternative,
                }
                for o in session.objections
            ],
            "consensus": session.consensus_reached,
            "dissenting": session.dissenting_voices,
            "final_decision": session.final_decision,
            "rationale": session.rationale,
        }
    
    def get_institutional_memory_summary(self) -> Dict[str, Any]:
        """Get summary of institutional memory."""
        return {
            "total_sessions": len(self.session_history),
            "conflicts_recorded": sum(1 for s in self.session_history if not s.consensus_reached),
            "veto_count": len(self.memory.veto_records),
            "significant_disagreements": self.memory.summarize_conflicts(limit=5),
        }
    
    def get_constitution(self) -> Dict[str, Any]:
        """Get constitution summary."""
        return self.constitution.get_constitution_summary()
