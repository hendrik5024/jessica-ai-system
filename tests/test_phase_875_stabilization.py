"""
Phase 87.5: Core Cognitive Stabilization Tests

Test memory consistency, identity reasoning, and model dependency reduction.
"""

import pytest
from datetime import datetime
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


class TestKnowledgeStoreHelpers:
    """Test new helper methods."""

    def test_get_user_name(self):
        store = KnowledgeStore()
        store.set_fact("user.name", "Hendrik")
        assert store.get_user_name() == "Hendrik"

    def test_get_birth_year(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        assert store.get_birth_year() == 1975

    def test_get_birth_date(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_date", "1975-03-15")
        assert store.get_birth_date() == "1975-03-15"


class TestReasoningEngineEnhancements:
    """Test improved reasoning methods."""

    def test_resolve_age_with_birth_year(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        engine = ReasoningEngine()
        result = engine.resolve_age(store)
        current_year = datetime.now().year
        expected_age = current_year - 1975
        assert f"{expected_age}" in result

    def test_resolve_age_without_birth_year(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        result = engine.resolve_age(store)
        assert result is None

    def test_resolve_name_with_name(self):
        store = KnowledgeStore()
        store.set_fact("user.name", "Hendrik")
        engine = ReasoningEngine()
        result = engine.resolve_name(store)
        assert result == "Your name is Hendrik."

    def test_resolve_name_without_name(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        result = engine.resolve_name(store)
        assert result is None

    def test_resolve_identity_what_are_you(self):
        engine = ReasoningEngine()
        result = engine.resolve_identity("What are you?")
        assert "Jessica" in result
        assert "cognitive AI system" in result

    def test_resolve_identity_who_created_you(self):
        store = KnowledgeStore()
        store.set_fact("user.name", "Hendrik")
        engine = ReasoningEngine()
        result = engine.resolve_identity("Who created you?", store)
        assert result == "You created me, Hendrik."

    def test_resolve_identity_creator_unknown(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        result = engine.resolve_identity("Who created you?", store)
        assert result == "I was created by my developer."

    def test_resolve_identity_your_name(self):
        engine = ReasoningEngine()
        result = engine.resolve_identity("What is your name?")
        assert result == "My name is Jessica."


class TestCognitiveControllerMemoryExtraction:
    """Test memory capture from user input."""

    def test_extract_name(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        controller.process("My name is Alice")
        assert store.get_user_name() == "Alice"

    def test_extract_birth_year(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        controller.process("I was born in 1985")
        assert store.get_birth_year() == 1985

    def test_extract_name_titlecase(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        controller.process("my name is bob smith")
        assert store.get_user_name() == "Bob Smith"


class TestCognitiveControllerFlow:
    """Test complete processing flow and model dependency."""

    def test_name_recall_no_model_prefix(self):
        store = KnowledgeStore()
        store.set_fact("user.name", "Hendrik")
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine, None)
        result = controller.process("What is my name?")
        # Should NOT have "I understand this as follows:" prefix
        assert result == "Your name is Hendrik."
        assert "I understand this as follows:" not in result

    def test_age_recall_no_model_prefix(self):
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine, None)
        result = controller.process("How old am I?")
        current_year = datetime.now().year
        expected_age = current_year - 1975
        # Should NOT have wrapper prefix
        assert f"{expected_age}" in result
        assert "I understand this as follows:" not in result

    def test_identity_no_model_prefix(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine, None)
        result = controller.process("What is your name?")
        assert result == "My name is Jessica."
        assert "I understand this as follows:" not in result

    def test_model_fallback_has_prefix(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()

        # Mock LLM
        class MockLLM:
            def generate(self, prompt, **kwargs):
                return "Paris is the capital of France."

        controller = CognitiveController(store, engine, MockLLM())
        result = controller.process("What is the capital of France?")
        # Phase 87.6: No wrapper, clean response
        assert "Paris is the capital of France" in result
        # Wrapper should NOT be present (removed in Phase 87.6)
        assert "I understand this as follows:" not in result

    def test_model_blocks_identity_leak(self):
        store = KnowledgeStore()
        engine = ReasoningEngine()

        # Mock LLM returning identity leak
        class MockLLM:
            def generate(self, prompt, **kwargs):
                return "I am Phi, a language model."

        controller = CognitiveController(store, engine, MockLLM())
        result = controller.process("Who are you?")
        # Should block and return identity override
        assert result == "I am Jessica."


class TestPhase875Integration:
    """End-to-end integration tests."""

    def test_full_flow_name_storage_and_recall(self):
        kernel = CognitiveKernel(llm=None)
        kernel.process("My name is Hendrik")
        result = kernel.process("What is my name?")
        assert result == "Your name is Hendrik."

    def test_full_flow_birth_year_and_age(self):
        kernel = CognitiveKernel(llm=None)
        kernel.process("I was born in 1975")
        result = kernel.process("How old am I?")
        current_year = datetime.now().year
        expected_age = current_year - 1975
        assert f"{expected_age}" in result

    def test_full_flow_identity_knowledge(self):
        kernel = CognitiveKernel(llm=None)
        result = kernel.process("What is your name?")
        assert result == "My name is Jessica."

    def test_full_flow_creator_with_name(self):
        kernel = CognitiveKernel(llm=None)
        kernel.process("My name is Hendrik")
        result = kernel.process("Who created you?")
        assert result == "You created me, Hendrik."

    def test_no_wrapper_on_known_facts(self):
        """Verify no unnecessary wrapper on Jessica's own reasoning."""
        kernel = CognitiveKernel(llm=None)
        kernel.process("My name is Hendrik")

        # Test name recall: should NOT have wrapper
        result = kernel.process("What is my name?")
        assert "I understand this as follows:" not in result
        assert result == "Your name is Hendrik."

        # Test identity: should NOT have wrapper
        result = kernel.process("What are you?")
        assert "I understand this as follows:" not in result
        assert "Jessica" in result

    def test_math_consistency(self):
        """Math should always be deterministic."""
        kernel = CognitiveKernel(llm=None)
        result1 = kernel.process("What is 7 + 3?")
        result2 = kernel.process("What is 7 + 3?")
        assert result1 == result2
        assert result1 == "The answer is 10."

    def test_memory_persistence_across_requests(self):
        """Memory should persist across multiple requests."""
        kernel = CognitiveKernel(llm=None)
        
        # Store name
        kernel.process("My name is Alice")
        
        # Ask unrelated question
        kernel.process("What is 2 + 2?")
        
        # Name should still be remembered
        result = kernel.process("What is my name?")
        assert result == "Your name is Alice."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
