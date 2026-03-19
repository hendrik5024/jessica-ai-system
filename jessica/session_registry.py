"""Phase 12 — Operational Assistance Layer: append-only session registry."""

from __future__ import annotations

from typing import Dict, List

from jessica.task_session import TaskSession, SessionStatus


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: Dict[str, List[TaskSession]] = {}
        self._order: List[str] = []

    def register_session(self, session: TaskSession) -> None:
        if session.session_id not in self._sessions:
            self._sessions[session.session_id] = []
            self._order.append(session.session_id)
        self._sessions[session.session_id].append(session)

    def get_session(self, session_id: str) -> TaskSession | None:
        history = self._sessions.get(session_id)
        if not history:
            return None
        return history[-1]

    def list_active_sessions(self) -> List[TaskSession]:
        active: List[TaskSession] = []
        for session_id in self._order:
            current = self.get_session(session_id)
            if current and current.status in (SessionStatus.ACTIVE, SessionStatus.PAUSED):
                active.append(current)
        return active

    def history_count(self, session_id: str) -> int:
        history = self._sessions.get(session_id)
        return len(history) if history else 0
