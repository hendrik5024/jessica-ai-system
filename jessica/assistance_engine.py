"""Phase 12 — Operational Assistance Layer: assistance engine."""

from __future__ import annotations

from typing import List

from jessica.task_session import TaskSession


class AssistanceEngine:
    """Deterministic assistance suggestion engine (no execution)."""

    def generate_assistance(self, session: TaskSession) -> List[str]:
        suggestions: List[str] = []
        if session.active_tasks:
            suggestions.append(f"You have {len(session.active_tasks)} active task(s).")
        else:
            suggestions.append("No active tasks are currently tracked.")

        if session.context_notes:
            suggestions.append("I can summarize your latest notes if you'd like.")
        else:
            suggestions.append("You can add context notes to track session details.")

        return suggestions

    def suggest_next_steps(self, session: TaskSession) -> List[str]:
        if session.active_tasks:
            return [f"Next, consider: {session.active_tasks[0]}"]
        return ["Next, consider defining a task to work on."]

    def summarize_session_progress(self, session: TaskSession) -> str:
        return (
            f"Session has {len(session.active_tasks)} active task(s) and "
            f"{len(session.context_notes)} note(s)."
        )
