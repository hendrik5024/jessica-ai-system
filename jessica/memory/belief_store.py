"""
Phase 98.8: Belief Store - Core Truth System for Jessica

BeliefStore maintains Jessica's core beliefs that override all other systems:
- User information (name, age, creator)
- Jessica's identity (name, purpose)
- Established facts from conversation

These beliefs ALWAYS win over model responses.
"""

from typing import Any, Dict, Optional


class BeliefStore:
    """
    Stores and manages core beliefs that take absolute priority.
    
    Beliefs are truths that override all other systems:
    - Model responses cannot contradict them
    - They persist across processing
    - They are the source of truth for the system
    """
    
    def __init__(self):
        """Initialize belief store with no prior beliefs."""
        self.beliefs: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a belief as a core truth.
        
        Args:
            key: Belief identifier (e.g., "user_name", "creator")
            value: The belief content
        """
        self.beliefs[key] = value
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a stored belief.
        
        Args:
            key: Belief identifier
            
        Returns:
            The belief value, or None if not found
        """
        return self.beliefs.get(key)
    
    def has(self, key: str) -> bool:
        """
        Check if a belief exists.
        
        Args:
            key: Belief identifier
            
        Returns:
            True if belief exists, False otherwise
        """
        return key in self.beliefs
    
    def all(self) -> Dict[str, Any]:
        """
        Get all stored beliefs.
        
        Returns:
            Dictionary of all beliefs
        """
        return dict(self.beliefs)
    
    def clear(self) -> None:
        """Clear all beliefs."""
        self.beliefs.clear()
    
    def delete(self, key: str) -> bool:
        """
        Delete a specific belief.
        
        Args:
            key: Belief identifier
            
        Returns:
            True if deleted, False if didn't exist
        """
        if key in self.beliefs:
            del self.beliefs[key]
            return True
        return False
    
    def update(self, beliefs_dict: Dict[str, Any]) -> None:
        """
        Update multiple beliefs at once.
        
        Args:
            beliefs_dict: Dictionary of beliefs to add/update
        """
        self.beliefs.update(beliefs_dict)

    def set_fact(self, key: str, value: Any) -> None:
        """Store a dynamic fact for general memory reasoning."""
        if not hasattr(self, "facts"):
            self.facts: Dict[str, Any] = {}
        self.facts[key] = value

    def get_fact(self, key: str) -> Optional[Any]:
        """Retrieve a dynamic fact by key."""
        if hasattr(self, "facts"):
            return self.facts.get(key)
        return None

    def get_all_facts(self) -> Dict[str, Any]:
        """Return all dynamic facts."""
        if hasattr(self, "facts"):
            return dict(self.facts)
        return {}
    
    def __len__(self) -> int:
        """Return number of stored beliefs."""
        return len(self.beliefs)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for checking belief existence."""
        return key in self.beliefs
    
    def __repr__(self) -> str:
        """String representation of BeliefStore."""
        return f"BeliefStore(beliefs={len(self.beliefs)})"
    
    def has_memory(self) -> bool:
        """Check if any beliefs are stored."""
        return len(self.beliefs) > 0
    
    def __str__(self) -> str:
        """Human-readable representation of BeliefStore."""
        if not self.beliefs:
            return "BeliefStore (empty)"
        
        lines = ["BeliefStore:"]
        for key, value in self.beliefs.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
