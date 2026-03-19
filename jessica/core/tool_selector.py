"""
Phase 95: Tool Selection Engine

Decides which capability Jessica should use
based on user intent.

This is NOT keyword matching.
This is structured reasoning.
"""

import re


class ToolSelector:
    """
    Determines what action Jessica should take.

    Output:
        "calculate"
        "internet_search"
        "open_file"
        "reasoning"
        None
    """

    def select_tool(self, user_input: str) -> str | None:
        text = user_input.lower().strip()

        # --- INTERNET SEARCH (Check first - explicit user intent) ---
        if self._is_search(text):
            return "internet_search"

        # --- FILE ACCESS (Check before math) ---
        if self._is_file_request(text):
            return "open_file"

        # --- MATH DETECTION ---
        if self._is_math(text):
            return "calculate"

        # --- DEFAULT ---
        return "reasoning"

    # -------------------------

    def _is_math(self, text: str) -> bool:
        # Detect numbers with symbol operators (+, -, *, /)
        if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", text):
            return True
        
        # Detect numbers with word-based operators
        word_operators = r"\b(\d+)\s+(plus|minus|times|divided by|multiplied by)\s+(\d+)\b"
        if re.search(word_operators, text):
            return True
        
        return False

    def _is_search(self, text: str) -> bool:
        keywords = ["search", "look up", "find online", "google"]
        return any(k in text for k in keywords)

    def _is_file_request(self, text: str) -> bool:
        keywords = ["open file", "read file", "load file"]
        return any(k in text for k in keywords)
