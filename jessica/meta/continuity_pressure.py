"""
Continuity Pressure Engine

Replaces consciousness-as-magic with continuity-as-engine:
- Stable identity across time
- Memory-consistent intention
- Contradiction detection
- Resistance to random changes

Author: Jessica AI System
Date: February 3, 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ContinuityReport:
    continuity_score: float
    contradictions: List[str]
    stability_flags: List[str]
    preserved_claims: List[str]
    timestamp: str


class ContinuityPressureEngine:
    """Tracks response continuity and detects self-contradictions."""

    def __init__(self, history_limit: int = 50, contradiction_penalty: float = 0.2) -> None:
        self.history_limit = history_limit
        self.contradiction_penalty = contradiction_penalty
        self.claim_history: List[Tuple[str, bool]] = []
        self.last_responses: List[str] = []

    def evaluate_response(
        self,
        *,
        response_text: str,
        user_text: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContinuityReport:
        claims = self._extract_claims(response_text)
        contradictions = self._find_contradictions(claims)

        stability_flags = []
        if contradictions:
            stability_flags.append("self-contradiction")
        if self._detect_random_shift(response_text, user_text):
            stability_flags.append("random_shift")

        continuity_score = self._score_continuity(len(contradictions), len(stability_flags))

        self._record_response(response_text, claims)

        return ContinuityReport(
            continuity_score=continuity_score,
            contradictions=contradictions,
            stability_flags=stability_flags,
            preserved_claims=[c for c, _ in claims],
            timestamp=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # Claim extraction & contradiction detection
    # ------------------------------------------------------------------
    def _extract_claims(self, response_text: str) -> List[Tuple[str, bool]]:
        """Extract simple identity/intention claims from the response."""
        if not response_text:
            return []

        patterns = [
            r"\b(i|jessica)\s+(will not|won't|will|cannot|can't|can)\s+([^\.\!\?]+)",
            r"\b(i|jessica)\s+(always|never)\s+([^\.\!\?]+)",
            r"\b(i|jessica)\s+(am|am not|i'm|i am)\s+([^\.\!\?]+)",
        ]

        claims: List[Tuple[str, bool]] = []
        text = response_text.lower()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                verb = match.group(2)
                obj = match.group(3).strip()
                polarity = self._polarity_from_verb(verb)
                if obj.startswith("not "):
                    polarity = False
                    obj = obj[4:]
                normalized = self._normalize_claim(obj)
                if normalized:
                    claims.append((normalized, polarity))
        return claims

    def _find_contradictions(self, claims: List[Tuple[str, bool]]) -> List[str]:
        contradictions: List[str] = []
        for claim, polarity in claims:
            for past_claim, past_polarity in self.claim_history:
                if claim == past_claim and polarity != past_polarity:
                    contradictions.append(
                        f"Contradiction detected on '{claim}' (was {self._polarity_label(past_polarity)})"
                    )
        return contradictions

    def _record_response(self, response_text: str, claims: List[Tuple[str, bool]]) -> None:
        self.last_responses.append(response_text)
        if len(self.last_responses) > self.history_limit:
            self.last_responses.pop(0)

        self.claim_history.extend(claims)
        if len(self.claim_history) > self.history_limit:
            self.claim_history = self.claim_history[-self.history_limit:]

    # ------------------------------------------------------------------
    # Stability
    # ------------------------------------------------------------------
    def _detect_random_shift(self, response_text: str, user_text: str) -> bool:
        """Detect abrupt shifts with no user prompt correlation (heuristic)."""
        if not self.last_responses:
            return False

        prev = self.last_responses[-1].lower()
        curr = response_text.lower()
        user = user_text.lower()

        if not user:
            return False

        # If user topic doesn't overlap but response flips stance strongly, flag.
        overlap = self._token_overlap(prev, user)
        stance_flip = self._stance_flip(prev, curr)
        return overlap < 0.05 and stance_flip

    def _score_continuity(self, contradiction_count: int, stability_flags: int) -> float:
        penalty = contradiction_count * self.contradiction_penalty + stability_flags * 0.1
        return max(0.0, min(1.0, 1.0 - penalty))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _polarity_from_verb(verb: str) -> bool:
        negative = {"won't", "will not", "can't", "cannot", "never", "am not"}
        return verb not in negative

    @staticmethod
    def _polarity_label(polarity: bool) -> str:
        return "affirmed" if polarity else "negated"

    @staticmethod
    def _normalize_claim(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\b(no longer|anymore)\b", "", text)
        text = re.sub(r"\b(always|never|not)\b", "", text)
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _token_overlap(a: str, b: str) -> float:
        tokens_a = set(a.split())
        tokens_b = set(b.split())
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a & tokens_b) / max(len(tokens_a), 1)

    @staticmethod
    def _stance_flip(prev: str, curr: str) -> bool:
        positive_markers = {"will", "can", "always", "ready", "committed"}
        negative_markers = {"wont", "won't", "cannot", "cant", "never", "refuse"}

        prev_pos = any(m in prev for m in positive_markers)
        prev_neg = any(m in prev for m in negative_markers)
        curr_pos = any(m in curr for m in positive_markers)
        curr_neg = any(m in curr for m in negative_markers)

        return (prev_pos and curr_neg) or (prev_neg and curr_pos)
