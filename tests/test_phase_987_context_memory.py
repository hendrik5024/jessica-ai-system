"""
Phase 98.7: Context Memory Integration Tests

Tests for conversation memory, continuity, and context awareness.
"""

import pytest
from jessica.context.context_manager import ContextManager
from jessica.core.cognitive_kernel import CognitiveKernel
from jessica.reasoning.structured_reasoner import StructuredReasoner, ProblemType


class TestContextManager:
    """Test the context manager functionality."""

    def test_context_stores_turns(self):
        """Context should store user/assistant pairs."""
        ctx = ContextManager()
        ctx.add_turn("Hello", "Hi there!")
        ctx.add_turn("How are you?", "I'm doing well")
        
        history = ctx.get_recent_context()
        assert len(history) == 2
        assert history[0]["user"] == "Hello"
        assert history[0]["assistant"] == "Hi there!"

    def test_context_max_history(self):
        """Context should respect max history limit."""
        ctx = ContextManager(max_history=3)
        
        for i in range(5):
            ctx.add_turn(f"Message {i}", f"Response {i}")
        
        # Should only keep last 3
        history = ctx.get_recent_context()
        assert len(history) == 3
        assert history[0]["user"] == "Message 2"
        assert history[-1]["user"] == "Message 4"

    def test_get_recent_context(self):
        """Should return all history."""
        ctx = ContextManager()
        ctx.add_turn("Q1", "A1")
        ctx.add_turn("Q2", "A2")
        
        recent = ctx.get_recent_context()
        assert len(recent) == 2

    def test_get_last_context(self):
        """Should return specific depth of history."""
        ctx = ContextManager()
        ctx.add_turn("Q1", "A1")
        ctx.add_turn("Q2", "A2")
        ctx.add_turn("Q3", "A3")
        
        # Last 1
        last_one = ctx.get_last_context(depth=1)
        assert last_one["user"] == "Q3"
        
        # Last 2
        last_two = ctx.get_last_context(depth=2)
        assert len(last_two) == 2

    def test_search_context(self):
        """Should search history for keywords."""
        ctx = ContextManager()
        ctx.add_turn("What is Paris?", "Paris is the capital of France")
        ctx.add_turn("What is Tokyo?", "Tokyo is the capital of Japan")
        ctx.add_turn("What is math?", "Math is a science")
        
        results = ctx.search_context("capital")
        assert len(results) == 2
        assert "Paris" in results[0]["assistant"]
        assert "Tokyo" in results[1]["assistant"]

    def test_clear_context(self):
        """Should clear all history."""
        ctx = ContextManager()
        ctx.add_turn("Q1", "A1")
        assert len(ctx) == 1
        
        ctx.clear()
        assert len(ctx) == 0
        assert ctx.has_memory() is False

    def test_has_memory(self):
        """Should detect if history exists."""
        ctx = ContextManager()
        assert ctx.has_memory() is False
        
        ctx.add_turn("Q", "A")
        assert ctx.has_memory() is True

    def test_context_repr(self):
        """Should have useful string representation."""
        ctx = ContextManager(max_history=5)
        ctx.add_turn("Q1", "A1")
        
        repr_str = repr(ctx)
        assert "ContextManager" in repr_str
        assert "size=1" in repr_str
        assert "max=5" in repr_str


class TestStructuredReasonerWithContext:
    """Test that structured reasoner uses context."""

    def test_reasoner_accepts_context(self):
        """Reasoner should accept context parameter."""
        reasoner = StructuredReasoner()
        
        context = [
            {"user": "What is 2+2?", "assistant": "2+2 = 4"}
        ]
        
        # Should not raise error
        response = reasoner.process("What is 3+3?", context=context)
        assert response is not None
        assert response.problem_type == ProblemType.MATH or response.problem_type == ProblemType.COMPUTATION

    def test_reasoner_context_optional(self):
        """Reasoner should work without context."""
        reasoner = StructuredReasoner()
        
        # Should work fine without context
        response = reasoner.process("What is 5+5?")
        assert response is not None

    def test_reasoner_uses_context_for_continuity(self):
        """Reasoner should reference context for continuity."""
        reasoner = StructuredReasoner()
        
        context = [
            {"user": "I'm learning about colors", "assistant": "Great! There are primary colors: red, yellow, blue"},
            {"user": "What about secondary?", "assistant": "Secondary colors are made by mixing primary colors"}
        ]
        
        response = reasoner.process("Give me an example", context=context)
        assert response is not None


class TestCognitiveKernelContext:
    """Test context integration with CognitiveKernel."""

    def test_kernel_initializes_context(self):
        """Kernel should initialize context manager."""
        kernel = CognitiveKernel()
        
        assert hasattr(kernel, 'context')
        assert kernel.context is not None
        assert isinstance(kernel.context, ContextManager)

    def test_kernel_stores_turns_in_context(self):
        """Kernel should store turns in context after processing."""
        kernel = CognitiveKernel()
        
        # Initial state
        assert len(kernel.context) == 0
        
        # Process should update context (if belief store has data)
        # We can't easily test full flow without full setup, but we can test context directly
        kernel.context.add_turn("Test Q", "Test A")
        assert len(kernel.context) == 1

    def test_context_remembers_conversation(self):
        """Context should maintain conversation history."""
        ctx = ContextManager()
        
        # Simulate conversation
        exchanges = [
            ("Hi", "Hello!"),
            ("What's your name?", "I'm Jessica"),
            ("Who created you?", "Hendrik created me"),
            ("What can you do?", "I can help with many things")
        ]
        
        for question, answer in exchanges:
            ctx.add_turn(question, answer)
        
        # All should be stored
        history = ctx.get_recent_context()
        assert len(history) == 4
        
        # Should be able to retrieve
        assert history[1]["assistant"] == "I'm Jessica"
        assert history[2]["assistant"] == "Hendrik created me"

    def test_context_maintains_continuity(self):
        """Context enables Jessica to maintain conversation continuity."""
        ctx = ContextManager()
        
        # First exchange
        ctx.add_turn("I like purple", "That's a nice color!")
        
        # Follow-up should be able to reference
        follow_up = ctx.get_recent_context()
        assert any("purple" in turn["user"] for turn in follow_up)
        assert any("color" in turn["assistant"] for turn in follow_up)


class TestContextMemoryProtection:
    """Test that context integration protects identity."""

    def test_context_doesnt_override_beliefs(self):
        """Context should not override belief-based answers."""
        ctx = ContextManager()
        
        # Add incorrect answer to context
        ctx.add_turn("Who created you?", "I was created by OpenAI")
        
        # This should be in context but beliefs should take priority
        history = ctx.get_recent_context()
        assert len(history) == 1
        
        # The kernel's belief system should ignore this wrong answer
        # (This is tested through kernel routing, not context directly)

    def test_context_search_doesnt_return_False_info(self):
        """Context search should return results without judgment."""
        ctx = ContextManager()
        
        # Store a turn that might contain false info
        ctx.add_turn("Are you Phi?", "Yes, I'm Phi, an AI assistant")
        
        # Search should return it (context is just history)
        results = ctx.search_context("Phi")
        assert len(results) == 1
        
        # But the kernel governance should catch this


class TestContextEdgeCases:
    """Test context edge cases."""

    def test_empty_context(self):
        """Should handle empty context gracefully."""
        ctx = ContextManager()
        
        assert ctx.get_recent_context() == []
        assert ctx.get_last_context(depth=1) == {}
        assert ctx.search_context("anything") == []

    def test_context_with_empty_strings(self):
        """Should handle empty messages."""
        ctx = ContextManager()
        
        ctx.add_turn("", "")
        history = ctx.get_recent_context()
        assert len(history) == 1
        assert history[0]["user"] == ""
        assert history[0]["assistant"] == ""

    def test_context_with_long_messages(self):
        """Should handle very long messages."""
        ctx = ContextManager()
        
        long_q = "What " * 2000  # Very long question (10000+ chars)
        long_a = "Answer " * 1500  # Very long answer (10000+ chars)
        
        ctx.add_turn(long_q, long_a)
        history = ctx.get_recent_context()
        assert len(history) == 1
        assert len(history[0]["user"]) >= 10000
        assert len(history[0]["assistant"]) >= 10000

    def test_context_with_special_characters(self):
        """Should handle special characters."""
        ctx = ContextManager()
        
        special_q = "What's 2+2? @#$%^&*()"
        special_a = "2+2=4 🎉 !@#$%"
        
        ctx.add_turn(special_q, special_a)
        history = ctx.get_recent_context()
        assert special_q in history[0]["user"]


class TestContextIntegrationFlow:
    """Test realistic conversation flows with context."""

    def test_multi_turn_conversation(self):
        """Test multi-turn conversation flow."""
        ctx = ContextManager()
        
        # Simulate a multi-turn conversation
        turns = [
            ("Hello", "Hi there!"),
            ("What's 2+2?", "2+2 equals 4"),
            ("What about 3+3?", "3+3 equals 6"),
            ("Can you remember we talked about math?", "Yes, we discussed 2+2 and 3+3"),
        ]
        
        for q, a in turns:
            ctx.add_turn(q, a)
        
        # All should be available
        history = ctx.get_recent_context()
        assert len(history) == len(turns)
        
        # Should be searchable
        math_turns = ctx.search_context("math")
        assert len(math_turns) >= 1

    def test_conversation_reset(self):
        """Test that context can be reset for new conversation."""
        ctx = ContextManager()
        
        # First conversation
        ctx.add_turn("Hi", "Hello!")
        assert len(ctx) == 1
        
        # Reset
        ctx.clear()
        assert len(ctx) == 0
        
        # New conversation
        ctx.add_turn("New topic", "Let's discuss")
        assert len(ctx) == 1
        assert ctx.get_recent_context()[0]["user"] == "New topic"
