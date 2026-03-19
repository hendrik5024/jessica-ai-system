"""Phase 9.5 — Identity Model Layer."""

from __future__ import annotations

from typing import Optional

from jessica.memory.knowledge_memory import KnowledgeMemory


class IdentityModel:
    """Deterministic identity model backed by structured knowledge memory."""

    def __init__(self, memory: KnowledgeMemory):
        self.memory = memory

    def get_user_name(self) -> Optional[str]:
        return self.memory.recall("fact:user_name")

    def get_assistant_name(self) -> str:
        stored = self.memory.recall("fact:assistant_name")
        return stored if stored else "Jessica"

    def describe_self(self) -> str:
        assistant_name = self.get_assistant_name()
        return (
            f"I am {assistant_name}, your offline AI assistant designed to help you "
            "manage tasks, knowledge, and workflows."
        )

    def describe_user(self) -> str:
        user_name = self.get_user_name()
        if user_name:
            return f"Your name is {user_name}."
        return "I do not yet know your name."
