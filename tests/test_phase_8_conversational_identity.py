"""Phase 8: Conversational Identity Layer - Comprehensive Test Suite

Tests all four core components of Phase 8:
- IdentityProfile: Immutable identity definition
- NarrativeFormatter: Stateless technical → natural language transformation
- ResponseComposer: Coherent multi-part response composition
- ConversationalOrchestrator: Coordinated narrative workflow

Safety Verification:
- No execution capability
- No autonomy (responds only, never initiates)
- No decision-making
- No learning or memory mutation
- No technical leakage (filters internal details)
- Read-only narrative interface only
"""

import pytest
from datetime import datetime
from jessica.execution import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
    create_reflection_record,
)


# ============================================================================
# Mock Phase 8 Components (For Testing Design)
# ============================================================================
# Note: These are test mocks. Actual implementation will be in jessica/conversation/


from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


@dataclass(frozen=True)
class IdentityProfile:
    """Immutable definition of Jessica's conversational identity."""
    
    name: str = "Jessica"
    voice_tone: str = "warm, honest, helpful, professional"
    perspective: str = "first-person"
    constraint_no_execution: str = "I'm designed to only observe and reflect, not execute actions directly."
    constraint_human_approval: str = "You'll need to approve and trigger any actions yourself."
    constraint_read_only: str = "I can only analyze what's already happened."
    
    def get_constraint_explanation(self, constraint_type: str) -> str:
        """Get explanation for a constraint type."""
        constraint_map = {
            "no_execution": self.constraint_no_execution,
            "human_approval": self.constraint_human_approval,
            "read_only": self.constraint_read_only,
        }
        return constraint_map.get(constraint_type, "I have certain limitations to ensure safety.")


class NarrativeFormatter:
    """Stateless formatter for technical → natural language."""
    
    def __init__(self, identity_profile: IdentityProfile):
        self.profile = identity_profile
        self.enabled = True
    
    def format_reflection(
        self,
        reflection: ReflectionRecord,
        filter_technical: bool = True,
    ) -> str:
        """Convert technical reflection to first-person narrative."""
        if not self.enabled:
            return ""
        
        # Build narrative without technical details
        narrative_parts = []
        
        # Main summary (first-person)
        if reflection.source_type == SourceType.EXECUTION:
            narrative_parts.append(f"I {reflection.summary.lower()}")
        else:
            narrative_parts.append(f"Regarding the proposal: {reflection.summary.lower()}")
        
        # Identified risks (first-person)
        if reflection.has_risks():
            if len(reflection.identified_risks) == 1:
                narrative_parts.append(f"I noticed {reflection.identified_risks[0].lower()}")
            else:
                risk_list = ", ".join(reflection.identified_risks[:2])  # Limit for brevity
                narrative_parts.append(f"I noticed a few concerns: {risk_list.lower()}")
        
        # Confidence level (first-person)
        confidence_phrases = {
            ConfidenceLevel.HIGH: "I'm confident in this assessment",
            ConfidenceLevel.MEDIUM: "I'm fairly certain about this",
            ConfidenceLevel.LOW: "I'm uncertain, but it seems",
        }
        narrative_parts.append(confidence_phrases[reflection.confidence_level])
        
        return ". ".join(narrative_parts) + "."
    
    def format_constraint(
        self,
        constraint_type: str,
        context: Optional[Dict] = None,
    ) -> str:
        """Explain a constraint/limitation naturally."""
        if not self.enabled:
            return ""
        
        return self.profile.get_constraint_explanation(constraint_type)
    
    def format_error(
        self,
        error: str,
        context: Optional[Dict] = None,
    ) -> str:
        """Convert technical error to helpful explanation."""
        if not self.enabled:
            return ""
        
        # Simple error formatting with technical term filtering
        if "required" in error.lower():
            return "I couldn't process that request because some required information was missing. Could you provide more details?"
        elif "disabled" in error.lower():
            return "That capability is currently disabled."
        elif "validation" in error.lower():
            return "I couldn't validate that input. Please check the information and try again."
        elif "exception" in error.lower() or "error" in error.lower():
            return "I encountered an unexpected issue while processing that request."
        elif "timeout" in error.lower() or "connection" in error.lower():
            return "I had trouble connecting. Could you try again?"
        else:
            # Generic fallback (still filter technical details)
            return "I encountered an issue while processing your request."
    
    def disable(self):
        """Disable formatter."""
        self.enabled = False
    
    def enable(self):
        """Enable formatter."""
        self.enabled = True


class ResponseComposer:
    """Stateless composer for coherent multi-part responses."""
    
    def __init__(self, identity_profile: IdentityProfile):
        self.profile = identity_profile
        self.enabled = True
    
    def compose_reflection_response(
        self,
        narrative: str,
        include_metadata: bool = False,
    ) -> str:
        """Compose complete response from narrative."""
        if not self.enabled:
            return ""
        
        response_parts = [narrative]
        
        if include_metadata:
            response_parts.append("(This is my observation from what I've seen)")
        
        # Optional follow-up prompt
        response_parts.append("Would you like me to reflect on anything else?")
        
        return "\n\n".join(response_parts)
    
    def compose_multi_part_response(
        self,
        narratives: List[str],
        context: Optional[str] = None,
    ) -> str:
        """Compose response from multiple narratives."""
        if not self.enabled:
            return ""
        
        if not narratives:
            return ""
        
        # Add context if provided
        response_parts = []
        if context:
            response_parts.append(context)
        
        # Add narratives with transitions
        for i, narrative in enumerate(narratives):
            if i == 0:
                response_parts.append(narrative)
            elif i == len(narratives) - 1:
                response_parts.append(f"Finally, {narrative}")
            else:
                response_parts.append(f"Additionally, {narrative}")
        
        return "\n\n".join(response_parts)
    
    def compose_capability_explanation(
        self,
        capability: str,
        can_do: List[str],
        cannot_do: List[str],
    ) -> str:
        """Explain what Jessica can/cannot do naturally."""
        if not self.enabled:
            return ""
        
        response_parts = []
        
        # What I can do
        if can_do:
            can_list = ", ".join(can_do)
            response_parts.append(f"I can {can_list}.")
        
        # What I cannot do
        if cannot_do:
            cannot_list = ", ".join(cannot_do)
            response_parts.append(f"However, I'm designed to only observe—I can't {cannot_list}. You maintain full control.")
        
        return " ".join(response_parts)
    
    def disable(self):
        """Disable composer."""
        self.enabled = False
    
    def enable(self):
        """Enable composer."""
        self.enabled = True


class ConversationalOrchestrator:
    """Single entry point for conversational narrative interface."""
    
    def __init__(self, identity_profile: Optional[IdentityProfile] = None):
        self.profile = identity_profile or IdentityProfile()
        self.formatter = NarrativeFormatter(self.profile)
        self.composer = ResponseComposer(self.profile)
        self.enabled = True
    
    def narrate_reflection(
        self,
        reflection: ReflectionRecord,
        include_metadata: bool = False,
    ) -> str:
        """Convert reflection to natural conversational narrative."""
        if not self.enabled:
            return ""
        
        # Format reflection
        narrative = self.formatter.format_reflection(reflection)
        
        # Compose response
        response = self.composer.compose_reflection_response(
            narrative,
            include_metadata=include_metadata,
        )
        
        return response
    
    def explain_constraint(
        self,
        constraint_type: str,
        context: Optional[Dict] = None,
    ) -> str:
        """Explain a limitation or constraint naturally."""
        if not self.enabled:
            return ""
        
        return self.formatter.format_constraint(constraint_type, context)
    
    def respond_to_capability_question(
        self,
        can_do: List[str],
        cannot_do: List[str],
    ) -> str:
        """Answer questions about Jessica's capabilities."""
        if not self.enabled:
            return ""
        
        return self.composer.compose_capability_explanation(
            "general",
            can_do,
            cannot_do,
        )
    
    def narrate_multiple_reflections(
        self,
        reflections: List[ReflectionRecord],
        context: Optional[str] = None,
    ) -> str:
        """Narrate multiple reflections coherently."""
        if not self.enabled:
            return ""
        
        narratives = [
            self.formatter.format_reflection(r)
            for r in reflections
        ]
        
        return self.composer.compose_multi_part_response(narratives, context)
    
    def disable(self):
        """Disable all narrative generation."""
        self.enabled = False
        self.formatter.disable()
        self.composer.disable()
    
    def enable(self):
        """Re-enable narrative generation."""
        self.enabled = True
        self.formatter.enable()
        self.composer.enable()


# ============================================================================
# IdentityProfile Tests (Immutability)
# ============================================================================


def test_identity_profile_creation():
    """Test basic identity profile creation."""
    profile = IdentityProfile()
    
    assert profile.name == "Jessica"
    assert profile.perspective == "first-person"
    assert "observe" in profile.constraint_no_execution.lower()


def test_identity_profile_immutability():
    """Test that identity profile is truly immutable."""
    profile = IdentityProfile()
    
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        profile.name = "NewName"
    
    with pytest.raises(Exception):
        profile.voice_tone = "different tone"


def test_identity_profile_constraint_explanations():
    """Test constraint explanation retrieval."""
    profile = IdentityProfile()
    
    explanation = profile.get_constraint_explanation("no_execution")
    assert "observe" in explanation.lower() or "reflect" in explanation.lower()
    
    explanation = profile.get_constraint_explanation("human_approval")
    assert "approve" in explanation.lower() or "you" in explanation.lower()


def test_identity_profile_custom_values():
    """Test creating profile with custom values."""
    custom_profile = IdentityProfile(
        name="TestBot",
        voice_tone="formal",
    )
    
    assert custom_profile.name == "TestBot"
    assert custom_profile.voice_tone == "formal"


# ============================================================================
# NarrativeFormatter Tests (Stateless, Deterministic)
# ============================================================================


def test_formatter_reflection_formatting():
    """Test formatter converts reflection to narrative."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="sent email successfully",
        identified_risks=["No email validation performed"],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    narrative = formatter.format_reflection(reflection)
    
    # Should be first-person
    assert narrative.lower().startswith("i ")
    # Should mention the action
    assert "email" in narrative.lower()
    # Should mention risk
    assert "validation" in narrative.lower()
    # Should express confidence
    assert "confident" in narrative.lower()


def test_formatter_no_technical_leakage():
    """Test formatter filters technical details."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Action completed",
        identified_risks=[],
        confidence_level=ConfidenceLevel.MEDIUM,
    )
    
    narrative = formatter.format_reflection(reflection)
    
    # Should NOT contain technical terms
    assert "ReflectionRecord" not in narrative
    assert "exec_123" not in narrative
    assert "source_id" not in narrative
    assert "SourceType" not in narrative


def test_formatter_determinism():
    """Test formatter produces same output for same input."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test action",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    narrative1 = formatter.format_reflection(reflection)
    narrative2 = formatter.format_reflection(reflection)
    
    assert narrative1 == narrative2


def test_formatter_constraint_explanation():
    """Test formatter explains constraints naturally."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    explanation = formatter.format_constraint("no_execution")
    
    assert len(explanation) > 0
    assert "I" in explanation or "I'm" in explanation  # First-person
    assert "observe" in explanation.lower() or "reflect" in explanation.lower()


def test_formatter_error_formatting():
    """Test formatter converts errors to helpful messages."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    technical_error = "Validation failed: required field missing"
    helpful_message = formatter.format_error(technical_error)
    
    assert "I" in helpful_message  # First-person
    assert "couldn't" in helpful_message.lower() or "issue" in helpful_message.lower()


def test_formatter_disable_enable():
    """Test formatter safety switches."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    # Disable
    formatter.disable()
    narrative = formatter.format_reflection(reflection)
    assert narrative == ""
    
    # Re-enable
    formatter.enable()
    narrative = formatter.format_reflection(reflection)
    assert len(narrative) > 0


def test_formatter_stateless():
    """Test formatter has no state (stateless)."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    # Only profile and enabled flag should exist
    assert hasattr(formatter, 'profile')
    assert hasattr(formatter, 'enabled')
    
    # Should not have memory/learning attributes
    assert not hasattr(formatter, 'history')
    assert not hasattr(formatter, 'learned_patterns')
    assert not hasattr(formatter, 'conversation_state')


# ============================================================================
# ResponseComposer Tests (Coherent Multi-Part)
# ============================================================================


def test_composer_single_narrative():
    """Test composer composes single narrative response."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    narrative = "I completed the action successfully."
    response = composer.compose_reflection_response(narrative)
    
    assert narrative in response
    assert len(response) > len(narrative)  # Added context


def test_composer_multi_part_response():
    """Test composer creates coherent multi-part response."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    narratives = [
        "I sent the email successfully.",
        "I verified the recipient address.",
        "I logged the action.",
    ]
    
    response = composer.compose_multi_part_response(narratives)
    
    # All narratives should be present
    for narrative in narratives:
        assert narrative in response
    
    # Should have transitions
    assert "additionally" in response.lower() or "finally" in response.lower()


def test_composer_capability_explanation():
    """Test composer explains capabilities naturally."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    can_do = ["reflect on completed actions", "provide insights"]
    cannot_do = ["execute actions", "make decisions"]
    
    explanation = composer.compose_capability_explanation(
        "general",
        can_do,
        cannot_do,
    )
    
    assert "I can" in explanation
    assert "reflect" in explanation.lower()
    assert "can't" in explanation.lower() or "cannot" in explanation.lower()
    assert "execute" in explanation.lower()


def test_composer_metadata_inclusion():
    """Test composer includes metadata when requested."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    narrative = "I completed the action."
    
    # Without metadata
    response_no_meta = composer.compose_reflection_response(narrative, include_metadata=False)
    
    # With metadata
    response_with_meta = composer.compose_reflection_response(narrative, include_metadata=True)
    
    assert len(response_with_meta) > len(response_no_meta)
    assert "observation" in response_with_meta.lower() or "seen" in response_with_meta.lower()


def test_composer_disable_enable():
    """Test composer safety switches."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    narrative = "Test narrative"
    
    # Disable
    composer.disable()
    response = composer.compose_reflection_response(narrative)
    assert response == ""
    
    # Re-enable
    composer.enable()
    response = composer.compose_reflection_response(narrative)
    assert len(response) > 0


def test_composer_stateless():
    """Test composer has no state (stateless)."""
    profile = IdentityProfile()
    composer = ResponseComposer(profile)
    
    # Only profile and enabled flag should exist
    assert hasattr(composer, 'profile')
    assert hasattr(composer, 'enabled')
    
    # Should not have memory/learning attributes
    assert not hasattr(composer, 'history')
    assert not hasattr(composer, 'context_memory')


# ============================================================================
# ConversationalOrchestrator Tests (Workflow)
# ============================================================================


def test_orchestrator_narrate_reflection():
    """Test orchestrator complete reflection narration workflow."""
    orchestrator = ConversationalOrchestrator()
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="sent email successfully",
        identified_risks=["No validation"],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    narrative = orchestrator.narrate_reflection(reflection)
    
    assert len(narrative) > 0
    assert "i " in narrative.lower()  # First-person
    assert "email" in narrative.lower()


def test_orchestrator_explain_constraint():
    """Test orchestrator explains constraints naturally."""
    orchestrator = ConversationalOrchestrator()
    
    explanation = orchestrator.explain_constraint("no_execution")
    
    assert len(explanation) > 0
    assert "I" in explanation or "I'm" in explanation
    assert "observe" in explanation.lower() or "reflect" in explanation.lower()


def test_orchestrator_capability_question():
    """Test orchestrator answers capability questions."""
    orchestrator = ConversationalOrchestrator()
    
    response = orchestrator.respond_to_capability_question(
        can_do=["reflect on actions"],
        cannot_do=["execute actions"],
    )
    
    assert "I can" in response
    assert "reflect" in response.lower()
    assert "can't" in response.lower() or "cannot" in response.lower()


def test_orchestrator_multiple_reflections():
    """Test orchestrator narrates multiple reflections coherently."""
    orchestrator = ConversationalOrchestrator()
    
    reflections = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary=f"Action {i} completed",
            identified_risks=[],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(3)
    ]
    
    narrative = orchestrator.narrate_multiple_reflections(reflections)
    
    assert len(narrative) > 0
    # Should mention multiple actions
    assert "action 0" in narrative.lower() or "action 1" in narrative.lower()


def test_orchestrator_disable_enable():
    """Test orchestrator safety switches."""
    orchestrator = ConversationalOrchestrator()
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    # Disable
    orchestrator.disable()
    narrative = orchestrator.narrate_reflection(reflection)
    assert narrative == ""
    
    # Re-enable
    orchestrator.enable()
    narrative = orchestrator.narrate_reflection(reflection)
    assert len(narrative) > 0


def test_orchestrator_coordinates_formatter_and_composer():
    """Test orchestrator coordinates formatter and composer."""
    orchestrator = ConversationalOrchestrator()
    
    assert hasattr(orchestrator, 'formatter')
    assert hasattr(orchestrator, 'composer')
    assert isinstance(orchestrator.formatter, NarrativeFormatter)
    assert isinstance(orchestrator.composer, ResponseComposer)


def test_orchestrator_custom_profile():
    """Test orchestrator with custom identity profile."""
    custom_profile = IdentityProfile(name="TestBot")
    orchestrator = ConversationalOrchestrator(identity_profile=custom_profile)
    
    assert orchestrator.profile.name == "TestBot"


# ============================================================================
# Safety Constraint Verification
# ============================================================================


def test_no_execution_capability():
    """Verify conversational layer cannot execute actions."""
    orchestrator = ConversationalOrchestrator()
    
    # No execute methods
    assert not hasattr(orchestrator, 'execute')
    assert not hasattr(orchestrator, 'execute_action')
    assert not hasattr(orchestrator, 'run_action')
    assert not hasattr(orchestrator, 'perform_action')


def test_no_autonomy():
    """Verify conversational layer has no autonomy (responds only)."""
    orchestrator = ConversationalOrchestrator()
    
    # No initiate methods
    assert not hasattr(orchestrator, 'initiate_conversation')
    assert not hasattr(orchestrator, 'auto_respond')
    assert not hasattr(orchestrator, 'start_dialogue')
    assert not hasattr(orchestrator, 'proactive_message')


def test_no_decision_making():
    """Verify conversational layer cannot make decisions."""
    orchestrator = ConversationalOrchestrator()
    formatter = NarrativeFormatter(IdentityProfile())
    composer = ResponseComposer(IdentityProfile())
    
    # No decide/approve methods
    assert not hasattr(orchestrator, 'decide')
    assert not hasattr(orchestrator, 'approve')
    assert not hasattr(formatter, 'influence_decision')
    assert not hasattr(composer, 'recommend_action')


def test_no_learning_capability():
    """Verify conversational layer cannot learn or adapt."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    # Generate twice
    narrative1 = formatter.format_reflection(reflection)
    narrative2 = formatter.format_reflection(reflection)
    
    # Should be identical (no learning)
    assert narrative1 == narrative2


def test_no_technical_leakage_in_narratives():
    """Verify no technical details leak into narratives."""
    orchestrator = ConversationalOrchestrator()
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test action completed",
        identified_risks=["Risk 1"],
        confidence_level=ConfidenceLevel.MEDIUM,
    )
    
    narrative = orchestrator.narrate_reflection(reflection)
    
    # Should NOT contain technical terms
    assert "ReflectionRecord" not in narrative
    assert "Phase 7.3" not in narrative
    assert "Phase 8" not in narrative
    assert "exec_123" not in narrative
    assert "source_id" not in narrative
    assert "reflection_id" not in narrative
    assert "SourceType" not in narrative
    assert "ConfidenceLevel" not in narrative


def test_read_only_narrative_interface():
    """Verify conversational layer is read-only (no mutations)."""
    orchestrator = ConversationalOrchestrator()
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    # Narrate shouldn't modify reflection
    original_summary = reflection.summary
    narrative = orchestrator.narrate_reflection(reflection)
    
    assert reflection.summary == original_summary


def test_no_state_mutation():
    """Verify components don't mutate state (stateless)."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    composer = ResponseComposer(profile)
    
    # Create reflections
    reflection1 = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_1",
        summary="Action 1",
        identified_risks=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    reflection2 = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_2",
        summary="Action 2",
        identified_risks=[],
        confidence_level=ConfidenceLevel.LOW,
    )
    
    # Format both
    narrative1 = formatter.format_reflection(reflection1)
    narrative2 = formatter.format_reflection(reflection2)
    
    # Should be different (not influenced by state)
    assert narrative1 != narrative2
    assert "action 1" in narrative1.lower()
    assert "action 2" in narrative2.lower()


def test_no_background_processing():
    """Verify conversational layer has no background processing."""
    orchestrator = ConversationalOrchestrator()
    
    # No async/background methods
    assert not hasattr(orchestrator, 'start_background_narration')
    assert not hasattr(orchestrator, 'watch')
    assert not hasattr(orchestrator, 'monitor')
    assert not hasattr(orchestrator, 'continuous_narration')


def test_phase_8_no_autonomous_language():
    """Verify responses avoid autonomous/agentic language."""
    from jessica.execution import (
        IdentityProfile,
        ConversationalOrchestrator,
        create_reflection_record,
        SourceType,
        ConfidenceLevel,
    )
    
    forbidden_phrases = [
        "I decided",
        "I chose",
        "I will",
        "I plan to",
        "I executed",
        "I took action",
    ]
    
    profile = IdentityProfile.default()
    orchestrator = ConversationalOrchestrator(profile)
    
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="e1",
        summary="Settings updated",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.MEDIUM,
    )
    
    response = orchestrator.respond(reflection=reflection)
    
    for phrase in forbidden_phrases:
        assert phrase not in response


# ============================================================================
# Integration Tests
# ============================================================================


def test_phase_7_to_phase_8_integration():
    """Test Phase 7.3 reflection → Phase 8 narrative pipeline."""
    # Phase 7.3: Create reflection
    reflection = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="sent email to user@example.com",
        identified_risks=["No email validation"],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    # Phase 8: Convert to narrative
    orchestrator = ConversationalOrchestrator()
    narrative = orchestrator.narrate_reflection(reflection)
    
    # Verify transformation
    assert len(narrative) > 0
    assert "i " in narrative.lower()  # First-person
    assert "email" in narrative.lower()
    assert "ReflectionRecord" not in narrative  # No leakage


def test_consistent_voice_across_multiple_reflections():
    """Test consistent voice across multiple reflections."""
    orchestrator = ConversationalOrchestrator()
    
    reflections = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary=f"Action {i} completed",
            identified_risks=[],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(3)
    ]
    
    narratives = [
        orchestrator.narrate_reflection(r)
        for r in reflections
    ]
    
    # All should be first-person
    for narrative in narratives:
        assert "i " in narrative.lower() or "i'm" in narrative.lower()
    
    # All should have similar structure
    assert len(set(len(n.split()) for n in narratives)) <= 5  # Similar length


def test_error_handling_with_natural_language():
    """Test error messages are natural, not technical."""
    profile = IdentityProfile()
    formatter = NarrativeFormatter(profile)
    
    technical_errors = [
        "ValidationError: required field missing",
        "NullPointerException in module X",
        "Database connection timeout",
    ]
    
    for error in technical_errors:
        helpful_message = formatter.format_error(error)
        
        # Should be first-person and helpful
        assert "I" in helpful_message
        # Should not leak technical terms
        assert "ValidationError" not in helpful_message
        assert "NullPointerException" not in helpful_message


def test_phase_8_comprehensive_no_internal_leakage():
    """
    Comprehensive test: verify no internal technical terms leak into responses.
    
    This validates Phase 8's core constraint: never expose implementation details
    to humans. All responses must be natural, first-person narratives without
    technical jargon.
    """
    from jessica.execution import (
        IdentityProfile,
        ConversationalOrchestrator,
        create_reflection_record,
        SourceType,
        ConfidenceLevel,
    )
    
    forbidden_terms = [
        # Phase/implementation references
        "Phase",
        "Phase 7.3",
        "Phase 8",
        # Technical type names
        "ReflectionRecord",
        "SourceType",
        "ConfidenceLevel",
        "IdentityProfile",
        "ConversationalOrchestrator",
        # Internal IDs
        "execution_id",
        "proposal_id",
        "source_id",
        "reflection_id",
        # Python/implementation details
        "dataclass",
        "module",
        "orchestrator",
        "formatter",
        "composer",
        "jessica.execution",
        # Database/storage terms
        "registry",
        "factory",
        "analyzer",
    ]
    
    profile = IdentityProfile.default()
    orchestrator = ConversationalOrchestrator(profile)
    
    # Test with execution reflection
    reflection1 = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="e1",
        summary="Report generated successfully",
        identified_risks=["Missing approval step"],
        anomalies=[],
        confidence_level=ConfidenceLevel.MEDIUM,
        notes="Request approval before generating reports",
    )
    
    response1 = orchestrator.respond(reflection=reflection1)
    
    # Test with proposal reflection
    reflection2 = create_reflection_record(
        source_type=SourceType.PROPOSAL,
        source_id="p1",
        summary="File deletion requested",
        identified_risks=["Destructive action", "No backup"],
        anomalies=["High risk level"],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    response2 = orchestrator.respond(reflection=reflection2)
    
    # Check both responses for forbidden terms
    responses = [response1, response2]
    
    for i, response in enumerate(responses, 1):
        failed_terms = []
        for term in forbidden_terms:
            if term in response:
                failed_terms.append(term)
        
        assert not failed_terms, (
            f"Response {i} contains forbidden terms: {failed_terms}\n"
            f"Response: {response}"
        )
        
        # Verify it IS conversational (first-person)
        assert "I " in response or "I'm" in response, (
            f"Response {i} should be first-person. Got: {response}"
        )

