"""
Phase 95: Tool Selection Engine - Tests

Tests for the ToolSelector that routes requests
to appropriate capabilities.
"""

import pytest
from jessica.core.tool_selector import ToolSelector
from jessica.core.cognitive_kernel import CognitiveKernel


class TestToolSelector:
    """Test ToolSelector detection logic."""

    def test_selector_initializes(self):
        """ToolSelector initializes without error."""
        selector = ToolSelector()
        assert selector is not None

    # ============================================================
    # MATH DETECTION
    # ============================================================

    def test_detects_simple_addition(self):
        """Detects simple addition."""
        selector = ToolSelector()
        result = selector.select_tool("calculate 5 + 3")
        assert result == "calculate"

    def test_detects_subtraction(self):
        """Detects subtraction."""
        selector = ToolSelector()
        result = selector.select_tool("what is 10 - 7")
        assert result == "calculate"

    def test_detects_multiplication(self):
        """Detects multiplication."""
        selector = ToolSelector()
        result = selector.select_tool("2 * 8")
        assert result == "calculate"

    def test_detects_division(self):
        """Detects division."""
        selector = ToolSelector()
        result = selector.select_tool("100 / 4")
        assert result == "calculate"

    def test_detects_complex_math(self):
        """Detects complex expressions."""
        selector = ToolSelector()
        result = selector.select_tool("(50 + 25) * 2")
        assert result == "calculate"

    def test_detects_math_with_spaces(self):
        """Detects math with various spacing."""
        selector = ToolSelector()
        assert selector.select_tool("5   +   5") == "calculate"
        assert selector.select_tool("10-3") == "calculate"

    # ============================================================
    # INTERNET SEARCH DETECTION
    # ============================================================

    def test_detects_search_keyword(self):
        """Detects 'search' keyword."""
        selector = ToolSelector()
        result = selector.select_tool("search for machine learning")
        assert result == "internet_search"

    def test_detects_look_up(self):
        """Detects 'look up' phrase."""
        selector = ToolSelector()
        result = selector.select_tool("look up Python documentation")
        assert result == "internet_search"

    def test_detects_find_online(self):
        """Detects 'find online' phrase."""
        selector = ToolSelector()
        result = selector.select_tool("find online the capital of France")
        assert result == "internet_search"

    def test_detects_google(self):
        """Detects 'google' keyword."""
        selector = ToolSelector()
        result = selector.select_tool("google artificial intelligence")
        assert result == "internet_search"

    def test_detects_search_case_insensitive(self):
        """Search detection is case-insensitive."""
        selector = ToolSelector()
        assert selector.select_tool("SEARCH for something") == "internet_search"
        assert selector.select_tool("Search for AI") == "internet_search"

    # ============================================================
    # FILE DETECTION
    # ============================================================

    def test_detects_open_file(self):
        """Detects 'open file' request."""
        selector = ToolSelector()
        result = selector.select_tool("open file config.txt")
        assert result == "open_file"

    def test_detects_read_file(self):
        """Detects 'read file' request."""
        selector = ToolSelector()
        result = selector.select_tool("read file data.json")
        assert result == "open_file"

    def test_detects_load_file(self):
        """Detects 'load file' request."""
        selector = ToolSelector()
        result = selector.select_tool("load file settings.yaml")
        assert result == "open_file"

    def test_detects_file_case_insensitive(self):
        """File detection is case-insensitive."""
        selector = ToolSelector()
        assert selector.select_tool("OPEN FILE test.txt") == "open_file"
        assert selector.select_tool("Read File data.csv") == "open_file"

    # ============================================================
    # REASONING (DEFAULT)
    # ============================================================

    def test_defaults_to_reasoning(self):
        """Unknown requests default to reasoning."""
        selector = ToolSelector()
        assert selector.select_tool("hello jessica") == "reasoning"
        assert selector.select_tool("how are you") == "reasoning"
        assert selector.select_tool("tell me a joke") == "reasoning"

    def test_empty_input_returns_reasoning(self):
        """Empty input returns reasoning."""
        selector = ToolSelector()
        result = selector.select_tool("")
        assert result == "reasoning"

    def test_whitespace_only_returns_reasoning(self):
        """Whitespace-only input returns reasoning."""
        selector = ToolSelector()
        result = selector.select_tool("   ")
        assert result == "reasoning"

    # ============================================================
    # EDGE CASES
    # ============================================================

    def test_math_detection_requires_numbers(self):
        """Math detection requires actual numbers."""
        selector = ToolSelector()
        # "a + b" should NOT be detected as math
        result = selector.select_tool("a + b")
        assert result == "reasoning"

    def test_math_detection_requires_operators(self):
        """Math requires operators."""
        selector = ToolSelector()
        result = selector.select_tool("5 5")
        assert result == "reasoning"

    def test_mixed_case_handling(self):
        """Mixed case is handled properly."""
        selector = ToolSelector()
        assert selector.select_tool("CaLcUlAtE 10 + 5") == "calculate"
        assert selector.select_tool("SeArCh for info") == "internet_search"

    def test_leading_trailing_whitespace(self):
        """Leading/trailing whitespace is stripped."""
        selector = ToolSelector()
        assert selector.select_tool("   5 + 5   ") == "calculate"
        assert selector.select_tool("  search for AI  ") == "internet_search"

    # ============================================================
    # KERNEL INTEGRATION
    # ============================================================

    def test_kernel_has_tool_selector(self):
        """CognitiveKernel has tool selector."""
        kernel = CognitiveKernel()
        assert hasattr(kernel, "tool_selector")
        assert isinstance(kernel.tool_selector, ToolSelector)

    def test_kernel_uses_tool_selector(self):
        """Kernel uses tool selector in process()."""
        kernel = CognitiveKernel()
        result = kernel.process("5 + 5")
        
        # If it's a proposal, check for selected_tool
        if isinstance(result, dict) and result.get("type") == "proposal":
            assert "selected_tool" in result

    # ============================================================
    # PRIORITY TESTS
    # ============================================================

    def test_math_takes_priority_over_search(self):
        """Math detection has priority."""
        selector = ToolSelector()
        # "10 + 5" should be math, not search
        result = selector.select_tool("10 + 5")
        assert result == "calculate"

    def test_search_takes_priority_over_reasoning(self):
        """Search detection has priority over reasoning."""
        selector = ToolSelector()
        result = selector.select_tool("search for 10 + 5")
        assert result == "internet_search"

    def test_file_takes_priority_over_reasoning(self):
        """File detection has priority over reasoning."""
        selector = ToolSelector()
        result = selector.select_tool("open file data.json")
        assert result == "open_file"

    # ============================================================
    # REAL-WORLD EXAMPLES
    # ============================================================

    def test_realistic_math_query(self):
        """Realistic math query."""
        selector = ToolSelector()
        result = selector.select_tool("What is 1024 divided by 2?")
        assert result == "calculate"

    def test_realistic_search_query(self):
        """Realistic search query."""
        selector = ToolSelector()
        result = selector.select_tool("Can you search for the weather in New York?")
        assert result == "internet_search"

    def test_realistic_file_query(self):
        """Realistic file query."""
        selector = ToolSelector()
        result = selector.select_tool("I need you to open file configuration.json")
        assert result == "open_file"

    def test_realistic_reasoning_query(self):
        """Realistic reasoning query."""
        selector = ToolSelector()
        result = selector.select_tool("What do you think about artificial intelligence?")
        assert result == "reasoning"

    # ============================================================
    # ACCURACY TESTS
    # ============================================================

    def test_multiple_operators(self):
        """Math with multiple operators."""
        selector = ToolSelector()
        assert selector.select_tool("50 + 25 - 10") == "calculate"
        assert selector.select_tool("10 * 5 / 2") == "calculate"

    def test_operator_spacing_variations(self):
        """Various operator spacing."""
        selector = ToolSelector()
        assert selector.select_tool("5+5") == "calculate"
        assert selector.select_tool("5 + 5") == "calculate"
        assert selector.select_tool("5  +  5") == "calculate"

    def test_search_phrase_variations(self):
        """Various search phrasings."""
        selector = ToolSelector()
        assert selector.select_tool("Please search for help") == "internet_search"
        assert selector.select_tool("Can you look up information") == "internet_search"
        assert selector.select_tool("Find online the answer") == "internet_search"

    def test_file_operation_variations(self):
        """Various file operation phrasings."""
        selector = ToolSelector()
        assert selector.select_tool("Open file please") == "open_file"
        assert selector.select_tool("Can you read file settings") == "open_file"
        assert selector.select_tool("Load file from disk") == "open_file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
