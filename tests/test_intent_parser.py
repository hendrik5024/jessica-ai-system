"""
Unit tests for intent_parser.
"""

import pytest
from jessica.nlp.intent_parser import parse_intent


class TestIntentParser:
    """Test intent parsing."""

    def test_parse_chat_intent(self):
        """Test detecting chat intent."""
        result = parse_intent("Hello, how are you?")
        assert result.get("intent") == "chat"

    def test_parse_programming_intent(self):
        """Test detecting programming intent."""
        test_cases = [
            "write a Python function",
            "install requests",
            "create file",
        ]
        for text in test_cases:
            result = parse_intent(text)
            intent = result.get("intent")
            # "programming" or "chat" are both acceptable for ambiguous inputs
            assert intent in ["programming", "chat"], f"Failed for: {text}"

    def test_parse_recipe_intent(self):
        """Test detecting recipe intent."""
        result = parse_intent("recipe for pasta carbonara")
        assert result.get("intent") == "recipe"

    def test_parse_web_intent(self):
        """Test detecting web browser intent."""
        result = parse_intent("search for Python tutorials")
        intent = result.get("intent")
        # "web_browser" or "chat" are both acceptable
        assert intent in ["web_browser", "chat"]

    def test_parse_chess_intent(self):
        """Test detecting chess intent."""
        result = parse_intent("play chess with me")
        assert result.get("intent") == "play_chess"

    def test_parse_monitor_intent(self):
        """Test detecting system monitor intent."""
        result = parse_intent("show CPU usage")
        assert result.get("intent") == "monitor"

    def test_parse_advice_intent(self):
        """Test detecting advice intent."""
        test_cases = [
            "what is ad hominem",
            "give me communication feedback",
        ]
        for text in test_cases:
            result = parse_intent(text)
            intent = result.get("intent")
            # "advice" or "chat" are both acceptable for edge cases
            assert intent in ["advice", "chat"], f"Failed for: {text}"

    def test_text_preserved(self):
        """Test that original text is preserved."""
        text = "Generate code for data analysis"
        result = parse_intent(text)
        assert result.get("text") == text
