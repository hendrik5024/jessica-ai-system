from __future__ import annotations

import json
import os
import time
from collections import Counter
from typing import Any, Dict, List

from jessica.meta.self_model import SelfModelManager
from jessica.meta.long_term_goals import LongTermGoalsManager
from jessica.meta.alignment_tracker import AlignmentTracker


class ReflectionWindow:
    """Scheduled introspection job for private cognition."""

    def __init__(self, memory_store, reflection_path: str | None = None, routing_path: str | None = None):
        self.memory_store = memory_store
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(base_dir), "data")
        self.reflection_path = reflection_path or os.path.join(data_dir, "reflection_state.json")
        self.routing_path = routing_path or os.path.join(data_dir, "routing_weights.json")
        self.self_model = SelfModelManager(memory_store)
        self.goals = LongTermGoalsManager(memory_store)
        self.alignment = AlignmentTracker(memory_store)

    def run(self, days: int = 1) -> Dict[str, Any]:
        now = int(time.time())
        summary = self.memory_store.get_meta_summary(days=days)
        observations = self.memory_store.get_meta_observations_since(now - (days * 86400))

        report = {
            "window_days": days,
            "run_ts": now,
            "meta_summary": summary,
            "what_went_well": self._what_went_well(observations),
            "what_confused_me": self._what_confused_me(observations),
            "user_patterns": self._user_patterns(observations),
            "alignment_status": self.alignment.get_alignment_summary(),
        }

        # Update self-model weekly (or when due)
        self.self_model.update_if_due(days=7)

        # Update long-term goals from batch
        self.goals.update_from_meta_batch(observations)

        # Update routing weights based on meta observations
        self._update_routing_weights(observations)

        self._save_reflection(report)
        return report

    def _save_reflection(self, report: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.reflection_path), exist_ok=True)
        with open(self.reflection_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def _what_went_well(self, items: List[Dict[str, Any]]) -> List[str]:
        if not items:
            return ["No recent interactions to evaluate."]

        positives = [i for i in items if (i.get("user_sentiment") in {"positive", "neutral-positive"})]
        high_conf = [i for i in items if (i.get("confidence", 0) or 0) >= 0.75]

        notes = []
        if positives:
            notes.append(f"Positive user sentiment in {len(positives)} interactions.")
        if high_conf:
            notes.append(f"High confidence in {len(high_conf)} responses.")

        return notes or ["Mixed results; no strong positives detected."]

    def _what_confused_me(self, items: List[Dict[str, Any]]) -> List[str]:
        if not items:
            return ["No recent interactions to evaluate."]

        low_conf = [i for i in items if (i.get("confidence", 0) or 0) < 0.55]
        unsure = [i for i in items if "unsure" in (i.get("response_state_tags") or [])]

        notes = []
        if low_conf:
            notes.append(f"Low confidence in {len(low_conf)} responses.")
        if unsure:
            notes.append(f"Unsure tags in {len(unsure)} responses.")

        return notes or ["No major confusion signals detected."]

    def _user_patterns(self, items: List[Dict[str, Any]]) -> List[str]:
        if not items:
            return ["No recent interactions to analyze."]

        intents = [str(i.get("intent", "unknown")) for i in items]
        top_intents = Counter(intents).most_common(3)

        sentiment = [str(i.get("user_sentiment", "neutral")) for i in items]
        top_sentiment = Counter(sentiment).most_common(1)

        patterns = []
        if top_intents:
            patterns.append("Top intents: " + ", ".join(f"{k}({v})" for k, v in top_intents))
        if top_sentiment:
            patterns.append("Dominant user sentiment: " + f"{top_sentiment[0][0]}({top_sentiment[0][1]})")

        return patterns or ["No clear patterns detected."]

    def _update_routing_weights(self, items: List[Dict[str, Any]]) -> None:
        if not items:
            return

        model_scores: Dict[str, List[float]] = {}
        for item in items:
            model = item.get("model_used") or "unknown"
            conf = float(item.get("confidence", 0.0) or 0.0)
            model_scores.setdefault(model, []).append(conf)

        avg_scores = {m: (sum(vals) / max(1, len(vals))) for m, vals in model_scores.items()}
        total = sum(avg_scores.values()) or 1.0
        weights = {m: round(v / total, 3) for m, v in avg_scores.items()}

        payload = {
            "updated_ts": int(time.time()),
            "weights": weights,
            "avg_confidence": {m: round(v, 3) for m, v in avg_scores.items()},
        }

        os.makedirs(os.path.dirname(self.routing_path), exist_ok=True)
        with open(self.routing_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
