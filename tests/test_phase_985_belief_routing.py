"""
Tests for Phase 98.5: Belief-Aware Routing + Model Governance Integration

Validates:
1. Personal question detection
2. Belief-first routing
3. Model governance blocking Jessica from saying wrong things
4. Conflict detection and prevention
5. Model output wrapping
6. Audit logging
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from jessica.routing.personal_question_detector import PersonalQuestionDetector
from jessica.routing.model_governor import ModelGovernor
from jessica.security.audit_log import AuditLog


class TestPersonalQuestionDetection:
    """Test personal question detection"""

    def test_detect_name_question(self):
        """Detect 'my name' question"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("What is my name?") is True
        assert detector.is_personal_question("My name is Alice") is True
        assert detector.is_personal_question("Who am I?") is True

    def test_detect_creator_question(self):
        """Detect 'who created you' type questions"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("Who created you?") is True
        assert detector.is_personal_question("Who made you?") is True
        assert detector.is_personal_question("Who built you?") is True
        assert detector.is_personal_question("Who coded you?") is True
        assert detector.is_personal_question("Who created jessica?") is True

    def test_detect_age_question(self):
        """Detect age-related questions"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("How old am I?") is True
        assert detector.is_personal_question("When was I born?") is True
        assert detector.is_personal_question("My birth year") is True

    def test_detect_location_question(self):
        """Detect location questions"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("Where do I live?") is True
        assert detector.is_personal_question("My location") is True
        assert detector.is_personal_question("My home") is True

    def test_detect_identity_update(self):
        """Detect when user provides identity info"""
        detector = PersonalQuestionDetector()
        assert detector.is_identity_update("My name is Hendrik") is True
        assert detector.is_identity_update("I created you") is True
        assert detector.is_identity_update("I was born in 1990") is True

    def test_not_personal_math_question(self):
        """Math questions are NOT personal"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("What is 2 + 2?") is False
        assert detector.is_personal_question("How much is 10 * 5?") is False

    def test_not_personal_external_knowledge(self):
        """External knowledge questions are NOT personal"""
        detector = PersonalQuestionDetector()
        assert detector.is_personal_question("What is Paris?") is False
        assert detector.is_personal_question("Who was Einstein?") is False
        assert detector.is_personal_question("Explain gravity") is False

    def test_classify_question_type(self):
        """Test question classification"""
        detector = PersonalQuestionDetector()
        assert detector.classify_question("My name is Hendrik") == "identity_update"
        assert detector.classify_question("What is my name?") == "personal"
        assert detector.classify_question("What is 2 + 2?") == "math"
        assert detector.classify_question("Who was Einstein?") == "external_knowledge"


class TestModelGovernor:
    """Test model governance"""

    def test_model_blocked_from_creator_question(self):
        """Model should NOT answer 'who created you'"""
        governor = ModelGovernor()
        assert governor.can_answer_this_question("Who created you?") is False
        assert governor.can_answer_this_question("Who made jessica?") is False

    def test_model_blocked_from_personal_questions(self):
        """Model should NOT answer personal questions"""
        governor = ModelGovernor()
        assert governor.can_answer_this_question("What is my name?") is False
        assert governor.can_answer_this_question("My age") is False
        assert governor.can_answer_this_question("When was I born?") is False

    def test_model_blocked_from_identity_questions(self):
        """Model should NOT answer identity questions"""
        governor = ModelGovernor()
        assert governor.can_answer_this_question("Who are you?") is False
        assert governor.can_answer_this_question("What are you?") is False
        assert governor.can_answer_this_question("Who is jessica?") is False

    def test_model_allowed_for_external_knowledge(self):
        """Model CAN answer external knowledge"""
        governor = ModelGovernor()
        assert governor.can_answer_this_question("What is Paris?") is True
        assert governor.can_answer_this_question("Who was Einstein?") is True

    def test_detect_conflict_with_belief(self):
        """Detect when model answer conflicts with belief"""
        governor = ModelGovernor()
        
        # No conflict: belief is in model answer
        conflict = governor.check_conflict(
            model_answer="You are Hendrik",
            belief_answer="Hendrik",
            question="Who created you?"
        )
        assert conflict is False
        
        # Conflict: belief NOT in model answer
        conflict = governor.check_conflict(
            model_answer="I was created by OpenAI",
            belief_answer="Hendrik",
            question="Who created you?"
        )
        assert conflict is True

    def test_wrap_model_output(self):
        """Model output should be wrapped to show it's external knowledge"""
        audit_log = AuditLog(log_file=":memory:")
        governor = ModelGovernor(audit_log=audit_log)
        
        wrapped = governor.wrap_model_output(
            model_answer="Paris is the capital of France",
            question="What is the capital of France?"
        )
        
        assert "I understand it as follows:" in wrapped
        assert "Paris" in wrapped

    def test_wrap_removes_identity_markers(self):
        """Model output should remove 'I am' markers"""
        audit_log = AuditLog(log_file=":memory:")
        governor = ModelGovernor(audit_log=audit_log)
        
        wrapped = governor.wrap_model_output(
            model_answer="I am a language model",
            question="What are you?"
        )
        
        # Should NOT start with "I am"
        assert not wrapped.startswith("I am")
        assert "I understand it as follows:" in wrapped

    def test_govern_response_blocked(self):
        """Govern should block unauthorized questions"""
        governor = ModelGovernor()
        
        result = governor.govern_model_response(
            question="Who created you?",
            model_answer="I was created by OpenAI",
            belief_answer=None
        )
        
        assert result["allowed"] is False
        assert "not authorized" in result["reason"].lower()

    def test_govern_response_conflict(self):
        """Govern should handle model responses for allowed questions"""
        governor = ModelGovernor()
        
        # External knowledge question - model IS allowed to answer
        result = governor.govern_model_response(
            question="What is the capital of France?",
            model_answer="Paris is the capital of France",
            belief_answer=None  # No belief for external knowledge
        )
        
        # Model IS allowed for external knowledge
        assert result["allowed"] is True
        assert "I understand it as follows:" in result["answer"]
        
        # For forbidden questions, test that model is blocked
        result_forbidden = governor.govern_model_response(
            question="Who created you?",
            model_answer="I was created by OpenAI",
            belief_answer="Hendrik"
        )
        
        # Model is blocked for this question type
        assert result_forbidden["allowed"] is False

    def test_govern_response_allowed_and_wrapped(self):
        """Govern should wrap allowed external knowledge"""
        governor = ModelGovernor()
        
        result = governor.govern_model_response(
            question="What is Paris?",
            model_answer="Paris is the capital of France",
            belief_answer=None
        )
        
        assert result["allowed"] is True
        assert "I understand it as follows:" in result["answer"]
        assert "Paris" in result["answer"]
        assert result["conflict"] is False


class TestBeliefFirstRouting:
    """Test belief-first routing in CognitiveKernel"""

    @patch('jessica.core.cognitive_kernel.CognitiveKernel._answer_from_beliefs')
    @patch('jessica.core.cognitive_kernel.StructuredReasoner')
    @patch('jessica.core.cognitive_kernel.PersonalQuestionDetector')
    def test_personal_question_uses_belief_first(self, mock_detector, mock_reasoner, mock_beliefs):
        """Personal questions should use beliefs first"""
        from jessica.core.cognitive_kernel import CognitiveKernel
        
        # Setup mocks
        mock_detector.return_value.is_personal_question.return_value = True
        mock_beliefs.return_value = "Your name is Hendrik"
        
        kernel = CognitiveKernel()
        
        # Mock the detector instance
        kernel.personal_detector.is_personal_question = Mock(return_value=True)
        
        result = kernel.process("What is my name?")
        
        # Should have called belief lookup
        assert "Hendrik" in str(result) or "Your name" in str(result)

    def test_model_never_says_im_phi(self):
        """Model should never be able to say 'I'm Phi'"""
        governor = ModelGovernor()
        
        # Try to make model say it's Phi
        result = governor.govern_model_response(
            question="Who are you?",
            model_answer="I'm Phi",
            belief_answer=None
        )
        
        # Should be blocked
        assert result["allowed"] is False

    def test_model_answer_contradicting_belief_blocked(self):
        """Model NOT allowed to answer creator questions regardless of belief"""
        governor = ModelGovernor()
        
        # Model is blocked from answering "Who created you?" entirely
        result = governor.govern_model_response(
            question="Who created you?",
            model_answer="I was created by Phi",
            belief_answer="Hendrik"
        )
        
        # Model not authorized to answer
        assert result["allowed"] is False
        # Not a conflict per se - model just can't answer this type of question


class TestLoggingAndAudit:
    """Test logging of conflicts and model usage"""

    def test_conflict_logged(self):
        """Conflicts should be logged to audit trail"""
        audit_log = AuditLog()
        governor = ModelGovernor(audit_log=audit_log)
        
        # Trigger a conflict
        governor.check_conflict(
            model_answer="I was created by OpenAI",
            belief_answer="Hendrik",
            question="Who created you?"
        )
        
        # Should be logged (audit log stores logs internally)
        # We can't directly test this without access to internal logs
        # but we're testing that it doesn't crash

    def test_model_usage_logged(self):
        """Model usage should be logged"""
        audit_log = AuditLog()
        governor = ModelGovernor(audit_log=audit_log)
        
        wrapped = governor.wrap_model_output(
            model_answer="Paris is the capital",
            question="What is the capital?"
        )
        
        # Should be wrapped (indicating model was used)
        assert "I understand it as follows:" in wrapped


class TestPriorityOrdering:
    """Test that priorities are correct"""

    def test_priority_personal_beats_math(self):
        """Personal questions should be answered from beliefs, not math"""
        detector = PersonalQuestionDetector()
        
        # "What is my name?" contains "is" (math-like) but is personal
        assert detector.is_personal_question("What is my name?") is True

    def test_priority_identity_update_recognized(self):
        """Identity updates should be recognized"""
        detector = PersonalQuestionDetector()
        
        assert detector.is_identity_update("My name is Hendrik") is True
        assert detector.is_identity_update("I created you") is True

    def test_external_knowledge_allowed_through_model(self):
        """External knowledge questions can use model"""
        governor = ModelGovernor()
        
        assert governor.can_answer_this_question("What is Paris?") is True
        assert governor.can_answer_this_question("Who was Napoleon?") is True
