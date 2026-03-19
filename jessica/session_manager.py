"""Phase 12 — Operational Assistance Layer: session manager."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from jessica.task_session import TaskSession, SessionStatus, create_session
from jessica.session_registry import SessionRegistry


class SessionManager:
    def __init__(self, registry: Optional[SessionRegistry] = None) -> None:
        self.registry = registry or SessionRegistry()

    def start_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
    ) -> TaskSession:
        start_time = start_time or datetime.now()
        session_id = session_id or f"session_{start_time.strftime('%Y%m%d%H%M%S%f')}"
        session = create_session(
            session_id=session_id,
            user_id=user_id,
            start_time=start_time,
            status=SessionStatus.ACTIVE,
        )
        self.registry.register_session(session)
        return session

    def pause_session(self, session_id: str) -> TaskSession:
        current = self.registry.get_session(session_id)
        if not current:
            raise ValueError("Session not found")
        if current.status != SessionStatus.ACTIVE:
            return current
        updated = create_session(
            session_id=current.session_id,
            user_id=current.user_id,
            start_time=current.start_time,
            active_tasks=current.active_tasks,
            context_notes=current.context_notes,
            status=SessionStatus.PAUSED,
        )
        self.registry.register_session(updated)
        return updated

    def resume_session(self, session_id: str) -> TaskSession:
        current = self.registry.get_session(session_id)
        if not current:
            raise ValueError("Session not found")
        if current.status != SessionStatus.PAUSED:
            return current
        updated = create_session(
            session_id=current.session_id,
            user_id=current.user_id,
            start_time=current.start_time,
            active_tasks=current.active_tasks,
            context_notes=current.context_notes,
            status=SessionStatus.ACTIVE,
        )
        self.registry.register_session(updated)
        return updated

    def close_session(self, session_id: str) -> TaskSession:
        current = self.registry.get_session(session_id)
        if not current:
            raise ValueError("Session not found")
        if current.status == SessionStatus.CLOSED:
            return current
        updated = create_session(
            session_id=current.session_id,
            user_id=current.user_id,
            start_time=current.start_time,
            active_tasks=current.active_tasks,
            context_notes=current.context_notes,
            status=SessionStatus.CLOSED,
        )
        self.registry.register_session(updated)
        return updated

    def add_note(self, session_id: str, note: str) -> TaskSession:
        current = self.registry.get_session(session_id)
        if not current:
            raise ValueError("Session not found")
        notes = list(current.context_notes)
        if note:
            notes.append(note)
        updated = create_session(
            session_id=current.session_id,
            user_id=current.user_id,
            start_time=current.start_time,
            active_tasks=current.active_tasks,
            context_notes=notes,
            status=current.status,
        )
        self.registry.register_session(updated)
        return updated

    def list_active_tasks(self, session_id: str) -> list[str]:
        current = self.registry.get_session(session_id)
        if not current:
            raise ValueError("Session not found")
        return list(current.active_tasks)
