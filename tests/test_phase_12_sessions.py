from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.task_session import TaskSession, SessionStatus, create_session
from jessica.session_registry import SessionRegistry
from jessica.session_manager import SessionManager
from jessica.assistance_engine import AssistanceEngine


def _session():
    return create_session(
        session_id="s1",
        user_id="u1",
        start_time=datetime(2026, 2, 9, 10, 0, 0),
        active_tasks=["task a"],
        context_notes=["note a"],
        status=SessionStatus.ACTIVE,
    )


def test_session_immutable():
    session = _session()
    with pytest.raises(FrozenInstanceError):
        session.user_id = "u2"


def test_start_session_defaults():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s2", start_time=datetime(2026, 2, 9, 11, 0, 0))
    assert session.status == SessionStatus.ACTIVE


def test_pause_and_resume():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s3", start_time=datetime(2026, 2, 9, 11, 0, 0))
    paused = manager.pause_session(session.session_id)
    assert paused.status == SessionStatus.PAUSED
    resumed = manager.resume_session(session.session_id)
    assert resumed.status == SessionStatus.ACTIVE


def test_pause_no_effect_if_not_active():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s4", start_time=datetime(2026, 2, 9, 11, 0, 0))
    closed = manager.close_session(session.session_id)
    assert manager.pause_session(closed.session_id).status == SessionStatus.CLOSED


def test_close_session():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s5", start_time=datetime(2026, 2, 9, 11, 0, 0))
    closed = manager.close_session(session.session_id)
    assert closed.status == SessionStatus.CLOSED


def test_add_note_appends():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s6", start_time=datetime(2026, 2, 9, 11, 0, 0))
    updated = manager.add_note(session.session_id, "note")
    assert updated.context_notes[-1] == "note"


def test_list_active_tasks():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s7", start_time=datetime(2026, 2, 9, 11, 0, 0))
    assert manager.list_active_tasks(session.session_id) == []


def test_registry_append_only():
    registry = SessionRegistry()
    session = _session()
    registry.register_session(session)
    registry.register_session(session)
    assert registry.history_count(session.session_id) == 2


def test_registry_get_session():
    registry = SessionRegistry()
    session = _session()
    registry.register_session(session)
    assert registry.get_session("s1") == session


def test_registry_list_active_sessions():
    registry = SessionRegistry()
    registry.register_session(_session())
    assert len(registry.list_active_sessions()) == 1


def test_registry_excludes_closed():
    registry = SessionRegistry()
    session = create_session(
        session_id="s8",
        user_id="u1",
        start_time=datetime(2026, 2, 9, 10, 0, 0),
        status=SessionStatus.CLOSED,
    )
    registry.register_session(session)
    assert registry.list_active_sessions() == []


def test_assistance_no_execution():
    engine = AssistanceEngine()
    suggestions = engine.generate_assistance(_session())
    assert all("execute" not in s.lower() for s in suggestions)


def test_assistance_deterministic():
    engine = AssistanceEngine()
    session = _session()
    assert engine.generate_assistance(session) == engine.generate_assistance(session)


def test_suggest_next_steps_with_tasks():
    engine = AssistanceEngine()
    session = _session()
    steps = engine.suggest_next_steps(session)
    assert steps[0].startswith("Next, consider:")


def test_suggest_next_steps_no_tasks():
    engine = AssistanceEngine()
    session = create_session(
        session_id="s9",
        user_id="u1",
        start_time=datetime(2026, 2, 9, 10, 0, 0),
        status=SessionStatus.ACTIVE,
    )
    steps = engine.suggest_next_steps(session)
    assert steps == ["Next, consider defining a task to work on."]


def test_summarize_progress():
    engine = AssistanceEngine()
    session = _session()
    summary = engine.summarize_session_progress(session)
    assert "1 active task" in summary


def test_pause_unknown_session():
    manager = SessionManager()
    with pytest.raises(ValueError):
        manager.pause_session("unknown")


def test_resume_unknown_session():
    manager = SessionManager()
    with pytest.raises(ValueError):
        manager.resume_session("unknown")


def test_close_unknown_session():
    manager = SessionManager()
    with pytest.raises(ValueError):
        manager.close_session("unknown")


def test_add_note_unknown_session():
    manager = SessionManager()
    with pytest.raises(ValueError):
        manager.add_note("unknown", "note")


def test_session_status_transitions_deterministic():
    manager = SessionManager()
    session = manager.start_session("u1", session_id="s10", start_time=datetime(2026, 2, 9, 11, 0, 0))
    paused = manager.pause_session(session.session_id)
    resumed = manager.resume_session(session.session_id)
    closed = manager.close_session(session.session_id)
    assert paused.status == SessionStatus.PAUSED
    assert resumed.status == SessionStatus.ACTIVE
    assert closed.status == SessionStatus.CLOSED
