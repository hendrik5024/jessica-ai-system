"""Phase 12 — Operational Assistance Layer: task session structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass(frozen=True)
class TaskSession:
    session_id: str
    user_id: str
    start_time: datetime
    active_tasks: List[str]
    context_notes: List[str]
    status: SessionStatus


def create_session(
    session_id: str,
    user_id: str,
    start_time: datetime,
    active_tasks: List[str] | None = None,
    context_notes: List[str] | None = None,
    status: SessionStatus = SessionStatus.ACTIVE,
) -> TaskSession:
    return TaskSession(
        session_id=session_id,
        user_id=user_id,
        start_time=start_time,
        active_tasks=list(active_tasks or []),
        context_notes=list(context_notes or []),
        status=status,
    )
