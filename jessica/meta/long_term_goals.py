from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List


class LongTermGoalsManager:
    """Maintain long-horizon motivational goals and update progress periodically."""

    def __init__(self, memory_store, goals_path: str | None = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(os.path.dirname(base_dir), "data", "long_term_goals.json")
        self.goals_path = goals_path or default_path
        self.memory_store = memory_store
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.isfile(self.goals_path):
            os.makedirs(os.path.dirname(self.goals_path), exist_ok=True)
            with open(self.goals_path, "w", encoding="utf-8") as f:
                json.dump(self._default_state(), f, indent=2)

    def _default_state(self) -> Dict[str, Any]:
        return {
            "interaction_count": 0,
            "last_update_ts": 0,
            "goals": [
                {
                    "goal": "Reduce user cognitive load",
                    "priority": 0.85,
                    "evidence": [],
                    "success_metric": "User completes tasks with fewer clarification turns",
                    "progress_score": 0.5,
                    "last_check_ts": 0,
                    "last_delta": 0.0,
                },
                {
                    "goal": "Anticipate needs earlier",
                    "priority": 0.8,
                    "evidence": [],
                    "success_metric": "Proactive suggestions accepted",
                    "progress_score": 0.5,
                    "last_check_ts": 0,
                    "last_delta": 0.0,
                },
                {
                    "goal": "Become more concise without losing warmth",
                    "priority": 0.75,
                    "evidence": [],
                    "success_metric": "Shorter responses with positive sentiment",
                    "progress_score": 0.5,
                    "last_check_ts": 0,
                    "last_delta": 0.0,
                },
            ],
        }

    def load(self) -> Dict[str, Any]:
        self._ensure_file()
        try:
            with open(self.goals_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._default_state()

    def save(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.goals_path), exist_ok=True)
        with open(self.goals_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def tick_interaction(self) -> Dict[str, Any]:
        data = self.load()
        data["interaction_count"] = int(data.get("interaction_count", 0) or 0) + 1
        self.save(data)
        return data

    def update_from_meta(self, meta: Dict[str, Any] | None, every_n: int = 5) -> Dict[str, Any]:
        if not meta:
            return self.load()

        data = self.load()
        count = int(data.get("interaction_count", 0) or 0)
        if count % max(1, every_n) != 0:
            return data

        now = int(time.time())
        response_text = str(meta.get("response_text", ""))
        response_len = int(meta.get("response_length", len(response_text)))
        followup_needed = bool(meta.get("followup_needed"))
        user_sentiment = str(meta.get("user_sentiment", "neutral"))

        for goal in data.get("goals", []):
            delta, evidence = self._evaluate_goal(
                goal=goal,
                response_text=response_text,
                response_len=response_len,
                followup_needed=followup_needed,
                user_sentiment=user_sentiment,
            )

            if delta == 0:
                continue

            progress = float(goal.get("progress_score", 0.5) or 0.5)
            progress = max(0.0, min(1.0, progress + delta))
            goal["progress_score"] = round(progress, 3)
            goal["last_delta"] = round(delta, 3)
            goal["last_check_ts"] = now

            if evidence:
                evidence_list: List[str] = list(goal.get("evidence", []))
                evidence_list.append(evidence)
                goal["evidence"] = evidence_list[-5:]

        data["last_update_ts"] = now
        self.save(data)
        return data

    def update_from_meta_batch(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not items:
            return self.load()

        data = self.load()
        now = int(time.time())

        for meta in items:
            response_text = str(meta.get("response_text", ""))
            response_len = int(meta.get("response_length", len(response_text)))
            followup_needed = bool(meta.get("followup_needed"))
            user_sentiment = str(meta.get("user_sentiment", "neutral"))

            for goal in data.get("goals", []):
                delta, evidence = self._evaluate_goal(
                    goal=goal,
                    response_text=response_text,
                    response_len=response_len,
                    followup_needed=followup_needed,
                    user_sentiment=user_sentiment,
                )

                if delta == 0:
                    continue

                progress = float(goal.get("progress_score", 0.5) or 0.5)
                progress = max(0.0, min(1.0, progress + delta))
                goal["progress_score"] = round(progress, 3)
                goal["last_delta"] = round(delta, 3)
                goal["last_check_ts"] = now

                if evidence:
                    evidence_list: List[str] = list(goal.get("evidence", []))
                    evidence_list.append(evidence)
                    goal["evidence"] = evidence_list[-5:]

        data["last_update_ts"] = now
        self.save(data)
        return data

    def _evaluate_goal(
        self,
        *,
        goal: Dict[str, Any],
        response_text: str,
        response_len: int,
        followup_needed: bool,
        user_sentiment: str,
    ) -> tuple[float, str | None]:
        goal_text = f"{goal.get('goal', '')} {goal.get('success_metric', '')}".lower()
        delta = 0.0
        evidence = None

        if "concise" in goal_text or "cognitive load" in goal_text:
            if response_len <= 600:
                delta = 0.05
                evidence = f"Conciseness ok (len={response_len})."
            else:
                delta = -0.03
                evidence = f"Too long (len={response_len})."

        if "anticipate" in goal_text or "proactive" in goal_text:
            proactive_markers = [
                "would you like", "i can also", "next step", "if you want", "want me to",
                "i can go ahead", "i can set up",
            ]
            if any(m in response_text.lower() for m in proactive_markers):
                delta = max(delta, 0.05)
                evidence = "Proactive suggestion offered."
            elif followup_needed:
                delta = max(delta, 0.02)
                evidence = "Follow-up invited."
            else:
                delta = min(delta, -0.02)
                evidence = "No proactive cue detected."

        if "warmth" in goal_text or "empathy" in goal_text:
            if user_sentiment in {"positive", "neutral-positive"}:
                delta = max(delta, 0.03)
                evidence = "User sentiment positive."
            elif user_sentiment in {"negative", "neutral-negative"}:
                delta = min(delta, -0.03)
                evidence = "User sentiment negative."

        return delta, evidence

    def get_prompt_excerpt(self, top_k: int = 3) -> str:
        data = self.load()
        goals = sorted(data.get("goals", []), key=lambda g: g.get("priority", 0), reverse=True)
        goals = goals[:top_k]
        if not goals:
            return ""

        lines = ["Long-term goals (motivations):"]
        for g in goals:
            score = g.get("progress_score", 0.0)
            delta = g.get("last_delta", 0.0)
            trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
            lines.append(f"- {g.get('goal')} (priority={g.get('priority', 0)}, trend={trend}, score={score})")
        lines.append("After responding, reflect briefly on whether progress moved closer or further.")
        return "\n".join(lines)
