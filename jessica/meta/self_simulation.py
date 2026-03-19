from __future__ import annotations

from typing import Any, Dict, List


class SelfSimulationEngine:
    """Simulate action trajectories and choose the safest/best path."""

    def __init__(self, enabled: bool = True, threshold: float = 0.55) -> None:
        self.enabled = enabled
        self.threshold = threshold

    def choose_trajectory(
        self,
        *,
        action: Dict[str, Any],
        user_text: str,
        model_text: str,
        intent: Dict[str, Any] | str,
        confidence: float,
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "decision": "proceed",
                "reason": "simulation_disabled",
                "trajectories": [],
            }

        intent_label = intent.get("intent") if isinstance(intent, dict) else str(intent)
        risk = self._estimate_risk(action)
        needs_details = self._needs_details(user_text)
        user_explicit = self._user_explicitly_requested_action(user_text)

        trajectories = [
            self._score_execute(confidence, risk, user_explicit),
            self._score_clarify(confidence, needs_details),
            self._score_defer(confidence, risk, intent_label),
        ]

        trajectories = sorted(trajectories, key=lambda t: t["score"], reverse=True)
        best = trajectories[0]

        return {
            "decision": best["decision"],
            "reason": best["reason"],
            "trajectories": trajectories,
        }

    # -------------------------------------------------
    # Scoring
    # -------------------------------------------------
    def _score_execute(self, confidence: float, risk: float, user_explicit: bool) -> Dict[str, Any]:
        score = 0.5 + (confidence * 0.3) - (risk * 0.4) + (0.15 if user_explicit else 0.0)
        return {
            "decision": "proceed",
            "score": round(score, 3),
            "reason": "execute_action",
        }

    def _score_clarify(self, confidence: float, needs_details: bool) -> Dict[str, Any]:
        score = 0.45 + ((self.threshold - confidence) * 0.35) + (0.15 if needs_details else 0.0)
        return {
            "decision": "clarify",
            "score": round(score, 3),
            "reason": "need_clarification",
        }

    def _score_defer(self, confidence: float, risk: float, intent_label: str) -> Dict[str, Any]:
        score = 0.25 + ((self.threshold - confidence) * 0.25) + (risk * 0.45)
        if intent_label in {"code", "chat"}:
            score -= 0.05
        return {
            "decision": "defer",
            "score": round(score, 3),
            "reason": "risk_or_low_confidence",
        }

    # -------------------------------------------------
    # Heuristics
    # -------------------------------------------------
    def _estimate_risk(self, action: Dict[str, Any]) -> float:
        if action.get("action") != "terminal":
            return 0.2

        cmd = (action.get("cmd") or "").lower()
        high_risk = ["rm ", "del ", "rmdir", "format", "shutdown", "reboot", "erase", "diskpart", "mkfs"]
        if any(tok in cmd for tok in high_risk):
            return 0.95

        read_only = ["dir", "ls", "cat ", "type ", "python -m pytest", "git status", "git diff"]
        if any(tok in cmd for tok in read_only):
            return 0.15

        return 0.45

    def _needs_details(self, user_text: str) -> bool:
        t = (user_text or "").lower().strip()
        if len(t.split()) < 6:
            return True
        vague = {"it", "that", "this", "they", "them", "something"}
        return any(token in vague for token in t.split())

    def _user_explicitly_requested_action(self, user_text: str) -> bool:
        t = (user_text or "").lower()
        markers = ["run", "execute", "launch", "start", "open", "build", "test", "install"]
        return any(m in t for m in markers)

    # -------------------------------------------------
    # Responses
    # -------------------------------------------------
    def build_block_response(self, decision: str, action: Dict[str, Any]) -> str:
        if decision == "clarify":
            return "Before I run that, can you confirm the exact action and any constraints?"
        if decision == "defer":
            return "I’m not confident enough to run that yet. Please add more context or confirm the intent."
        return ""
