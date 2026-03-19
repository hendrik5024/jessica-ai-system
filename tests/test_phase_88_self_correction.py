"""
Phase 88: Self-Correction & Deep Reasoning Tests

Tests for improved age calculation, self-correction, and consistency checking.
"""

import pytest
from datetime import datetime
from pathlib import Path
from jessica.core.knowledge_store import KnowledgeStore
from jessica.core.reasoning_engine import ReasoningEngine
from jessica.core.cognitive_controller import CognitiveController
from jessica.core.self_correction import SelfCorrectionEngine


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


class TestAgeCalculation:
    """Test improved age calculation with birth month."""

    def test_calculate_age_without_month(self):
        """Calculate age using only birth year."""
        engine = ReasoningEngine()
        current_year = datetime.now().year
        birth_year = 1975
        
        age = engine.calculate_age(birth_year)
        
        expected_age = current_year - birth_year
        assert age == expected_age

    def test_calculate_age_with_month_before_birthday(self):
        """Calculate age when birthday hasn't occurred yet this year."""
        engine = ReasoningEngine()
        current_month = datetime.now().month
        current_year = datetime.now().year
        birth_year = 1975
        
        # Set birth month to future month
        birth_month = (current_month % 12) + 1
        
        age = engine.calculate_age(birth_year, birth_month)
        
        # Should subtract 1 if birth month is in the future
        if birth_month > current_month:
            expected_age = current_year - birth_year - 1
        else:
            expected_age = current_year - birth_year
        
        assert age == expected_age

    def test_calculate_age_with_month_after_birthday(self):
        """Calculate age when birthday has already occurred this year."""
        engine = ReasoningEngine()
        current_month = datetime.now().month
        current_year = datetime.now().year
        birth_year = 1975
        
        # Set birth month to past month
        birth_month = max(1, current_month - 1)
        
        age = engine.calculate_age(birth_year, birth_month)
        
        expected_age = current_year - birth_year
        assert age == expected_age

    def test_resolve_age_with_month(self):
        """Test age resolution using birth year and month."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        
        store.set_fact("user.birth_year", 1975)
        store.set_fact("user.birth_month", 12)  # December
        
        result = engine.resolve_age(store)
        
        assert "You are" in result
        assert "years old" in result
        assert result.count("approximately") == 0  # Should not say "approximately" anymore


class TestBirthMonthStorage:
    """Test storing and using birth month information."""

    def test_store_birth_month_december(self):
        """Store birth information with month."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        response = controller.process("I was born in December 1975")
        
        assert "remember" in response.lower()
        assert store.get_fact("user.birth_year") == 1975
        assert store.get_fact("user.birth_month") == 12

    def test_store_birth_month_january(self):
        """Store birth information with January."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        response = controller.process("I was born in January 1980")
        
        assert store.get_fact("user.birth_year") == 1980
        assert store.get_fact("user.birth_month") == 1

    def test_store_birth_year_only(self):
        """Store birth year without month."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        response = controller.process("I was born in 1990")
        
        assert store.get_fact("user.birth_year") == 1990
        assert store.get_fact("user.birth_month") is None

    def test_accurate_age_with_month(self):
        """Test accurate age calculation with birth month."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store birth info with December
        current_month = datetime.now().month
        
        controller.process("I was born in December 1975")
        response = controller.process("How old am I?")
        
        # Calculate expected age
        current_year = datetime.now().year
        expected_age = current_year - 1975
        if current_month < 12:  # Before December birthday
            expected_age -= 1
        
        assert f"You are {expected_age} years old" in response


class TestSelfCorrection:
    """Test self-correction capabilities."""

    def test_correction_signal_incorrect(self):
        """Detect 'incorrect' correction signal."""
        engine = SelfCorrectionEngine()
        
        result = engine.check("That is incorrect")
        
        assert result is not None
        assert "review" in result.lower()

    def test_correction_signal_wrong(self):
        """Detect 'wrong' correction signal."""
        engine = SelfCorrectionEngine()
        
        result = engine.check("That's wrong")
        
        assert result is not None
        assert "mistake" in result.lower()

    def test_correction_signal_not_right(self):
        """Detect 'not right' correction signal."""
        engine = SelfCorrectionEngine()
        
        result = engine.check("No that's not right")
        
        assert result is not None
        assert "apologize" in result.lower() or "reconsider" in result.lower()

    def test_no_correction_signal(self):
        """No correction needed for normal input."""
        engine = SelfCorrectionEngine()
        
        result = engine.check("What is my name?")
        
        assert result is None

    def test_correction_in_controller(self):
        """Test correction signal handling in controller."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        response = controller.process("That is wrong")
        
        assert "mistake" in response.lower() or "review" in response.lower()


class TestConsistencyChecking:
    """Test consistency checking for conflicting information."""

    def test_detect_birth_year_conflict(self):
        """Detect conflicting birth year information."""
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        
        engine = SelfCorrectionEngine(store)
        
        result = engine.check_consistency("user.birth_year", 1980, "I was born in 1980")
        
        assert result is not None
        assert "conflict" in result.lower() or "inconsistent" in result.lower()

    def test_no_conflict_when_empty(self):
        """No conflict when nothing is stored."""
        store = KnowledgeStore()
        engine = SelfCorrectionEngine(store)
        
        result = engine.check_consistency("user.birth_year", 1975, "I was born in 1975")
        
        assert result is None

    def test_no_conflict_when_same(self):
        """No conflict when values match."""
        store = KnowledgeStore()
        store.set_fact("user.birth_year", 1975)
        
        engine = SelfCorrectionEngine(store)
        
        result = engine.check_consistency("user.birth_year", 1975, "I was born in 1975")
        
        assert result is None

    def test_age_inconsistency_detection(self):
        """Detect age claim inconsistent with stored birth year."""
        store = KnowledgeStore()
        current_year = datetime.now().year
        store.set_fact("user.birth_year", 1975)
        
        engine = SelfCorrectionEngine(store)
        
        # Claim age of 30 when birth year suggests ~50
        result = engine.check_consistency("user.birth_year", current_year - 30, "I am 30 years old")
        
        assert result is not None
        assert "inconsistent" in result.lower() or "1975" in result

    def test_consistency_in_controller(self):
        """Test consistency checking in controller."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store initial birth year
        controller.process("I was born in 1975")
        
        # Try to store conflicting birth year
        response = controller.process("I was born in 1980")
        
        assert "conflict" in response.lower() or "inconsistent" in response.lower()
        # Original value should be preserved
        assert store.get_fact("user.birth_year") == 1975


class TestIntegration:
    """Integration tests for Phase 88 features."""

    def test_full_age_workflow(self):
        """Test complete age workflow with month."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store birth info
        response1 = controller.process("I was born in December 1975")
        assert "remember" in response1.lower()
        
        # Query age
        response2 = controller.process("How old am I?")
        assert "years old" in response2
        assert "You are" in response2

    def test_correction_after_mistake(self):
        """Test correction flow after detecting mistake."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Jessica provides answer
        response1 = controller.process("What is 2+2?")
        assert "4" in response1
        
        # User says it's wrong (hypothetically)
        response2 = controller.process("That is incorrect")
        assert "review" in response2.lower() or "mistake" in response2.lower()

    def test_prevent_blind_overwrite(self):
        """Ensure Jessica doesn't blindly overwrite memory."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Initial memory
        controller.process("I was born in 1975")
        original = store.get_fact("user.birth_year")
        
        # Conflicting information
        response = controller.process("I was born in 1990")
        
        # Should warn about conflict
        assert "conflict" in response.lower() or "inconsistent" in response.lower()
        
        # Original should be preserved
        assert store.get_fact("user.birth_year") == original

    def test_model_still_fallback(self):
        """Ensure model is only used as fallback."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine, model=None)
        
        # Personal question (should NOT use model)
        response1 = controller.process("What is my name?")
        assert "do not know" in response1.lower()
        
        # Math question (should NOT use model)
        response2 = controller.process("What is 5+5?")
        assert "10" in response2

    def test_human_like_responses(self):
        """Test for more human-like response patterns."""
        store = KnowledgeStore()
        engine = ReasoningEngine()
        controller = CognitiveController(store, engine)
        
        # Store info with month
        response1 = controller.process("I was born in December 1975")
        
        # Age should be accurate (not "approximately")
        response2 = controller.process("How old am I?")
        assert "approximately" not in response2.lower()
        
        # Correction response should be natural
        response3 = controller.process("That is wrong")
        assert any(phrase in response3.lower() for phrase in ["mistake", "review", "correct"])
