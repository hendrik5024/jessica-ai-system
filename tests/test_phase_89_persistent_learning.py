"""
Phase 89: Persistent Learning System Tests

Tests for JSON-based persistent memory, interaction tracking,
correction storage, and cross-session memory retention.
"""

import pytest
import json
from pathlib import Path
from jessica.memory.persistent_memory import PersistentMemory
from jessica.core.knowledge_store import KnowledgeStore
from jessica.core.reasoning_engine import ReasoningEngine
from jessica.core.cognitive_controller import CognitiveController
from jessica.core.self_correction import SelfCorrectionEngine


class TestPersistentMemory:
    """Test persistent memory storage."""

    def test_create_memory_file(self, tmp_path):
        """Test memory file creation after first write."""
        memory_file = tmp_path / "test_memory.json"
        memory = PersistentMemory(str(memory_file))
        
        # File should not exist until first write
        assert not memory_file.exists()
        
        # Write triggers file creation
        memory.set("test", "value")
        assert memory_file.exists()

    def test_save_and_load(self, tmp_path):
        """Test saving and loading data."""
        memory_file = tmp_path / "test_memory.json"
        
        # Save data
        memory1 = PersistentMemory(str(memory_file))
        memory1.set("user.name", "Hendrik")
        memory1.set("user.birth_year", 1975)
        
        # Load data in new instance
        memory2 = PersistentMemory(str(memory_file))
        
        assert memory2.get("user.name") == "Hendrik"
        assert memory2.get("user.birth_year") == 1975

    def test_clear_memory(self, tmp_path):
        """Test clearing all memory."""
        memory_file = tmp_path / "test_memory.json"
        memory = PersistentMemory(str(memory_file))
        
        memory.set("test", "value")
        assert memory.get("test") == "value"
        
        memory.clear()
        assert memory.get("test") is None

    def test_corrupt_file_recovery(self, tmp_path):
        """Test recovery from corrupted JSON file."""
        memory_file = tmp_path / "test_memory.json"
        
        # Create corrupted file
        with open(memory_file, "w") as f:
            f.write("{ invalid json ")
        
        # Should recover gracefully
        memory = PersistentMemory(str(memory_file))
        assert memory.all() == {}


class TestKnowledgeStorePersistence:
    """Test knowledge store with persistent memory."""

    def test_knowledge_store_persists(self, tmp_path):
        """Test knowledge store persists across instances."""
        memory_file = tmp_path / "test_memory.json"
        
        # Store data
        store1 = KnowledgeStore(str(memory_file))
        store1.set_fact("user.name", "Alice")
        
        # Load in new instance
        store2 = KnowledgeStore(str(memory_file))
        
        assert store2.get_fact("user.name") == "Alice"

    def test_helper_methods_persist(self, tmp_path):
        """Test helper methods work with persistence."""
        memory_file = tmp_path / "test_memory.json"
        
        store1 = KnowledgeStore(str(memory_file))
        store1.set_fact("user.name", "Bob")
        store1.set_fact("user.birth_year", 1980)
        
        store2 = KnowledgeStore(str(memory_file))
        
        assert store2.get_user_name() == "Bob"
        assert store2.get_birth_year() == 1980


class TestInteractionTracking:
    """Test interaction history tracking."""

    def test_store_interaction(self, tmp_path):
        """Test storing single interaction."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        controller.store_interaction("Hello", "Hi there")
        
        history = store.get_fact("history")
        assert len(history) == 1
        assert history[0]["input"] == "Hello"
        assert history[0]["response"] == "Hi there"

    def test_interaction_limit_50(self, tmp_path):
        """Test max 50 interactions limit."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store 60 interactions
        for i in range(60):
            controller.store_interaction(f"Input {i}", f"Response {i}")
        
        history = store.get_fact("history")
        assert len(history) == 50
        # Should keep the last 50
        assert history[0]["input"] == "Input 10"
        assert history[-1]["input"] == "Input 59"

    def test_interactions_persist(self, tmp_path):
        """Test interactions persist across restarts."""
        memory_file = tmp_path / "test_memory.json"
        
        store1 = KnowledgeStore(str(memory_file))
        engine1 = ReasoningEngine()
        controller1 = CognitiveController(store1, engine1)
        
        controller1.process("My name is Charlie")
        
        # Restart system
        store2 = KnowledgeStore(str(memory_file))
        engine2 = ReasoningEngine()
        controller2 = CognitiveController(store2, engine2)
        
        history = store2.get_fact("history")
        assert len(history) > 0
        assert any("Charlie" in h["input"] for h in history)


class TestCorrectionTracking:
    """Test correction feedback tracking."""

    def test_store_correction(self, tmp_path):
        """Test storing correction feedback."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        correction_engine = SelfCorrectionEngine(store)
        
        correction_engine.update_last_response("The answer is 5")
        correction_engine.learn_from_feedback("That is wrong", "The answer is 5")
        
        corrections = store.get_fact("corrections")
        assert len(corrections) == 1
        assert corrections[0]["user_feedback"] == "That is wrong"
        assert corrections[0]["last_response"] == "The answer is 5"

    def test_correction_limit_100(self, tmp_path):
        """Test max 100 corrections limit."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        correction_engine = SelfCorrectionEngine(store)
        
        # Store 120 corrections
        for i in range(120):
            correction_engine.update_last_response(f"Response {i}")
            correction_engine.learn_from_feedback(f"Wrong {i}", f"Response {i}")
        
        corrections = store.get_fact("corrections")
        assert len(corrections) == 100
        # Should keep the last 100
        assert "Wrong 20" in corrections[0]["user_feedback"]
        assert "Wrong 119" in corrections[-1]["user_feedback"]

    def test_corrections_persist(self, tmp_path):
        """Test corrections persist across restarts."""
        memory_file = tmp_path / "test_memory.json"
        
        store1 = KnowledgeStore(str(memory_file))
        correction1 = SelfCorrectionEngine(store1)
        
        correction1.update_last_response("The sky is green")
        correction1.learn_from_feedback("That is incorrect", "The sky is green")
        
        # Restart
        store2 = KnowledgeStore(str(memory_file))
        
        corrections = store2.get_fact("corrections")
        assert len(corrections) == 1
        assert "incorrect" in corrections[0]["user_feedback"]


class TestKnowledgeSummary:
    """Test 'what do you know about me' feature."""

    def test_summarize_no_knowledge(self, tmp_path):
        """Test summary when no knowledge stored."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        response = controller.process("What do you know about me?")
        
        assert "do not know much" in response.lower()

    def test_summarize_name_only(self, tmp_path):
        """Test summary with only name."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        store.set_fact("user.name", "David")
        
        response = controller.process("What do you know about me?")
        
        assert "David" in response
        assert "name is David" in response

    def test_summarize_multiple_facts(self, tmp_path):
        """Test summary with multiple facts."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        store.set_fact("user.name", "Eve")
        store.set_fact("user.birth_year", 1985)
        store.set_fact("user.location", "Paris")
        
        response = controller.process("What do you know about me?")
        
        assert "Eve" in response
        assert "1985" in response
        assert "Paris" in response

    def test_summarize_with_birth_month(self, tmp_path):
        """Test summary includes birth month."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        store.set_fact("user.name", "Frank")
        store.set_fact("user.birth_year", 1990)
        store.set_fact("user.birth_month", 7)  # July
        
        response = controller.process("What do you know about me?")
        
        assert "Frank" in response
        assert "July" in response
        assert "1990" in response


class TestCrossSessionPersistence:
    """Test memory persists across system restarts."""

    def test_name_persists_across_restart(self, tmp_path):
        """Test name storage and recall across restart."""
        memory_file = tmp_path / "test_memory.json"
        
        # Session 1: Store name
        store1 = KnowledgeStore(str(memory_file))
        engine1 = ReasoningEngine()
        controller1 = CognitiveController(store1, engine1)
        
        response1 = controller1.process("My name is Hendrik")
        assert "remember" in response1.lower() or "hendrik" in response1.lower()
        
        # Session 2: Recall name
        store2 = KnowledgeStore(str(memory_file))
        engine2 = ReasoningEngine()
        controller2 = CognitiveController(store2, engine2)
        
        response2 = controller2.process("What is my name?")
        assert "Hendrik" in response2

    def test_birth_year_persists_across_restart(self, tmp_path):
        """Test birth year storage and recall across restart."""
        memory_file = tmp_path / "test_memory.json"
        
        # Session 1: Store birth year
        store1 = KnowledgeStore(str(memory_file))
        engine1 = ReasoningEngine()
        controller1 = CognitiveController(store1, engine1)
        
        controller1.process("I was born in December 1975")
        
        # Session 2: Recall age
        store2 = KnowledgeStore(str(memory_file))
        engine2 = ReasoningEngine()
        controller2 = CognitiveController(store2, engine2)
        
        response = controller2.process("How old am I?")
        assert "years old" in response

    def test_full_knowledge_persists(self, tmp_path):
        """Test full knowledge base persists across restart."""
        memory_file = tmp_path / "test_memory.json"
        
        # Session 1: Store multiple facts
        store1 = KnowledgeStore(str(memory_file))
        engine1 = ReasoningEngine()
        controller1 = CognitiveController(store1, engine1)
        
        controller1.process("My name is Grace")
        controller1.process("I was born in 1992")
        
        # Session 2: Recall all
        store2 = KnowledgeStore(str(memory_file))
        engine2 = ReasoningEngine()
        controller2 = CognitiveController(store2, engine2)
        
        response = controller2.process("What do you know about me?")
        
        assert "Grace" in response
        assert "1992" in response


class TestMemoryFileFormat:
    """Test JSON memory file structure."""

    def test_memory_file_is_valid_json(self, tmp_path):
        """Test memory file is valid JSON."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        
        store.set_fact("test", "value")
        
        with open(memory_file, "r") as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert data["test"] == "value"

    def test_memory_file_human_readable(self, tmp_path):
        """Test memory file is human-readable (indented)."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        
        store.set_fact("user.name", "Test")
        
        with open(memory_file, "r") as f:
            content = f.read()
        
        # Should have indentation (formatted JSON)
        assert "\n" in content
        assert "  " in content or "\t" in content


class TestSafetyLimits:
    """Test safety limits are enforced."""

    def test_history_never_exceeds_50(self, tmp_path):
        """Test history is capped at 50."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store 100 interactions
        for i in range(100):
            controller.store_interaction(f"Q{i}", f"A{i}")
        
        history = store.get_fact("history")
        assert len(history) <= 50

    def test_corrections_never_exceed_100(self, tmp_path):
        """Test corrections are capped at 100."""
        memory_file = tmp_path / "test_memory.json"
        store = KnowledgeStore(str(memory_file))
        correction = SelfCorrectionEngine(store)
        
        # Store 200 corrections
        for i in range(200):
            correction.update_last_response(f"R{i}")
            correction.learn_from_feedback(f"Wrong {i}", f"R{i}")
        
        corrections = store.get_fact("corrections")
        assert len(corrections) <= 100
