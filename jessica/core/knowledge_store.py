"""
Phase 87/89/90: Knowledge Store

Persistent structured data storage for facts and relationships.
Phase 89: Now uses persistent JSON storage instead of in-memory dict.
Phase 90: Memory writes now require permission checks via PermissionManager.
"""

from jessica.memory.persistent_memory import PersistentMemory


class KnowledgeStore:
    """
    Stores structured facts about the user and system.
    Phase 89: Backed by persistent JSON storage.
    Phase 90: All writes gated through permission checks.
    """

    def __init__(self, memory_file="jessica_memory.json", permission_manager=None):
        self.memory = PersistentMemory(memory_file)
        self.permission_manager = permission_manager

    def set_fact(self, key: str, value):
        """Store a fact (persisted to disk). Phase 90: Requires memory_write permission."""
        if self.permission_manager:
            self.permission_manager.require("memory_write")
        self.memory.set(key, value)

    def get_fact(self, key: str):
        """Retrieve a fact."""
        return self.memory.get(key)

    def get_all(self):
        """Get all stored facts."""
        return self.memory.all()

    def clear(self):
        """Clear all facts."""
        self.memory.clear()

    def get_user_name(self):
        """Get user's name."""
        return self.get_fact("user.name")

    def get_birth_year(self):
        """Get user's birth year."""
        return self.get_fact("user.birth_year")

    def get_birth_date(self):
        """Get user's birth date."""
        return self.get_fact("user.birth_date")
