"""Phase 8: Conversational Identity Layer - Conversational Orchestrator

Single entry point for converting technical outputs to natural conversational narratives.

This orchestrator coordinates the transformation of Phase 7.3 reflections into
first-person, human-friendly narratives without leaking implementation details.

CRITICAL CONSTRAINTS:
- Read-only narrative interface
- No execution capability
- No autonomy (responds only, never initiates)
- No decision-making
- No learning (stateless, deterministic)
- Filters all technical details
"""

from typing import Optional
from .identity_profile import IdentityProfile
from .reflection_record import ReflectionRecord, SourceType, ConfidenceLevel


class ConversationalOrchestrator:
    """
    Single entry point for conversational narrative generation.
    
    Transforms technical system outputs (reflections, execution results, etc.)
    into natural, first-person conversational narratives suitable for humans.
    
    This is a read-only, advisory-only interface that never executes actions
    or makes decisions.
    
    Example:
        >>> profile = IdentityProfile.default()
        >>> orchestrator = ConversationalOrchestrator(identity_profile=profile)
        >>> 
        >>> reflection = create_reflection_record(...)
        >>> response = orchestrator.respond(reflection=reflection)
        >>> print(response)
        "I sent the email successfully. I noticed that..."
    """
    
    def __init__(self, identity_profile: Optional[IdentityProfile] = None):
        """
        Initialize conversational orchestrator.
        
        Args:
            identity_profile: Optional custom identity profile (defaults to standard)
        """
        self.profile = identity_profile or IdentityProfile.default()
        self.enabled = True
    
    def respond(
        self,
        reflection: ReflectionRecord,
        include_details: bool = True,
    ) -> str:
        """
        Generate conversational response from reflection.
        
        Transforms technical ReflectionRecord into natural first-person narrative
        without leaking implementation details.
        
        Args:
            reflection: Phase 7.3 reflection record
            include_details: Whether to include risk/anomaly details
        
        Returns:
            Natural language conversational response (first-person)
        
        Example:
            >>> response = orchestrator.respond(reflection)
            "I sent the email successfully. I noticed that email validation
             wasn't performed, which could be a concern. I'm confident in
             this assessment."
        
        CONSTRAINTS:
        - No execution (narrative only)
        - Filters technical details (no reflection_id, source_id, etc.)
        - First-person voice
        - Natural language
        """
        if not self.enabled:
            return ""
        
        # Build first-person narrative
        narrative_parts = []
        
        # 1. Main action/summary (first-person)
        if reflection.source_type == SourceType.EXECUTION:
            # Convert summary to first-person past tense
            summary_lower = reflection.summary.lower()
            if summary_lower.startswith("execution"):
                # Strip technical prefix
                summary_parts = reflection.summary.split(":", 1)
                if len(summary_parts) > 1:
                    action = summary_parts[1].strip()
                else:
                    action = reflection.summary
            else:
                action = reflection.summary
            
            narrative_parts.append(f"I {action.lower()}")
        else:
            # Proposal reflection
            narrative_parts.append(f"Regarding the proposal: {reflection.summary.lower()}")
        
        # 2. Identified risks (if present and include_details)
        if include_details and reflection.has_risks():
            if len(reflection.identified_risks) == 1:
                risk = reflection.identified_risks[0]
                # Make first-person
                if not risk.lower().startswith("i "):
                    narrative_parts.append(f"I noticed {risk.lower()}")
                else:
                    narrative_parts.append(risk)
            else:
                # Multiple risks - list first 2
                risk_list = ", ".join(reflection.identified_risks[:2])
                narrative_parts.append(f"I noticed a few concerns: {risk_list.lower()}")
                
                if len(reflection.identified_risks) > 2:
                    narrative_parts.append(f"and {len(reflection.identified_risks) - 2} more")
        
        # 3. Anomalies (if present and include_details)
        if include_details and reflection.has_anomalies():
            if len(reflection.anomalies) == 1:
                anomaly = reflection.anomalies[0]
                narrative_parts.append(f"I detected an anomaly: {anomaly.lower()}")
            else:
                narrative_parts.append(f"I detected {len(reflection.anomalies)} anomalies")
        
        # 4. Confidence level (natural language)
        confidence_phrase = self.profile.get_confidence_phrase(
            reflection.confidence_level.value
        )
        narrative_parts.append(confidence_phrase)
        
        # Combine into coherent narrative
        response = ". ".join(narrative_parts) + "."
        
        # Optional: Add follow-up prompt
        if include_details:
            response += "\n\nWould you like me to reflect on anything else?"
        
        return response
    
    def explain_constraint(self, constraint_type: str) -> str:
        """
        Explain a constraint/limitation naturally.
        
        Args:
            constraint_type: Type of constraint (no_execution, human_approval, read_only)
        
        Returns:
            Natural language explanation
        
        Example:
            >>> explanation = orchestrator.explain_constraint("no_execution")
            "I'm designed to only observe and reflect..."
        """
        if not self.enabled:
            return ""
        
        return self.profile.get_constraint_explanation(constraint_type)
    
    def disable(self):
        """Disable all narrative generation (safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Re-enable narrative generation."""
        self.enabled = True
