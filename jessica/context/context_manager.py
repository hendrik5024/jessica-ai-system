"""
Phase 98.7: Context Manager

Manages conversation history and short-term memory.
Keeps Jessica aware of previous messages and answers.
"""

from collections import deque
from typing import List, Dict, Any


class ContextManager:
    """
    Manages conversation history and context.
    
    Purpose:
    - Store recent conversation turns
    - Provide context to reasoning engine
    - Enable multi-turn continuity
    - Allow Jessica to reference previous answers
    """

    def __init__(self, max_history: int = 10):
        """
        Initialize context manager.
        
        Args:
            max_history: Maximum number of turns to keep (default 10)
        """
        self.history = deque(maxlen=max_history)

    def add_turn(self, user_input: str, response: str) -> None:
        """
        Add a complete turn (user input + assistant response) to history.
        
        Args:
            user_input: What the user said
            response: What Jessica responded
        """
        self.history.append({
            "user": user_input,
            "assistant": response
        })

    def get_recent_context(self) -> List[Dict[str, str]]:
        """
        Get all recent conversation history.
        
        Returns:
            List of turns with user and assistant messages
        """
        return list(self.history)

    def get_last_context(self, depth: int = 1) -> Dict[str, Any]:
        """
        Get the last N turns from history.
        
        Args:
            depth: How many turns back (1 = last turn, 2 = last 2 turns)
            
        Returns:
            Most recent turn(s)
        """
        if not self.history or depth < 1:
            return {}
        
        if depth == 1:
            return dict(self.history[-1]) if self.history else {}
        
        # Return multiple turns
        start_idx = max(0, len(self.history) - depth)
        return list(self.history)[start_idx:]

    def search_context(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search history for turns containing a keyword.
        
        Args:
            keyword: What to search for
            
        Returns:
            All turns matching the keyword
        """
        keyword_lower = keyword.lower()
        matches = []
        
        for turn in self.history:
            if (keyword_lower in turn.get("user", "").lower() or
                keyword_lower in turn.get("assistant", "").lower()):
                matches.append(turn)
        
        return matches

    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()

    def has_memory(self) -> bool:
        """Check if there's any conversation history."""
        return len(self.history) > 0

    def __len__(self) -> int:
        """Return number of turns in history."""
        return len(self.history)

    def __repr__(self) -> str:
        """String representation."""
        return f"ContextManager(size={len(self.history)}, max={self.history.maxlen})"
