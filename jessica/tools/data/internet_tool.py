"""
Phase 94: Internet Tool

Web search functionality using browser integration.
"""

import webbrowser
from jessica.tools.base_tool import BaseTool


class InternetTool(BaseTool):
    """
    Search the internet using browser.

    Opens user's default browser with Google search query.
    High risk due to external network access.
    """

    name = "internet_search"
    description = "Search the internet"
    risk = "high"

    def execute(self, input_data):
        """
        Execute an internet search.

        Args:
            input_data: Search query string

        Returns:
            str: Success or error message
        """
        try:
            # Extract query from user input
            query = self._extract_query(input_data)

            if not query:
                return "No search query provided."

            # Open browser with Google search
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)

            return "Opened browser for search."
        except Exception as e:
            return f"Could not perform search: {str(e)}"

    def _extract_query(self, user_input):
        """
        Extract search query from user input.

        Strips common trigger phrases like "search for", "look up", etc.

        Args:
            user_input: Raw user input string

        Returns:
            str: Cleaned search query
        """
        if not user_input:
            return ""

        text = user_input.lower()

        # Remove common trigger phrases
        phrases = [
            "search internet for",
            "search for",
            "look up",
            "find",
            "google",
        ]

        for phrase in phrases:
            text = text.replace(phrase, "")

        return text.strip()
