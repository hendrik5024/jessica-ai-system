"""
Phase 91: Belief Store

Persistent storage for Jessica's beliefs.
All beliefs are grounded in memory and interactions.
"""

import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from jessica.beliefs.belief_record import BeliefRecord


class BeliefStore:
    """
    Stores and retrieves Jessica's beliefs.
    Beliefs persist to disk for cross-session consistency.
    """

    def __init__(self, path="jessica/data/beliefs.json"):
        """
        Initialize belief store.
        
        Args:
            path: Path to beliefs file (auto-created if missing)
        """
        self.path = Path(path)
        self.beliefs = self._load()

    def _load(self):
        """Load existing beliefs from disk."""
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        """Persist beliefs to disk."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.beliefs, f, indent=2)
        except IOError:
            pass  # Fail silently on write errors

    def add_belief(self, subject, predicate, value, confidence=1.0, source="memory"):
        """
        Add a new belief.
        
        Args:
            subject: What the belief is about (e.g., "user", "system")
            predicate: Property being asserted (e.g., "name", "creator")
            value: The actual value
            confidence: Certainty (0.0-1.0, default 1.0)
            source: Origin of belief (memory, reasoning, interaction, etc.)
        
        Returns:
            Dictionary representation of the belief
        """
        record = {
            "belief_id": str(uuid4()),
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "confidence": confidence,
            "source": source,
            "created_at": datetime.now().isoformat()
        }
        self.beliefs.append(record)
        self._save()
        return record

    def update_belief(self, subject, predicate, value, confidence=1.0, source="memory"):
        """
        Update a belief by replacing the value for subject/predicate.
        Creates new belief if doesn't exist.
        
        Args:
            subject: What the belief is about
            predicate: Property being updated
            value: New value
            confidence: New confidence level
            source: Origin of update
        
        Returns:
            Updated belief record
        """
        # Remove old belief if exists
        self.beliefs = [
            b for b in self.beliefs
            if not (b["subject"] == subject and b["predicate"] == predicate)
        ]
        # Add new belief
        return self.add_belief(subject, predicate, value, confidence, source)

    def query(self, subject=None, predicate=None):
        """
        Query beliefs by subject and/or predicate.
        
        Args:
            subject: Filter by subject (optional)
            predicate: Filter by predicate (optional)
        
        Returns:
            List of matching belief records
        """
        results = []
        for belief in self.beliefs:
            if subject and belief["subject"] != subject:
                continue
            if predicate and belief["predicate"] != predicate:
                continue
            results.append(belief)
        return results

    def get_belief(self, subject, predicate):
        """
        Get the most recent belief for a subject/predicate pair.
        
        Args:
            subject: What the belief is about
            predicate: Property being queried
        
        Returns:
            Belief record or None if not found
        """
        beliefs = self.query(subject, predicate)
        return beliefs[-1] if beliefs else None

    def get_all(self):
        """Get all beliefs."""
        return list(self.beliefs)

    def clear(self):
        """Clear all beliefs."""
        self.beliefs = []
        self._save()

    def remove_belief(self, belief_id):
        """
        Remove a specific belief by ID.
        
        Args:
            belief_id: ID of belief to remove
        """
        self.beliefs = [b for b in self.beliefs if b["belief_id"] != belief_id]
        self._save()

    def count(self):
        """Get total number of stored beliefs."""
        return len(self.beliefs)
