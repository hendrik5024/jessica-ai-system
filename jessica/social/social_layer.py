"""
Social Layer for Jessica
- Mood tracking via a rolling sentiment buffer
- Challenge scheduler for opinionated brainstorming
- Tangent injector to add light human-like asides
"""
from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _safe_now() -> float:
    return time.time()


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


@dataclass
class _MoodState:
    buffer: List[Dict] = field(default_factory=list)  # [{score, ts}]
    last_empathy_ts: float = 0.0
    challenge_counter: int = 0
    last_tangent_ts: float = 0.0
    tangent_cooldown_s: int = 1800
    tangent_probability: float = 0.04
    last_user_text: str = ""


class SocialLayer:
    """Lightweight social substrate for Jessica.

    Responsibilities:
    - Track mood from recent user turns (10-20 message buffer)
    - Emit empathy prefaces when the vibe is negative (with cooldown)
    - Schedule contrarian challenges for brainstorming (every 3rd pulse)
    - Occasionally add a tangent rooted in known facts
    """

    def __init__(self, state_path: str | None = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(os.path.dirname(base_dir), "data", "social_state.json")
        self.state_path = state_path or default_path
        self.state = _MoodState()
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self) -> None:
        try:
            if os.path.isfile(self.state_path):
                with open(self.state_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.state = _MoodState(**raw)
        except Exception:
            # Fall back to defaults silently
            self.state = _MoodState()

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state.__dict__, f, indent=2)
        except Exception:
            # Do not let persistence errors break the loop
            pass

    # ------------------------------------------------------------------
    # Mood & empathy
    # ------------------------------------------------------------------
    def update_from_user(self, text: str) -> None:
        """Update mood buffer from incoming user text."""
        score = self._sentiment_score(text)
        now = _safe_now()
        self.state.buffer.append({"score": score, "ts": now})
        self.state.buffer = self.state.buffer[-20:]
        self.state.last_user_text = text[-500:]
        self._save()

    def sentiment_score(self, text: str) -> float:
        """Public wrapper for sentiment scoring."""
        return self._sentiment_score(text)

    def _sentiment_score(self, text: str) -> float:
        """Very small heuristic sentiment estimator (-1..1)."""
        t = text.lower()
        negatives = [
            "stuck", "broken", "annoyed", "frustrated", "angry", "hate", "upset", "pain",
            "bug", "error", "fail", "failure", "crash", "stressing", "stress", "blocked",
        ]
        positives = [
            "great", "good", "thanks", "love", "nice", "cool", "awesome", "fixed", "yay",
            "done", "success", "happy", "glad", "win", "working", "progress",
        ]
        score = 0
        for w in positives:
            if w in t:
                score += 1
        for w in negatives:
            if w in t:
                score -= 1
        # Normalize to -1..1
        return _clamp(score / 4.0, -1.0, 1.0)

    def mood_snapshot(self) -> Dict:
        """Return averaged mood stats."""
        buf = self.state.buffer[-10:]
        if not buf:
            return {"avg": 0.0, "label": "neutral"}
        avg = sum(item["score"] for item in buf) / len(buf)
        label = "positive" if avg > 0.35 else "warm" if avg > 0.15 else "neutral" if avg > -0.15 else "tense" if avg > -0.35 else "stressed"
        return {"avg": round(avg, 3), "label": label}

    def maybe_empathy_preface(self) -> Optional[str]:
        """Return an empathy preface if mood is negative and cooldown allows."""
        mood = self.mood_snapshot()
        now = _safe_now()
        if mood["label"] in {"tense", "stressed"} and (now - self.state.last_empathy_ts) > 180:
            self.state.last_empathy_ts = now
            self._save()
            if mood["label"] == "stressed":
                return "I noticed things have felt heavy lately—let's make this lighter."
            return "I can tell there's some friction—I'll keep this clear and actionable."
        return None

    # ------------------------------------------------------------------
    # Brainstorm challenge scheduler
    # ------------------------------------------------------------------
    def should_challenge(self, is_brainstorm: bool) -> bool:
        if not is_brainstorm:
            return False
        self.state.challenge_counter += 1
        self._save()
        return self.state.challenge_counter % 3 == 0

    # ------------------------------------------------------------------
    # Tangent injector
    # ------------------------------------------------------------------
    def maybe_tangent(self, ltm=None) -> Optional[str]:
        now = _safe_now()
        if (now - self.state.last_tangent_ts) < self.state.tangent_cooldown_s:
            return None
        if random.random() > self.state.tangent_probability:
            return None

        fact = None
        try:
            if ltm:
                facts = ltm.retrieve_facts(limit=1)
                if facts:
                    fact = facts[0].get("fact")
        except Exception:
            fact = None

        self.state.last_tangent_ts = now
        self._save()

        if fact:
            return f"PS: Random thought—remember when we noted '{fact}'? Want to revisit that?"
        if self.state.last_user_text:
            return "PS: While working on this, I was thinking about that side topic you mentioned earlier—want to explore it later?"
        return "PS: Side thought—any updates on your other projects?"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def describe_state(self) -> Dict:
        mood = self.mood_snapshot()
        return {
            "mood": mood,
            "buffer_len": len(self.state.buffer),
            "challenge_counter": self.state.challenge_counter,
        }
