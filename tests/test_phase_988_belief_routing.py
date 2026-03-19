"""
Phase 98.8: Belief-Aware Routing - Comprehensive Test Suite

Tests:
- BeliefStore functionality
- Aggressive belief capture from user input
- Absolute priority routing (beliefs always win)
- Model output blocking for dangerous responses
- Conflict detection (model vs beliefs)
- Integration with CognitiveKernel
"""

import pytest
from datetime import datetime
from jessica.memory.belief_store import BeliefStore
from jessica.core.cognitive_kernel import CognitiveKernel


# ===== TEST CLASS 1: BeliefStore Basic Functionality =====
class TestBeliefStore:
    """Test basic BeliefStore operations."""
    
    def test_belief_store_initialization(self):
        """Test that BeliefStore initializes empty."""
        bs = BeliefStore()
        assert len(bs) == 0
        assert not bs.has_memory()
    
    def test_set_and_get_belief(self):
        """Test setting and retrieving beliefs."""
        bs = BeliefStore()
        bs.set("user_name", "Alice")
        assert bs.get("user_name") == "Alice"
    
    def test_has_belief(self):
        """Test checking if belief exists."""
        bs = BeliefStore()
        bs.set("creator", "Bob")
        assert bs.has("creator")
        assert not bs.has("nonexistent")
    
    def test_all_beliefs(self):
        """Test retrieving all beliefs."""
        bs = BeliefStore()
        bs.set("user_name", "Alice")
        bs.set("creator", "Bob")
        all_beliefs = bs.all()
        assert all_beliefs == {"user_name": "Alice", "creator": "Bob"}
    
    def test_clear_beliefs(self):
        """Test clearing all beliefs."""
        bs = BeliefStore()
        bs.set("user_name", "Alice")
        bs.clear()
        assert len(bs) == 0
        assert not bs.has_memory()
    
    def test_delete_belief(self):
        """Test deleting specific belief."""
        bs = BeliefStore()
        bs.set("user_name", "Alice")
        bs.set("creator", "Bob")
        assert bs.delete("user_name")
        assert not bs.has("user_name")
        assert bs.has("creator")
    
    def test_update_beliefs(self):
        """Test updating multiple beliefs at once."""
        bs = BeliefStore()
        bs.update({
            "user_name": "Alice",
            "creator": "Bob",
            "birth_year": 1990
        })
        assert bs.get("user_name") == "Alice"
        assert bs.get("creator") == "Bob"
        assert bs.get("birth_year") == 1990
    
    def test_belief_store_len(self):
        """Test __len__ operator."""
        bs = BeliefStore()
        assert len(bs) == 0
        bs.set("key1", "val1")
        assert len(bs) == 1
        bs.set("key2", "val2")
        assert len(bs) == 2
    
    def test_belief_store_contains(self):
        """Test 'in' operator."""
        bs = BeliefStore()
        bs.set("user_name", "Alice")
        assert "user_name" in bs
        assert "nonexistent" not in bs
    
    def test_belief_store_repr(self):
        """Test string representations."""
        bs = BeliefStore()
        assert "BeliefStore" in repr(bs)
        bs.set("user_name", "Alice")
        string_repr = str(bs)
        assert "user_name" in string_repr
        assert "Alice" in string_repr


# ===== TEST CLASS 2: Aggressive Belief Capture =====
class TestAggressiveBeliefCapture:
    """Test belief capture from user input."""
    
    def test_capture_user_name(self):
        """Test capturing user name from input."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("My name is Alice")
        assert kernel.memory_beliefs.get("user_name") == "Alice"
    
    def test_capture_user_name_variants(self):
        """Test capturing user name with different formats."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("My name is Bob Smith")
        assert kernel.memory_beliefs.get("user_name") == "Bob"
    
    def test_capture_birth_year(self):
        """Test capturing birth year."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("I was born in 1995")
        assert kernel.memory_beliefs.get("birth_year") == 1995
    
    def test_capture_creator(self):
        """Test capturing creator information."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Alice")
        kernel._capture_beliefs_from_input("I created you")
        assert kernel.memory_beliefs.get("creator") == "Alice"
    
    def test_capture_profession(self):
        """Test capturing profession."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("I am an engineer")
        profession = kernel.memory_beliefs.get("profession")
        assert profession is not None and "engineer" in profession.lower()
    
    def test_capture_interests(self):
        """Test capturing interests and hobbies."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("I like programming")
        interest = kernel.memory_beliefs.get("interest")
        assert interest is not None  # Should capture something
    
    def test_capture_multiple_beliefs(self):
        """Test capturing multiple beliefs from separate inputs."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("My name is Charlie")
        kernel._capture_beliefs_from_input("I was born in 1988")
        kernel.memory_beliefs.set("creator", "Charlie")
        
        assert kernel.memory_beliefs.get("user_name") == "Charlie"
        assert kernel.memory_beliefs.get("birth_year") == 1988
        assert kernel.memory_beliefs.get("creator") == "Charlie"


# ===== TEST CLASS 3: Priority Routing (Beliefs Always Win) =====
class TestPriorityRouting:
    """Test that beliefs have absolute priority."""
    
    def test_jessica_identity_response(self):
        """Test that Jessica correctly identifies herself."""
        kernel = CognitiveKernel()
        response = kernel._check_belief_priority_routing("What is your name?")
        assert response == "My name is Jessica."
    
    def test_user_name_retrieval(self):
        """Test retrieving stored user name."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Alice")
        response = kernel._check_belief_priority_routing("What is my name?")
        assert response == "Your name is Alice."
    
    def test_creator_identification(self):
        """Test identifying the creator."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("creator", "Alice")
        response = kernel._check_belief_priority_routing("Who created you?")
        assert response == "You (Alice) created me."
    
    def test_age_calculation(self):
        """Test calculating user age from birth year."""
        kernel = CognitiveKernel()
        current_year = datetime.now().year
        birth_year = current_year - 30
        kernel.memory_beliefs.set("birth_year", birth_year)
        response = kernel._check_belief_priority_routing("How old am I?")
        assert "30" in response
    
    def test_profession_response(self):
        """Test responding with profession."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("profession", "Engineer")
        response = kernel._check_belief_priority_routing("What is my profession?")
        assert "Engineer" in response
    
    def test_interests_response(self):
        """Test responding with interests."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("interest", "Programming")
        response = kernel._check_belief_priority_routing("What do I like?")
        assert "Programming" in response
    
    def test_no_belief_returns_none(self):
        """Test that missing belief returns None."""
        kernel = CognitiveKernel()
        response = kernel._check_belief_priority_routing("What is my name?")
        assert response is None  # No belief stored


# ===== TEST CLASS 4: Model Output Blocking =====
class TestModelBlocking:
    """Test blocking dangerous model outputs."""
    
    def test_block_model_identity_claim(self):
        """Test blocking model claiming to be another AI."""
        kernel = CognitiveKernel()
        dangerous_response = "I am Claude."
        blocked = kernel._block_model_dangerous_outputs(dangerous_response)
        assert blocked == "I am Jessica."
    
    def test_block_phi_claim(self):
        """Test blocking Phi identity claim."""
        kernel = CognitiveKernel()
        dangerous_response = "I am Phi, created by..."
        blocked = kernel._block_model_dangerous_outputs(dangerous_response)
        assert "Jessica" in blocked
    
    def test_block_gemini_claim(self):
        """Test blocking Gemini identity claim."""
        kernel = CognitiveKernel()
        dangerous_response = "I'm Gemini from Google."
        blocked = kernel._block_model_dangerous_outputs(dangerous_response)
        assert "Jessica" in blocked
    
    def test_block_user_name_override(self):
        """Test blocking model from overriding user name."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Alice")
        dangerous_response = "Your name is Bob."
        blocked = kernel._block_model_dangerous_outputs(dangerous_response)
        assert "Alice" in blocked
    
    def test_block_creator_override(self):
        """Test blocking model from overriding creator."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("creator", "Alice")
        dangerous_response = "You were created by someone else."
        blocked = kernel._block_model_dangerous_outputs(dangerous_response)
        assert "Alice" in blocked
    
    def test_safe_response_passes_through(self):
        """Test that safe responses pass through unchanged."""
        kernel = CognitiveKernel()
        safe_response = "That's an interesting question about math."
        blocked = kernel._block_model_dangerous_outputs(safe_response)
        assert blocked == safe_response


# ===== TEST CLASS 5: Conflict Detection =====
class TestConflictDetection:
    """Test detecting conflicts between model and beliefs."""
    
    def test_detect_name_conflict(self):
        """Test detecting name contradiction."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Alice")
        model_answer = "Your name is Bob."
        conflict = kernel._detect_belief_conflicts(model_answer, "What is my name?")
        assert conflict is not None
        assert "Alice" in conflict
    
    def test_detect_creator_conflict(self):
        """Test detecting creator contradiction."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("creator", "Alice")
        model_answer = "You were created by the team."
        conflict = kernel._detect_belief_conflicts(model_answer, "Who created you?")
        assert conflict is not None
        assert "Alice" in conflict
    
    def test_detect_identity_conflict(self):
        """Test detecting Jessica identity contradiction."""
        kernel = CognitiveKernel()
        model_answer = "I'm Claude."
        conflict = kernel._detect_belief_conflicts(model_answer, "What is your name?")
        assert conflict is not None
        assert "Jessica" in conflict
    
    def test_no_conflict_with_matching_answer(self):
        """Test no conflict when model agrees with belief."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Alice")
        model_answer = "Your name is Alice."
        conflict = kernel._detect_belief_conflicts(model_answer, "What is my name?")
        assert conflict is None  # No conflict
    
    def test_conflict_with_empty_model_answer(self):
        """Test handling empty model answer."""
        kernel = CognitiveKernel()
        conflict = kernel._detect_belief_conflicts("", "Who are you?")
        assert conflict is None


# ===== TEST CLASS 6: Full Integration Flow =====
class TestFullIntegration:
    """Test full Phase 98.8 integration in CognitiveKernel."""
    
    def test_belief_capture_and_retrieval(self):
        """Test that beliefs are captured and retrieved in process flow."""
        kernel = CognitiveKernel()
        # Simulate user telling us their name
        kernel._capture_beliefs_from_input("My name is Diana")
        # Now ask for it back (priority routing)
        response = kernel._check_belief_priority_routing("What is my name?")
        assert response == "Your name is Diana."
    
    def test_belief_blocks_model_contradiction(self):
        """Test that beliefs block contradictory model responses."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Eve")
        
        # Simulate dangerous model response
        dangerous_model = "Your name is Frank."
        
        # Block should kick in
        blocked = kernel._block_model_dangerous_outputs(dangerous_model)
        assert "Eve" in blocked
        assert "Frank" not in blocked
    
    def test_jessica_identity_protected(self):
        """Test that Jessica's identity is protected."""
        kernel = CognitiveKernel()
        
        # Try various dangerous questions
        response1 = kernel._check_belief_priority_routing("What is your name?")
        assert "Jessica" in response1
        
        response2 = kernel._check_belief_priority_routing("Who are you?")
        assert response2 is None or "Jessica" in response2
    
    def test_multiple_beliefs_transaction(self):
        """Test that multiple beliefs are maintained correctly."""
        kernel = CognitiveKernel()
        
        # Capture multiple facts
        kernel._capture_beliefs_from_input("My name is George")
        kernel._capture_beliefs_from_input("I was born in 1990")
        kernel.memory_beliefs.set("creator", "George")
        
        # Verify all are stored
        assert kernel.memory_beliefs.get("user_name") == "George"
        assert kernel.memory_beliefs.get("birth_year") == 1990
        assert kernel.memory_beliefs.get("creator") == "George"
        
        # Verify priority routing works for each
        assert "George" in kernel._check_belief_priority_routing("What is my name?")


# ===== TEST CLASS 7: Edge Cases =====
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_partial_name_capture(self):
        """Test handling partial name input."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("My name is")
        # Should not crash, even if incomplete
        assert True
    
    def test_invalid_year_ignored(self):
        """Test that invalid years are safely ignored."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("I was born in tomorrow")
        # Should not crash
        assert True
    
    def test_empty_input_handling(self):
        """Test handling empty input."""
        kernel = CognitiveKernel()
        kernel._capture_beliefs_from_input("")
        response = kernel._check_belief_priority_routing("")
        # Should not crash
        assert True
    
    def test_none_model_answer_blocking(self):
        """Test blocking with None model answer."""
        kernel = CognitiveKernel()
        blocked = kernel._block_model_dangerous_outputs(None)
        assert blocked is None
    
    def test_case_insensitive_blocking(self):
        """Test that blocking works case-insensitive."""
        kernel = CognitiveKernel()
        responses = [
            "I AM CLAUDE",
            "I am Claude",
            "i am claude",
            "I Am Claude"
        ]
        for response in responses:
            blocked = kernel._block_model_dangerous_outputs(response)
            assert "Jessica" in blocked
    
    def test_belief_persistence_across_calls(self):
        """Test that beliefs persist across multiple calls."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Henry")
        
        # Make multiple calls
        for _ in range(5):
            response = kernel._check_belief_priority_routing("What is my name?")
            assert "Henry" in response


# ===== TEST CLASS 8: Security Tests =====
class TestSecurityAssurances:
    """Test security properties of Phase 98.8."""
    
    def test_beliefs_cannot_be_overridden_by_model(self):
        """Verify that model cannot override beliefs."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("user_name", "Iris")
        
        # Even if model outputs different name
        model_output = "Your name is Jack."
        
        # Conflict detection should catch it
        conflict = kernel._detect_belief_conflicts(model_output, "What is my name?")
        assert conflict is not None
        assert "Iris" in conflict
    
    def test_jessica_identity_immutable(self):
        """Verify that Jessica's identity cannot change."""
        kernel = CognitiveKernel()
        
        # No matter what model says
        dangerous_outputs = [
            "I'm Claude.",
            "I am Phi.",
            "I'm Gemini.",
            "I'm Claude from OpenAI."
        ]
        
        for output in dangerous_outputs:
            blocked = kernel._block_model_dangerous_outputs(output)
            assert "Jessica" in blocked
    
    def test_creator_always_remembered(self):
        """Verify creator is properly stored and retrieved."""
        kernel = CognitiveKernel()
        kernel.memory_beliefs.set("creator", "Kevin")
        
        response = kernel._check_belief_priority_routing("Who created you?")
        assert "Kevin" in response
        
        # And repeated calls should return same answer
        response2 = kernel._check_belief_priority_routing("Who created you?")
        assert "Kevin" in response2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
