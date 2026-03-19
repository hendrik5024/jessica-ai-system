"""
Proactive nudger for Jessica.
Uses idle signals and context to surface gentle check-ins instead of pure request/response.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Optional


class ProactiveNudger:
    def __init__(
        self,
        min_idle_seconds: int = 1200,  # 20 minutes
        nudge_cooldown_seconds: int = 3600,
        quiet_hours: tuple[int, int] = (22, 7),
    ):
        self.min_idle_seconds = min_idle_seconds
        self.nudge_cooldown_seconds = nudge_cooldown_seconds
        self.quiet_hours = quiet_hours
        self.last_nudge_ts = 0.0

    def _within_quiet_hours(self) -> bool:
        start, end = self.quiet_hours
        hour = datetime.now().hour
        if start > end:
            return hour >= start or hour < end
        return start <= hour < end

    def maybe_idle_nudge(self, system_state, context_manager) -> Optional[dict]:
        now = time.time()
        if (now - self.last_nudge_ts) < self.nudge_cooldown_seconds:
            return None
        if self._within_quiet_hours():
            return None

        idle_seconds = max(system_state.keyboard_idle_seconds, system_state.mouse_idle_seconds)
        if idle_seconds < self.min_idle_seconds:
            return None

        context = context_manager.profile.get_context_suggestion()
        current_app = context.get("current_app")
        likely_next = context.get("likely_next_apps") or []

        message = "Hey, I noticed a pause—want a quick hint or related doc I found?"
        if current_app:
            message = f"You've been away from {current_app} for a bit—want me to surface a quick reference or recent logs?"
        elif likely_next:
            message = f"Quick nudge: I can pull references for {likely_next[0]} if you like."

        self.last_nudge_ts = now
        return {
            "message": message,
            "context": context,
            "idle_seconds": idle_seconds,
        }
