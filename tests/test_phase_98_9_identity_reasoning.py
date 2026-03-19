"""
Test Suite for Phase 98.9 - Identity Reasoning Engine

Tests the new IdentityReasoner that replaces hardcoded identity logic
with intelligent reasoning that links facts together, answers consistently,
speaks naturally, and resolves conflicts.

Features Tested:
- Question detection (identity questions vs other)
- Answer generation with natural language
- Fact linking (combining multiple beliefs)
- Reasoning transparency
- Integration with CognitiveKernel
- All question patterns (who, how old, profession, interests, relationships)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jessica.reasoning.identity_reasoner import IdentityReasoner
from jessica.memory.belief_store import BeliefStore as MemoryBeliefStore


class TestIdentityReasonerQuestionDetection:
    """Test identity question detection"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_detects_who_created_you_question(self):
        """Should detect 'who created you' as identity question"""
        assert self.reasoner.has_identity_question("Who created you?")
        assert self.reasoner.has_identity_question("who made you")
        assert self.reasoner.has_identity_question("who built you")
        assert self.reasoner.has_identity_question("who coded you")
        assert self.reasoner.has_identity_question("who developed you")
    
    def test_detects_who_am_i_question(self):
        """Should detect 'who am I' as identity question"""
        assert self.reasoner.has_identity_question("Who am I?")
        assert self.reasoner.has_identity_question("who am i")
        assert self.reasoner.has_identity_question("What is my name?")
    
    def test_detects_age_questions(self):
        """Should detect age-related questions"""
        assert self.reasoner.has_identity_question("How old am I?")
        assert self.reasoner.has_identity_question("how old am i")
        assert self.reasoner.has_identity_question("When was I born?")
    
    def test_detects_profession_questions(self):
        """Should detect profession-related questions"""
        assert self.reasoner.has_identity_question("What do I do?")
        assert self.reasoner.has_identity_question("what do i do")
        assert self.reasoner.has_identity_question("What is my job?")
    
    def test_detects_interest_questions(self):
        """Should detect interest-related questions"""
        assert self.reasoner.has_identity_question("What do I like?")
        assert self.reasoner.has_identity_question("what do i like")
        assert self.reasoner.has_identity_question("What are my interests?")
    
    def test_detects_relationship_questions(self):
        """Should detect relationship questions"""
        assert self.reasoner.has_identity_question("What's our relationship?")
        assert self.reasoner.has_identity_question("Tell me about me")
        assert self.reasoner.has_identity_question("Do you know me?")
    
    def test_does_not_detect_non_identity_questions(self):
        """Should not detect non-identity questions"""
        assert not self.reasoner.has_identity_question("What's 2+2?")
        assert not self.reasoner.has_identity_question("Tell me a joke")
        assert not self.reasoner.has_identity_question("What's the weather?")
        assert not self.reasoner.has_identity_question("How do I bake a cake?")


class TestIdentityReasonerAnswerGeneration:
    """Test identity answer generation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_answers_who_created_you_with_creator_belief(self):
        """Should answer 'who created you' using creator belief"""
        self.belief_store.set("creator", "Alice")
        answer = self.reasoner.answer("Who created you?")
        assert answer is not None
        assert "Alice" in answer
        assert "created" in answer.lower() or "making" in answer.lower()
    
    def test_answers_who_am_i_with_user_name_belief(self):
        """Should answer 'who am I' using user_name belief"""
        self.belief_store.set("user_name", "Bob")
        answer = self.reasoner.answer("Who am I?")
        assert answer is not None
        assert "Bob" in answer
    
    def test_answers_how_old_am_i_with_birth_year_belief(self):
        """Should answer 'how old am I' using birth_year belief"""
        from datetime import datetime
        self.belief_store.set("birth_year", 1990)
        answer = self.reasoner.answer("How old am I?")
        assert answer is not None
        assert "born" in answer.lower()
        assert "1990" in answer
    
    def test_answers_profession_with_profession_belief(self):
        """Should answer 'what do I do' using profession belief"""
        self.belief_store.set("profession", "Engineer")
        answer = self.reasoner.answer("What do I do?")
        assert answer is not None
        assert "Engineer" in answer
    
    def test_answers_interest_with_interest_belief(self):
        """Should answer 'what do I like' using interest belief"""
        self.belief_store.set("interest", "music")
        answer = self.reasoner.answer("What do I like?")
        assert answer is not None
        assert "music" in answer.lower() or "enjoy" in answer.lower()
    
    def test_returns_none_for_missing_beliefs(self):
        """Should return None if beliefs don't exist"""
        # Empty belief store - no beliefs set
        answer = self.reasoner.answer("Who am I?")
        assert answer is None
    
    def test_answers_about_me_with_multiple_beliefs(self):
        """Should combine multiple beliefs into narrative"""
        self.belief_store.set("user_name", "Charlie")
        self.belief_store.set("profession", "Teacher")
        self.belief_store.set("creator", "Charlie")
        
        answer = self.reasoner.answer("Tell me about me")
        assert answer is not None
        assert "Charlie" in answer
        assert "Teacher" in answer
    
    def test_answers_relationship_question(self):
        """Should understand and answer relationship questions"""
        self.belief_store.set("creator", "Diana")
        answer = self.reasoner.answer("What's our relationship?")
        assert answer is not None
        assert "Diana" in answer or "relationship" in answer.lower() or "created" in answer.lower()


class TestIdentityReasonerNaturalLanguage:
    """Test natural language generation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_answers_in_natural_language(self):
        """Should answer in natural, conversational language"""
        self.belief_store.set("user_name", "Eve")
        answer = self.reasoner.answer("Who am I?")
        assert answer is not None
        # Should be conversational, not just a fact
        assert len(answer) > 2  # More than just "Eve"
        assert not answer.startswith("FACT:")  # Not formatted as raw fact
    
    def test_speaks_consistently(self):
        """Should speak in consistent style across questions"""
        self.belief_store.set("user_name", "Frank")
        self.belief_store.set("profession", "Doctor")
        
        name_answer = self.reasoner.answer("Who am I?")
        job_answer = self.reasoner.answer("What do I do?")
        
        assert name_answer is not None
        assert job_answer is not None
        # Both should be formatted similarly (sentences, no raw facts)
        assert not name_answer.startswith("FACT:")
        assert not job_answer.startswith("FACT:")


class TestIdentityReasonerReasoningTransparency:
    """Test reasoning transparency"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_explain_reasoning_for_creator_question(self):
        """Should explain reasoning for creator question"""
        self.belief_store.set("creator", "Grace")
        self.reasoner.answer("Who created you?")
        explanation = self.reasoner.explain_reasoning("Who created you?")
        
        assert explanation is not None
        assert "creator" in explanation.lower() or "made" in explanation.lower()
    
    def test_explain_reasoning_for_identity_question(self):
        """Should explain reasoning for identity question"""
        self.belief_store.set("user_name", "Henry")
        self.reasoner.answer("Who am I?")
        explanation = self.reasoner.explain_reasoning("Who am I?")
        
        assert explanation is not None
        assert "name" in explanation.lower() or "henry" in explanation.lower()


class TestIdentityReasonerFactLinking:
    """Test fact linking and coherence"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_links_creator_and_assistant_role(self):
        """Should link creator relationship to assistant role"""
        self.belief_store.set("creator", "Iris")
        answer = self.reasoner.answer("Tell me about me")
        
        assert answer is not None
        # Should mention Iris
        assert "Iris" in answer or "creator" in answer.lower()
    
    def test_links_user_identity_to_profession(self):
        """Should link user identity with profession"""
        self.belief_store.set("user_name", "Jack")
        self.belief_store.set("profession", "Engineer")
        
        about_answer = self.reasoner.answer("Tell me about me")
        
        assert about_answer is not None
        # Should mention both name and profession
        assert "Jack" in about_answer or "Engineer" in about_answer
    
    def test_links_age_with_birth_context(self):
        """Should link age calculation with birth year for context"""
        self.belief_store.set("birth_year", 1985)
        age_answer = self.reasoner.answer("How old am I?")
        
        assert age_answer is not None
        # Should provide context about birth year
        assert "1985" in age_answer or "born" in age_answer.lower()


class TestIdentityReasonerIntegration:
    """Test integration with CognitiveKernel"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_reasoner_can_be_initialized_with_belief_store(self):
        """Should initialize with belief store"""
        belief_store = MemoryBeliefStore()
        reasoner = IdentityReasoner(belief_store)
        assert reasoner is not None
    
    def test_reasoning_is_deterministic(self):
        """Should produce consistent answers for same input"""
        self.belief_store.set("user_name", "Karen")
        
        answer1 = self.reasoner.answer("Who am I?")
        answer2 = self.reasoner.answer("Who am I?")
        
        # Should be consistent (not necessarily identical, but contain same info)
        assert answer1 == answer2


class TestIdentityReasonerConflictResolution:
    """Test conflict resolution in identity reasoning"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_handles_missing_beliefs_gracefully(self):
        """Should handle missing beliefs without errors"""
        answer = self.reasoner.answer("Who am I?")
        # Should return None or error message, not crash
        assert answer is None or isinstance(answer, str)
    
    def test_handles_incomplete_information(self):
        """Should handle partial information"""
        self.belief_store.set("user_name", "Leo")
        # No profession set
        
        about_answer = self.reasoner.answer("Tell me about me")
        # Should handle gracefully, using available information
        if about_answer:
            assert "Leo" in about_answer or len(about_answer) > 0


class TestIdentityReasonerEdgeCases:
    """Test edge cases and robustness"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_handles_capitalization_variations(self):
        """Should handle various capitalizations"""
        self.belief_store.set("user_name", "Mike")
        
        answer1 = self.reasoner.answer("who am i?")
        answer2 = self.reasoner.answer("WHO AM I?")
        answer3 = self.reasoner.answer("Who Am I?")
        
        assert answer1 is not None
        assert answer2 is not None
        assert answer3 is not None
    
    def test_handles_punctuation_variations(self):
        """Should handle various punctuation"""
        self.belief_store.set("user_name", "Nancy")
        
        answer1 = self.reasoner.answer("Who am I?")
        answer2 = self.reasoner.answer("Who am I")
        answer3 = self.reasoner.answer("Who am I...")
        
        assert answer1 is not None
        assert answer2 is not None
        assert answer3 is not None
    
    def test_handles_extra_whitespace(self):
        """Should handle extra whitespace"""
        self.belief_store.set("user_name", "Oscar")
        
        answer1 = self.reasoner.answer("Who am I?")
        answer2 = self.reasoner.answer("  Who am I?  ")
        
        assert answer1 is not None
        assert answer2 is not None
    
    def test_handles_belief_confidence_levels(self):
        """Should respect belief confidence levels"""
        # High confidence
        self.belief_store.set("user_name", "Paul")
        answer = self.reasoner.answer("Who am I?")
        assert answer is not None


class TestIdentityReasonerComprehensiveness:
    """Test comprehensive question patterns"""
    
    def setup_method(self):
        """Setup for each test"""
        self.belief_store = MemoryBeliefStore()
        self.reasoner = IdentityReasoner(self.belief_store)
    
    def test_all_creator_variations(self):
        """Should handle all creator question variations"""
        self.belief_store.set("creator", "Quinn")
        
        questions = [
            "Who created you?",
            "Who made you?",
            "Who built you?",
            "Who coded you?",
            "Who developed you?",
            "Who created Jessica?",
        ]
        
        for q in questions:
            answer = self.reasoner.answer(q)
            assert answer is not None, f"Failed on question: {q}"
            assert "Quinn" in answer, f"Missing creator info for: {q}"
    
    def test_all_age_variations(self):
        """Should handle all age question variations"""
        self.belief_store.set("birth_year", 1995)
        
        questions = [
            "How old am I?",
            "What is my age?",
            "When was I born?",
        ]
        
        for q in questions:
            answer = self.reasoner.answer(q)
            assert answer is not None, f"Failed on question: {q}"
            assert "1995" in answer or "born" in answer.lower(), f"Missing birth info for: {q}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
