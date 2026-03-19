"""Extended tests for intent_parser to improve coverage."""
import pytest
from jessica.nlp.intent_parser import parse_intent


class TestIntentParserExtended:
    """Extended coverage for intent parser edge cases."""

    def test_parse_intent_preserves_lowercase_text(self):
        """Test that original text case is preserved."""
        text = "PrInT ThE sYsTeM mOnItOr"
        result = parse_intent(text)
        assert result.get("text") == text

    def test_parse_intent_empty_string(self):
        """Test parsing empty string."""
        result = parse_intent("")
        assert result.get("intent") in ["chat", "unknown"]

    def test_parse_intent_very_long_text(self):
        """Test parsing very long input."""
        long_text = "Python " * 100
        result = parse_intent(long_text)
        assert result.get("text") is not None

    def test_parse_intent_special_characters(self):
        """Test parsing text with special characters."""
        text = "fix @#$% error in <script>"
        result = parse_intent(text)
        assert result.get("text") == text

    def test_parse_intent_multiple_keywords(self):
        """Test parsing with multiple matching keywords."""
        # Text with both programming and web keywords
        text = "create a Python script and search online"
        result = parse_intent(text)
        # Should route to one or the other (or chat)
        assert "intent" in result

    def test_parse_intent_numbers_only(self):
        """Test parsing with only numbers."""
        result = parse_intent("12345")
        assert result.get("intent") in ["chat", "unknown"]

    def test_parse_intent_whitespace_only(self):
        """Test parsing whitespace-only input."""
        result = parse_intent("   \t\n  ")
        assert result.get("intent") in ["chat", "unknown"]

    def test_parse_intent_single_word(self):
        """Test parsing single word inputs."""
        test_cases = ["code", "recipe", "chess", "help"]
        for word in test_cases:
            result = parse_intent(word)
            assert result.get("intent") is not None
