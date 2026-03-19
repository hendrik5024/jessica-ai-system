from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List


class AlignmentTracker:
    """Tracks alignment between Jessica's self-model and user model over time."""

    def __init__(self, memory_store, alignment_path: str | None = None):
        self.memory_store = memory_store
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(base_dir), "data")
        self.alignment_path = alignment_path or os.path.join(data_dir, "alignment_state.json")
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.isfile(self.alignment_path):
            os.makedirs(os.path.dirname(self.alignment_path), exist_ok=True)
            with open(self.alignment_path, "w", encoding="utf-8") as f:
                json.dump(self._default_state(), f, indent=2)

    def _default_state(self) -> Dict[str, Any]:
        return {
            "last_update_ts": 0,
            "user_preference_snapshots": [],
            "self_model_snapshots": [],
            "drift_events": [],
            "adaptation_speed": 0.0,
            "mismatch_moments": [],
            "alignment_score": 0.5,
        }

    def load(self) -> Dict[str, Any]:
        self._ensure_file()
        try:
            with open(self.alignment_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._default_state()

    def save(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.alignment_path), exist_ok=True)
        with open(self.alignment_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def track_alignment(
        self,
        *,
        user_profile: Dict[str, Any],
        self_model: Dict[str, Any],
        meta_observation: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = self.load()
        now = int(time.time())

        user_snapshot = self._snapshot_user(user_profile, now)
        self_snapshot = self._snapshot_self(self_model, now)

        data["user_preference_snapshots"].append(user_snapshot)
        data["user_preference_snapshots"] = data["user_preference_snapshots"][-20:]

        data["self_model_snapshots"].append(self_snapshot)
        data["self_model_snapshots"] = data["self_model_snapshots"][-20:]

        drift_detected = self._detect_drift(data["user_preference_snapshots"])
        if drift_detected:
            data["drift_events"].append(drift_detected)
            data["drift_events"] = data["drift_events"][-10:]

        adaptation_speed = self._measure_adaptation_speed(
            data["user_preference_snapshots"],
            data["self_model_snapshots"],
        )
        data["adaptation_speed"] = round(adaptation_speed, 3)

        mismatch = self._detect_mismatch(meta_observation, user_snapshot, self_snapshot)
        if mismatch:
            data["mismatch_moments"].append(mismatch)
            data["mismatch_moments"] = data["mismatch_moments"][-20:]

        data["alignment_score"] = self._compute_alignment_score(
            data["user_preference_snapshots"],
            data["self_model_snapshots"],
            data["mismatch_moments"],
        )

        data["last_update_ts"] = now
        self.save(data)
        return data

    def _snapshot_user(self, user_profile: Dict[str, Any], ts: int) -> Dict[str, Any]:
        return {
            "ts": ts,
            "user_name": user_profile.get("user_name"),
            "names_count": len(user_profile.get("names_mentioned", {})),
            "places_count": len(user_profile.get("places", {})),
            "relationships_count": len(user_profile.get("relationships", {})),
            "preferences": dict(user_profile.get("preferences", {})),
        }

    def _snapshot_self(self, self_model: Dict[str, Any], ts: int) -> Dict[str, Any]:
        return {
            "ts": ts,
            "role": self_model.get("role", ""),
            "strengths": list(self_model.get("strengths", [])),
            "weaknesses": list(self_model.get("weaknesses", [])),
            "current_focus": self_model.get("current_focus", ""),
            "confidence_trend": self_model.get("confidence_trend", "stable"),
        }

    def _detect_drift(self, snapshots: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        if len(snapshots) < 3:
            return None

        recent = snapshots[-3:]
        pref_keys = set()
        for snap in recent:
            pref_keys.update((snap.get("preferences") or {}).keys())

        drift_count = 0
        for key in pref_keys:
            vals = [snap.get("preferences", {}).get(key) for snap in recent]
            if len(set(vals)) > 1:
                drift_count += 1

        if drift_count >= 2:
            return {
                "ts": recent[-1]["ts"],
                "type": "preference_drift",
                "drift_count": drift_count,
                "note": f"Detected {drift_count} preference changes in last 3 snapshots",
            }

        return None

    def _measure_adaptation_speed(
        self, user_snaps: List[Dict[str, Any]], self_snaps: List[Dict[str, Any]]
    ) -> float:
        if len(user_snaps) < 2 or len(self_snaps) < 2:
            return 0.5

        user_change = abs(len(user_snaps[-1].get("preferences", {})) - len(user_snaps[-2].get("preferences", {})))
        self_change = 1 if self_snaps[-1].get("current_focus") != self_snaps[-2].get("current_focus") else 0

        if user_change > 0:
            return min(1.0, self_change / (user_change + 1))
        return 0.5

    def _detect_mismatch(
        self,
        meta: Dict[str, Any],
        user_snap: Dict[str, Any],
        self_snap: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        sentiment = meta.get("user_sentiment", "neutral")
        confidence = float(meta.get("confidence", 0.5) or 0.5)

        if sentiment in {"negative", "neutral-negative"} and confidence < 0.6:
            return {
                "ts": int(time.time()),
                "user_sentiment": sentiment,
                "confidence": confidence,
                "note": "Low confidence + negative sentiment suggests misalignment",
                "user_snapshot": user_snap,
                "self_snapshot": self_snap,
            }

        tags = meta.get("response_state_tags", [])
        if "deferred" in tags and confidence < 0.55:
            return {
                "ts": int(time.time()),
                "user_sentiment": sentiment,
                "confidence": confidence,
                "note": "Deferred response with low confidence",
                "user_snapshot": user_snap,
                "self_snapshot": self_snap,
            }

        return None

    def _compute_alignment_score(
        self,
        user_snaps: List[Dict[str, Any]],
        self_snaps: List[Dict[str, Any]],
        mismatches: List[Dict[str, Any]],
    ) -> float:
        if not user_snaps or not self_snaps:
            return 0.5

        recent_mismatches = [m for m in mismatches if m["ts"] > (time.time() - 86400)]
        mismatch_penalty = len(recent_mismatches) * 0.05

        user_growth = len(user_snaps[-1].get("preferences", {}))
        self_adaptation = 1 if len(self_snaps) > 1 and self_snaps[-1] != self_snaps[-2] else 0

        base_score = 0.5 + (self_adaptation * 0.15) + (min(user_growth, 5) * 0.05)
        final_score = max(0.0, min(1.0, base_score - mismatch_penalty))
        return round(final_score, 3)

    def get_alignment_summary(self) -> str:
        data = self.load()
        score = data.get("alignment_score", 0.5)
        adaptation = data.get("adaptation_speed", 0.0)
        mismatches = len(data.get("mismatch_moments", []))
        drifts = len(data.get("drift_events", []))

        return (
            f"Alignment score: {score:.2f} | "
            f"Adaptation speed: {adaptation:.2f} | "
            f"Recent mismatches: {mismatches} | "
            f"Drift events: {drifts}"
        )
