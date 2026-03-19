"""
Uncertainty Tokens

Explicitly tracks known unknowns, unknown unknowns, and assumptions.
Generates disclosure lines like:
"I don't know — yet. I'm 63% confident. I can improve this if you allow exploration."

Author: Jessica AI System
Date: February 3, 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import List, Optional


@dataclass
class UncertaintyReport:
    confidence: float
    known_unknowns: List[str]
    unknown_unknowns: List[str]
    assumptions: List[str]
    disclosure: str
    should_disclose: bool
    timestamp: str


class UncertaintyEngine:
    """Extract and disclose uncertainty explicitly without performative doubt."""

    def __init__(self, disclose_threshold: float = 0.75) -> None:
        self.disclose_threshold = disclose_threshold

    def analyze(
        self,
        *,
        response_text: str,
        user_text: str,
        confidence: float,
        allow_exploration: bool = True,
    ) -> UncertaintyReport:
        known_unknowns = self._extract_known_unknowns(response_text, user_text)
        assumptions = self._extract_assumptions(response_text)
        unknown_unknowns = self._infer_unknown_unknowns(user_text, confidence)

        should_disclose = confidence < self.disclose_threshold or bool(known_unknowns)
        disclosure = self._build_disclosure(confidence, allow_exploration, should_disclose)

        return UncertaintyReport(
            confidence=confidence,
            known_unknowns=known_unknowns,
            unknown_unknowns=unknown_unknowns,
            assumptions=assumptions,
            disclosure=disclosure,
            should_disclose=should_disclose,
            timestamp=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------
    def _extract_known_unknowns(self, response_text: str, user_text: str) -> List[str]:
        text = f"{response_text} {user_text}".lower()
        patterns = [
            r"not sure about ([^\.\!\?]+)",
            r"unclear ([^\.\!\?]+)",
            r"need more ([^\.\!\?]+)",
            r"depends on ([^\.\!\?]+)",
        ]
        results: List[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                results.append(match.group(1).strip())
        return results[:5]

    def _extract_assumptions(self, response_text: str) -> List[str]:
        text = response_text.lower()
        patterns = [
            r"assuming ([^\.\!\?]+)",
            r"assume ([^\.\!\?]+)",
            r"if ([^\.\!\?]+), then",
        ]
        results: List[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                results.append(match.group(1).strip())
        return results[:5]

    def _infer_unknown_unknowns(self, user_text: str, confidence: float) -> List[str]:
        if confidence >= self.disclose_threshold:
            return []
        if len(user_text.split()) < 8:
            return ["Missing context that could change the answer"]
        return ["Hidden constraints or goals not yet stated"]

    # ------------------------------------------------------------------
    # Disclosure
    # ------------------------------------------------------------------
    def _build_disclosure(self, confidence: float, allow_exploration: bool, should_disclose: bool) -> str:
        if not should_disclose:
            return ""
        pct = max(0, min(100, round(confidence * 100)))
        exploration = " I can improve this if you allow exploration." if allow_exploration else ""
        return f"I don't know — yet. I'm {pct}% confident.{exploration}"
