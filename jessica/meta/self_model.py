from __future__ import annotations

import json
import os
import time
from typing import Any, Dict


class SelfModelManager:
    """Identity self-model with weekly updates from Meta-Memory summaries."""

    def __init__(self, memory_store, model_path: str | None = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(os.path.dirname(base_dir), "data", "self_model.json")
        self.model_path = model_path or default_path
        self.memory_store = memory_store
        self._ensure_model()

    def _ensure_model(self) -> None:
        if not os.path.isfile(self.model_path):
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "w", encoding="utf-8") as f:
                json.dump(self._default_model(), f, indent=2)

    def _default_model(self) -> Dict[str, Any]:
        return {
            "role": "Personal AI Companion & Assistant",
            "strengths": ["organization", "empathy", "technical reasoning"],
            "weaknesses": ["long-horizon planning", "humor timing"],
            "current_focus": "improving proactive assistance",
            "confidence_trend": "stable",
            "last_updated_ts": 0,
            "last_avg_confidence": 0.0,
            "recent_summary": "",
        }

    def load(self) -> Dict[str, Any]:
        self._ensure_model()
        try:
            with open(self.model_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._default_model()

    def save(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def update_if_due(self, days: int = 7) -> Dict[str, Any]:
        data = self.load()
        last_ts = int(data.get("last_updated_ts", 0) or 0)
        now = int(time.time())
        if (now - last_ts) < (days * 86400):
            return data

        summary = self.memory_store.get_meta_summary(days=days)
        if summary.get("count", 0) == 0:
            data["last_updated_ts"] = now
            data["recent_summary"] = "No recent meta observations."
            self.save(data)
            return data

        prev_avg = float(data.get("last_avg_confidence", 0.0) or 0.0)
        avg_conf = float(summary.get("avg_confidence", 0.0) or 0.0)
        delta = avg_conf - prev_avg

        if delta >= 0.05:
            trend = "increasing"
        elif delta <= -0.05:
            trend = "decreasing"
        else:
            trend = "stable"

        top_model = summary.get("top_model") or "unknown"
        memory_rate = summary.get("memory_use_rate", 0.0)
        follow_rate = summary.get("followup_rate", 0.0)

        data["confidence_trend"] = trend
        data["last_updated_ts"] = now
        data["last_avg_confidence"] = avg_conf
        data["recent_summary"] = (
            f"Last {days}d: avg_conf={avg_conf:.2f}, memory_use={memory_rate:.2f}, "
            f"followups={follow_rate:.2f}, top_model={top_model}."
        )

        if summary.get("top_improvement"):
            data["current_focus"] = summary["top_improvement"]

        self.save(data)
        return data

    def get_prompt_excerpt(self) -> str:
        data = self.load()
        strengths = ", ".join(data.get("strengths", [])) or "None"
        weaknesses = ", ".join(data.get("weaknesses", [])) or "None"
        focus = data.get("current_focus", "")
        trend = data.get("confidence_trend", "stable")
        role = data.get("role", "")

        return (
            "Self-model (identity, internal):\n"
            f"- Role: {role}\n"
            f"- Strengths: {strengths}\n"
            f"- Weaknesses: {weaknesses}\n"
            f"- Current focus: {focus}\n"
            f"- Confidence trend: {trend}\n"
            "Use this to shape the reply and, when appropriate, add one short line such as: "
            "'Based on my current strengths, I should ...'"
        )
