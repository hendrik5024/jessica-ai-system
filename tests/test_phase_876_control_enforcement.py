"""
Phase 87.6: Cognitive Control Enforcement Tests

Ensures Jessica ALWAYS reasons first before calling model.
Model is STRICTLY fallback only.
"""

import pytest
from pathlib import Path
from jessica.core.knowledge_store import KnowledgeStore
from jessica.core.reasoning_engine import ReasoningEngine
from jessica.core.cognitive_controller import CognitiveController
from jessica.core.cognitive_kernel import CognitiveKernel


@pytest.fixture(autouse=True)
def clear_memory():
    """Clear persistent memory before each test."""
    memory_file = Path("jessica_memory.json")
    beliefs_file = Path("jessica/data/beliefs.json")
    permissions_file = Path("jessica/config/permissions.json")
    
    # Clean before
    for f in [memory_file, beliefs_file, permissions_file]:
        if f.exists():
            f.unlink()
    
    yield
    
    # Clean after
    for f in [memory_file, beliefs_file, permissions_file]:
        if f.exists():
            f.unlink()


class TestBirthYearStorage:
    """Test birth year storage with immediate response."""

    def test_birth_year_storage_returns_confirmation(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("I was born in 1975")
        assert result == "I will remember your birth information."
        assert store.get_birth_year() == 1975

    def test_birth_year_storage_various_formats(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Test "born in"
        result = controller.process("I was born in 1985")
        assert "remember" in result.lower()
        assert store.get_birth_year() == 1985


class TestBirthYearRecall:
    """Test birth year recall without model."""

    def test_resolve_birth_year_with_stored_year(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        engine = ReasoningEngine()
        result = engine.resolve_birth_year(store)
        assert result == "You were born in 1975."

    def test_resolve_birth_year_without_stored_year(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        result = engine.resolve_birth_year(store)
        assert result is None

    def test_birth_year_query_when_was_i_born(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("When was I born?")
        assert result == "You were born in 1975."

    def test_birth_year_query_what_year_was_i_born(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1985)
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("What year was I born?")
        assert result == "You were born in 1985."

    def test_birth_year_unknown(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("When was I born?")
        assert result == "I do not know your birth year yet."


class TestAgeQuestions:
    """Test age question handling."""

    def test_jessica_age_question(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("How old are you?")
        assert result == "I do not have an age like a human. I am a cognitive system."

    def test_user_age_question(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        result = controller.process("How old am I?")
        assert "years old" in result


class TestModelGate:
    """Test strict model gate prevents unnecessary model calls."""

    def test_model_blocked_for_name_query(self):
        """Model should NOT be called for name queries."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        # Mock model that should NOT be called
        class MockLLM:
            def __init__(self):
                self.called = False
            
            def generate(self, prompt, **kwargs):
                self.called = True
                return "This should not appear"
        
        mock_llm = MockLLM()
        controller = CognitiveController(store, engine, mock_llm)
        
        # Query without stored name - should NOT call model
        result = controller.process("What is my name?")
        assert mock_llm.called is False
        assert "do not know" in result.lower()

    def test_model_blocked_for_age_query(self):
        """Model should NOT be called for age queries."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        class MockLLM:
            def __init__(self):
                self.called = False
            
            def generate(self, prompt, **kwargs):
                self.called = True
                return "This should not appear"
        
        mock_llm = MockLLM()
        controller = CognitiveController(store, engine, mock_llm)
        
        result = controller.process("How old are you?")
        assert mock_llm.called is False
        assert "cognitive system" in result

    def test_model_blocked_for_identity_query(self):
        """Model should NOT be called for identity queries."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        class MockLLM:
            def __init__(self):
                self.called = False
            
            def generate(self, prompt, **kwargs):
                self.called = True
                return "This should not appear"
        
        mock_llm = MockLLM()
        controller = CognitiveController(store, engine, mock_llm)
        
        result = controller.process("What are you?")
        assert mock_llm.called is False
        assert "Jessica" in result

    def test_model_allowed_for_knowledge_query(self):
        """Model SHOULD be called for knowledge queries."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        class MockLLM:
            def __init__(self):
                self.called = False
            
            def generate(self, prompt, **kwargs):
                self.called = True
                return "Paris is the capital of France."
        
        mock_llm = MockLLM()
        controller = CognitiveController(store, engine, mock_llm)
        
        result = controller.process("What is the capital of France?")
        assert mock_llm.called is True
        assert "Paris" in result


class TestModelWrapper:
    """Test that model output is clean without wrapper."""

    def test_model_response_no_wrapper(self):
        """Model response should NOT have 'I understand this as follows:' prefix."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        class MockLLM:
            def generate(self, prompt, **kwargs):
                return "The Earth orbits the Sun."
        
        controller = CognitiveController(store, engine, MockLLM())
        result = controller.process("Does the Earth orbit the Sun?")
        
        # Should NOT have wrapper
        assert "I understand this as follows:" not in result
        # Should have clean response
        assert "The Earth orbits the Sun." in result

    def test_model_identity_leak_blocked(self):
        """Identity leaks should still be blocked."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        class MockLLM:
            def generate(self, prompt, **kwargs):
                return "I am Phi, a language model."
        
        controller = CognitiveController(store, engine, MockLLM())
        result = controller.process("What is gravity?")
        
        # Should block and return identity override
        assert result == "I am Jessica."


class TestPhase876Integration:
    """End-to-end integration tests."""

    def test_full_flow_birth_year_storage_and_recall(self):
        kernel = CognitiveKernel(llm=None)
        
        # Store birth year
        result = kernel.process("I was born in 1975")
        assert "I will remember your birth information." in result
        
        # Recall birth year
        result = kernel.process("When was I born?")
        assert result == "You were born in 1975."

    def test_jessica_age_vs_user_age(self):
        kernel = CognitiveKernel(llm=None)
        
        # Jessica's age
        result = kernel.process("How old are you?")
        assert "cognitive system" in result
        
        # User's age (with birth year)
        kernel.process("I was born in 1975")
        result = kernel.process("How old am I?")
        assert "years old" in result

    def test_reasoning_before_model(self):
        """Jessica must reason first, model only for knowledge."""
        kernel = CognitiveKernel(llm=None)
        
        # Name query: direct answer (no model)
        result = kernel.process("What is my name?")
        assert "do not know" in result.lower()
        
        # Identity query: direct answer (no model)
        result = kernel.process("What is your name?")
        assert result == "My name is Jessica."
        
        # Math query: direct answer (no model)
        result = kernel.process("What is 5 + 5?")
        assert result == "The answer is 10."

    def test_model_gate_prevents_personal_queries(self):
        """Personal queries blocked from model."""
        
        class MockLLM:
            def __init__(self):
                self.call_count = 0
            
            def generate(self, prompt, **kwargs):
                self.call_count += 1
                return "Model response"
        
        mock_llm = MockLLM()
        kernel = CognitiveKernel(llm=mock_llm)
        
        # All these should NOT trigger model
        kernel.process("What is my name?")
        kernel.process("How old are you?")
        kernel.process("What are you?")
        kernel.process("Who created you?")
        
        # Model should NOT have been called
        assert mock_llm.call_count == 0

    def test_memory_consistency(self):
        """Memory should be consistent across queries."""
        kernel = CognitiveKernel(llm=None)
        
        # Store information
        kernel.process("My name is Alice")
        kernel.process("I was born in 1990")
        
        # Verify name persists
        result = kernel.process("What is my name?")
        assert result == "Your name is Alice."
        
        # Verify birth year persists
        result = kernel.process("When was I born?")
        assert result == "You were born in 1990."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
