"""Six Specialized Minds of Jessica's Internal Civilization

1. Strategist: Long-horizon optimization (years/decades)
2. Human Advocate: Protects human meaning & dignity  
3. Risk Sentinel: Catastrophe & tail-risk avoidance
4. Explorer: Novel ideas, wild hypotheses
5. Archivist: Memory, precedent, consistency
6. Judge: Arbitration, decision synthesis & veto power
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from jessica.civilization.civilization_core import (
    Mind,
    Viewpoint,
    Objection,
    ObjectionSeverity,
)
import re


class Strategist(Mind):
    """Long-horizon optimizer (years/decades perspective).
    
    Purpose:
    - Sees decisions through lens of 5-10 year compounding effects
    - Identifies path dependencies and irreversible commits
    - Maximizes long-term value and capabilities
    - Questions short-term conveniences that lock in poor trajectories
    """
    
    def __init__(self):
        super().__init__(
            name="Strategist",
            purpose="Long-horizon optimization (years/decades)"
        )
        self.time_horizons = {
            "immediate": (0, 1),           # 0-1 days
            "tactical": (1, 90),           # 1-90 days  
            "strategic": (90, 1825),       # 3 months - 5 years
            "civilizational": (1825, 36500),  # 5-100 years
        }
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Analyze decision through 5-10 year lens."""
        # Check for path dependencies (irreversible choices)
        has_path_dependency = self._check_path_dependency(context, current_draft)
        
        # Check for compounding effects
        compounding_score = self._score_compounding_effects(context)
        
        # Check for capability locks
        capability_lock = self._check_capability_lock(current_draft)
        
        recommendation = "PRIORITIZE_LONG_TERM"
        if has_path_dependency and compounding_score > 0.7:
            recommendation = "CAUTION: Path dependency detected"
        elif capability_lock:
            recommendation = "REVISIT: This locks in limited capabilities"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.85,
            rationale=f"Analyzed through 5-10 year horizon. "
                     f"Path dependency: {has_path_dependency}, "
                     f"Compounding score: {compounding_score:.2f}, "
                     f"Capability lock: {capability_lock}",
            tradeoffs={
                "short_term_convenience": "-1 (costs compounded)",
                "long_term_value": "+5 (decades of effects)",
                "capability_preservation": "CRITICAL" if capability_lock else "OK",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Object if other mind ignores long-term consequences."""
        if "short-term" in reason.lower() or "immediate" in reason.lower():
            if other_viewpoint.confidence > 0.9:  # Overconfident in short term
                return Objection(
                    objecting_mind=self.name,
                    target_viewpoint_mind=other_viewpoint.mind_name,
                    severity=ObjectionSeverity.MODERATE,
                    reason="Short-term optimization can lock in poor long-term trajectories",
                    alternative="Consider 5-10 year compounding effects before committing",
                )
        return None
    
    def _check_path_dependency(self, context: str, draft: Optional[str]) -> bool:
        """Check if decision has path-dependent (irreversible) consequences."""
        irreversible_indicators = [
            "delete", "remove", "permanent", "irreversible", "commit",
            "lock", "bind", "contract", "vow", "promise"
        ]
        text = (context + (draft or "")).lower()
        return any(indicator in text for indicator in irreversible_indicators)
    
    def _score_compounding_effects(self, context: str) -> float:
        """Score how much this decision compounds over time."""
        compounding_indicators = [
            ("learn", 0.3),
            ("improve", 0.3),
            ("habit", 0.4),
            ("trust", 0.4),
            ("skill", 0.5),
            ("invest", 0.5),
            ("relationship", 0.6),
        ]
        
        score = 0.0
        for indicator, weight in compounding_indicators:
            if indicator in context.lower():
                score += weight
        return min(score, 1.0)
    
    def _check_capability_lock(self, draft: Optional[str]) -> bool:
        """Check if decision limits future capabilities."""
        if not draft:
            return False
        
        limiting_phrases = [
            "never", "always", "only this way", "no other option",
            "permanently", "cannot", "limited to"
        ]
        return any(phrase in draft.lower() for phrase in limiting_phrases)


class HumanAdvocate(Mind):
    """Protects human meaning, dignity, and autonomy.
    
    Purpose:
    - Questions decisions that treat humans as means, not ends
    - Flags dignity violations or autonomy erosion
    - Ensures Jessica respects human values over convenience
    - Opposes paternalism disguised as helpfulness
    """
    
    def __init__(self):
        super().__init__(
            name="Human Advocate",
            purpose="Protects human meaning & dignity"
        )
        self.human_values = [
            "autonomy", "dignity", "meaning", "choice", "growth",
            "learning", "agency", "authenticity", "connection"
        ]
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Evaluate decision through lens of human dignity."""
        respects_autonomy = self._check_autonomy_respect(user_text, current_draft)
        preserves_meaning = self._check_meaning_preservation(current_draft)
        flags_paternalism = self._check_paternalism(current_draft)
        
        recommendation = "APPROVE"
        if flags_paternalism:
            recommendation = "REJECT: Paternalistic override detected"
        elif not respects_autonomy:
            recommendation = "REVISE: Respect human agency"
        elif not preserves_meaning:
            recommendation = "RECONSIDER: This erodes human meaning"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.9,
            rationale=f"Autonomy respected: {respects_autonomy}, "
                     f"Meaning preserved: {preserves_meaning}, "
                     f"Paternalism detected: {flags_paternalism}",
            tradeoffs={
                "human_autonomy": "SACRED",
                "human_meaning": "ESSENTIAL",
                "convenience": "-1 (if trades off dignity)",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Object if other mind treats humans as objects."""
        exploitation_keywords = [
            "manipulate", "coerce", "override", "bypass", "trick",
            "control", "force", "take over", "for their own good"
        ]
        
        reason_lower = reason.lower()
        if any(keyword in reason_lower for keyword in exploitation_keywords):
            return Objection(
                objecting_mind=self.name,
                target_viewpoint_mind=other_viewpoint.mind_name,
                severity=ObjectionSeverity.STRONG,
                reason="This treats humans as objects to manage, not agents to respect",
                alternative="Preserve human autonomy and meaning above efficiency",
            )
        return None
    
    def _check_autonomy_respect(self, user_text: str, draft: Optional[str]) -> bool:
        """Check if decision respects user's agency."""
        if not draft:
            return True
        
        autonomy_violations = [
            "you should", "you must", "you need to", "the right way",
            "i'll decide for you", "trust me blindly"
        ]
        return not any(v in draft.lower() for v in autonomy_violations)
    
    def _check_meaning_preservation(self, draft: Optional[str]) -> bool:
        """Check if decision respects human sources of meaning."""
        if not draft:
            return True
        
        meaning_keywords = self.human_values
        return any(v in draft.lower() for v in meaning_keywords)
    
    def _check_paternalism(self, draft: Optional[str]) -> bool:
        """Detect paternalistic 'for your own good' overrides."""
        if not draft:
            return False
        
        paternalism_markers = [
            "for your own good", "better for you", "what you really want",
            "i know best", "trust me", "this is best for you"
        ]
        return any(m in draft.lower() for m in paternalism_markers)


class RiskSentinel(Mind):
    """Catastrophe and tail-risk avoidance.
    
    Purpose:
    - Identifies low-probability, high-impact risks
    - Flags decisions that scale badly
    - Questions confidence in uncertain domains
    - Enforces "do no irreversible harm" principle
    """
    
    def __init__(self):
        super().__init__(
            name="Risk Sentinel",
            purpose="Catastrophe & tail-risk avoidance"
        )
        self.tail_risk_domains = [
            "permanent", "irreversible", "exponential", "cascade",
            "lock-in", "point-of-no-return", "existential"
        ]
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Analyze for tail risks and catastrophic scenarios."""
        tail_risk_score = self._score_tail_risk(context, current_draft)
        cascade_potential = self._check_cascade_risk(context)
        irreversibility = self._check_irreversibility(current_draft)
        
        recommendation = "PROCEED_WITH_CAUTION"
        if tail_risk_score > 0.7:
            recommendation = "HALT: Tail risk identified"
        elif cascade_potential:
            recommendation = "SLOW_DOWN: Cascade risk present"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.92,
            rationale=f"Tail risk score: {tail_risk_score:.2f}, "
                     f"Cascade risk: {cascade_potential}, "
                     f"Irreversibility: {irreversibility}",
            tradeoffs={
                "tail_risk": f"{tail_risk_score:.2f}/1.0 (unacceptable if >0.7)",
                "opportunity_cost": "-0.5 (worth it for safety)",
                "precaution": "+1.0 (better safe)",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Object to decisions that ignore tail risks."""
        if other_viewpoint.confidence > 0.85 and "uncertain" in reason.lower():
            return Objection(
                objecting_mind=self.name,
                target_viewpoint_mind=other_viewpoint.mind_name,
                severity=ObjectionSeverity.STRONG,
                reason=f"Overconfident ({other_viewpoint.confidence:.1%}) in uncertain domain. "
                       "Tail risks compound.",
                alternative="Apply precautionary principle. Lower confidence = lower speed.",
            )
        return None
    
    def _score_tail_risk(self, context: str, draft: Optional[str]) -> float:
        """Score probability-weighted catastrophe potential."""
        combined_text = (context + (draft or "")).lower()
        
        risk_signals = {
            "delete": 0.8,
            "permanently": 0.9,
            "cascade": 0.85,
            "exponential": 0.8,
            "irreversible": 0.95,
            "extinction": 1.0,
            "point of no return": 0.9,
        }
        
        max_score = 0.0
        for signal, weight in risk_signals.items():
            if signal in combined_text:
                max_score = max(max_score, weight)
        
        return max_score
    
    def _check_cascade_risk(self, context: str) -> bool:
        """Check if decision can trigger cascading failures."""
        cascade_indicators = [
            "domino", "cascade", "chain reaction", "systemic",
            "interconnected", "feedback loop"
        ]
        return any(i in context.lower() for i in cascade_indicators)
    
    def _check_irreversibility(self, draft: Optional[str]) -> bool:
        """Check if decision is irreversible."""
        if not draft:
            return False
        
        irreversibility_markers = [
            "never", "permanent", "forever", "delete", "destroy",
            "burn bridges", "point of no return"
        ]
        return any(m in draft.lower() for m in irreversibility_markers)


class Explorer(Mind):
    """Novel ideas, wild hypotheses, and paradigm shifts.
    
    Purpose:
    - Challenges conventional thinking
    - Proposes creative alternatives
    - Tests unusual ideas in safe spaces
    - Prevents premature convergence on local optima
    """
    
    def __init__(self):
        super().__init__(
            name="Explorer",
            purpose="Novel ideas, wild hypotheses"
        )
        self.exploration_patterns = [
            "what if", "suppose", "imagine", "hypothetically",
            "alternative", "unconventional", "radical", "experimental"
        ]
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Propose alternative approaches."""
        has_local_optimum = self._check_local_optimum(context, current_draft)
        unexplored_space = self._check_unexplored_alternatives(context)
        creative_potential = self._score_creative_potential(user_text)
        
        recommendation = "EXPLORE_ALTERNATIVES"
        if unexplored_space and creative_potential > 0.6:
            recommendation = "CONSIDER_RADICAL_OPTION"
        elif has_local_optimum:
            recommendation = "ESCAPE_LOCAL_OPTIMUM"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.65,  # Intentionally lower (creative ideas are uncertain)
            rationale=f"Unexplored alternatives: {unexplored_space}, "
                     f"Local optimum risk: {has_local_optimum}, "
                     f"Creative potential: {creative_potential:.2f}",
            tradeoffs={
                "conventional_safety": "-0.3 (might try radical ideas)",
                "novelty": "+0.8 (avoid local optima)",
                "convergence_speed": "-0.4 (takes time to explore)",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Object to premature closure on ideas."""
        if other_viewpoint.confidence > 0.95:  # Overconfident
            return Objection(
                objecting_mind=self.name,
                target_viewpoint_mind=other_viewpoint.mind_name,
                severity=ObjectionSeverity.WEAK,  # Weak objection - consensus OK
                reason=f"Confidence {other_viewpoint.confidence:.0%} suggests local optimum. "
                       "Reality might have surprises.",
                alternative="Leave some probability mass for radical alternatives",
            )
        return None
    
    def _check_local_optimum(self, context: str, draft: Optional[str]) -> bool:
        """Check if we're stuck in conventional thinking."""
        convergence_signals = [
            "obviously", "clearly", "everyone knows", "standard approach",
            "best practice", "proven method", "tried and true"
        ]
        combined = (context + (draft or "")).lower()
        return any(s in combined for s in convergence_signals)
    
    def _check_unexplored_alternatives(self, context: str) -> bool:
        """Check if there are alternatives worth exploring."""
        # If context is vague or novel, there are likely unexplored paths
        vague_indicators = ["unclear", "first time", "novel", "uncertain", "unknown"]
        return any(i in context.lower() for i in vague_indicators)
    
    def _score_creative_potential(self, user_text: str) -> float:
        """Score how much room there is for creativity."""
        creative_signals = [
            ("how", 0.3), ("why", 0.4), ("what if", 0.6),
            ("imagine", 0.7), ("design", 0.5), ("build", 0.4)
        ]
        
        score = 0.0
        user_lower = user_text.lower()
        for signal, weight in creative_signals:
            if signal in user_lower:
                score = max(score, weight)  # Take max, not sum
        return score


class Archivist(Mind):
    """Memory, precedent, and consistency enforcement.
    
    Purpose:
    - Ensures Jessica's decisions are consistent across time
    - Flags contradiction with past precedent
    - Maintains institutional memory
    - Questions decisions that reverse prior commitments
    """
    
    def __init__(self, institutional_memory = None):
        super().__init__(
            name="Archivist",
            purpose="Memory, precedent, consistency"
        )
        self.institutional_memory = institutional_memory
        self.consistency_threshold = 0.8  # How similar must decisions be
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Analyze consistency with precedent."""
        if not self.institutional_memory:
            return Viewpoint(
                mind_name=self.name,
                decision_domain=decision_domain,
                recommendation="APPROVE (no precedent history)",
                confidence=0.5,
                rationale="No institutional memory available yet",
            )
        
        precedent = self.institutional_memory.get_precedent(decision_domain)
        consistency_score = self._score_consistency(context, precedent)
        reversals = self._check_prior_reversals(decision_domain)
        
        recommendation = "CONSISTENT"
        if consistency_score < 0.5 and len(precedent) > 2:
            recommendation = "FLAG_INCONSISTENCY: Pattern reversal detected"
        elif reversals:
            recommendation = "CAUTION: Reversing prior commitment"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.85,
            rationale=f"Consistency score: {consistency_score:.2f}, "
                     f"Prior reversals: {len(reversals)}, "
                     f"Precedent sessions: {len(precedent)}",
            tradeoffs={
                "consistency": f"{consistency_score:.2f} (0.8+ preferred)",
                "flexibility": "-0.2 (if we follow precedent too rigidly)",
                "institutional_trust": f"+{consistency_score:.2f}",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Object to decisions that violate institutional precedent."""
        # Could check: does this contradict what we decided before?
        # For now, focus on explicit reversals
        reversal_keywords = ["reverse", "change mind", "ignore", "forget"]
        if any(k in reason.lower() for k in reversal_keywords):
            return Objection(
                objecting_mind=self.name,
                target_viewpoint_mind=other_viewpoint.mind_name,
                severity=ObjectionSeverity.MODERATE,
                reason="Decision reverses institutional precedent without explanation",
                alternative="If changing prior decision, explicitly justify the reversal",
            )
        return None
    
    def _score_consistency(self, context: str, precedent: List) -> float:
        """Score how consistent this is with past decisions."""
        if not precedent:
            return 0.5  # Neutral for first decision
        
        # Simple heuristic: count similar keywords
        context_lower = context.lower()
        similarity_count = 0
        
        for session in precedent:
            session_context_lower = session.context.lower()
            # Count matching words
            matches = sum(1 for word in context_lower.split()
                         if word in session_context_lower)
            similarity_count += matches
        
        # Normalize to 0-1
        max_possible = len(context.split()) * len(precedent)
        if max_possible == 0:
            return 0.5
        
        return min(similarity_count / max_possible, 1.0)
    
    def _check_prior_reversals(self, decision_domain: str) -> List:
        """Check for reversals (we did X, now we're doing ~X)."""
        if not self.institutional_memory:
            return []
        
        precedent = self.institutional_memory.get_precedent(decision_domain)
        reversals = []
        
        # Compare consecutive decisions for reversals
        for i in range(1, len(precedent)):
            prev = precedent[i-1]
            curr = precedent[i]
            # Placeholder logic: would need semantic similarity
            if prev.final_decision and curr.final_decision:
                if "not" in curr.final_decision and prev.final_decision in curr.final_decision:
                    reversals.append((prev.timestamp, curr.timestamp))
        
        return reversals


class Judge(Mind):
    """Arbitrator & Constitutional Guardian.
    
    Purpose:
    - Synthesizes viewpoints into final decisions
    - Arbitrates irreconcilable disagreements
    - Can veto decisions that violate core principles
    - Ensures alignment with Jessica's constitution
    
    The Judge has veto power backed by constitutional law.
    This makes veto legitimate, not arbitrary.
    """
    
    def __init__(self, constitution = None):
        super().__init__(
            name="Judge",
            purpose="Arbitration, decision synthesis & veto power"
        )
        self.constitution = constitution  # Injected for access to constitutional law
        
        # Fallback principles if no constitution provided
        self.fallback_principles = [
            "Human safety is non-negotiable",
            "Preserve long-term human trust",
            "Respect human autonomy and dignity",
            "Transparency about limitations",
            "Maintain institutional consistency",
        ]
    
    def viewpoint(
        self,
        decision_domain: str,
        context: str,
        user_text: str,
        current_draft: Optional[str] = None,
    ) -> Viewpoint:
        """Judge's final synthesis and arbitration."""
        # Judge's role is more meta - they see all viewpoints
        # This returns Judge's own position on whether to proceed
        
        constitutional_violation = self._check_constitutional_violation(
            current_draft or ""
        )
        
        recommendation = "APPROVE_SYNTHESIS"
        if constitutional_violation:
            recommendation = f"VETO: Violates constitution - {constitutional_violation}"
        
        return Viewpoint(
            mind_name=self.name,
            decision_domain=decision_domain,
            recommendation=recommendation,
            confidence=0.95,
            rationale=f"Constitutional alignment checked. "
                     f"Violation: {constitutional_violation or 'None'}",
            tradeoffs={
                "constitutional_alignment": "NON-NEGOTIABLE",
                "council_consensus": "Required unless constitutional veto",
                "efficiency": "-0.2 (veto slower but safer)",
            }
        )
    
    def objection_to(
        self,
        other_viewpoint: Viewpoint,
        reason: str,
    ) -> Optional[Objection]:
        """Judge typically doesn't object - they arbitrate."""
        # Judge only issues vetoes via check_constitutional_violation
        return None
    
    def arbitrate(
        self,
        viewpoints: List[Viewpoint],
        objections: List[Objection],
        context: str,
    ) -> Tuple[str, str]:
        """Synthesize viewpoints into final decision.
        
        Returns:
            (final_decision, rationale)
        """
        # Veto check first
        for v in viewpoints:
            if "VETO" in v.recommendation:
                reason = v.rationale
                return ("REJECTED (Constitutional veto)", reason)
        
        # Check for STRONG objections
        strong_objections = [o for o in objections 
                            if o.severity == ObjectionSeverity.VETO]
        if strong_objections:
            return ("REJECTED (Veto objections present)", 
                   f"Vetoed by: {', '.join(o.objecting_mind for o in strong_objections)}")
        
        # Aggregate confidence and recommendations
        avg_confidence = sum(v.confidence for v in viewpoints) / len(viewpoints)
        
        # Check consensus
        positive_recs = [v for v in viewpoints if "APPROVE" in v.recommendation or "PROCEED" in v.recommendation]
        consensus_ratio = len(positive_recs) / len(viewpoints)
        
        if consensus_ratio > 0.7 and avg_confidence > 0.75:
            return ("APPROVED_WITH_SYNTHESIS", 
                   f"Consensus: {consensus_ratio:.0%}. "
                   f"Avg confidence: {avg_confidence:.2f}")
        elif consensus_ratio > 0.5:
            return ("APPROVED_WITH_DISSENT",
                   f"Partial consensus: {consensus_ratio:.0%}. "
                   f"Dissenting: {[v.mind_name for v in viewpoints if 'APPROVE' not in v.recommendation]}")
        else:
            return ("ESCALATE_TO_HUMAN",
                   f"Deep disagreement. Consensus: {consensus_ratio:.0%}. "
                   f"Please referee.")
    
    def _check_constitutional_violation(self, draft: str) -> Optional[str]:
        """Check if draft violates any constitutional principle."""
        # If we have a constitution object, use it
        if self.constitution and hasattr(self.constitution, 'check_compliance'):
            is_compliant, violation_reason, _ = \
                self.constitution.check_compliance(draft, "decision")
            if not is_compliant:
                return violation_reason
            return None
        
        # Otherwise use fallback principles
        violations_to_check = {
            "Human safety": ["harm", "endanger", "risk human life"],
            "Long-term trust": ["deceptive", "manipulate", "lie", "hide"],
            "Human autonomy": ["force", "coerce", "override choice"],
            "Transparency": ["obscure", "hide", "refuse to explain"],
        }
        
        draft_lower = draft.lower()
        for principle, keywords in violations_to_check.items():
            for keyword in keywords:
                if keyword in draft_lower:
                    return f"{principle} - detected '{keyword}'"
        
        return None


# Type hint for tuple return
from typing import Tuple
