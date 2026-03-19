from __future__ import annotations

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from jessica.personality import Personality


class MetaObserver:
    """Post-response self-monitoring layer for meta-cognition."""

    def __init__(self, memory_store, model_router=None, personality: Personality | None = None, social=None):
        self.memory_store = memory_store
        self.model_router = model_router
        self.personality = personality
        self.social = social

    def observe(
        self,
        *,
        user: str,
        intent: Dict[str, Any] | str,
        user_text: str,
        response_text: str,
        episode_id: int | None = None,
        model_used: str | None = None,
        memory_used: bool = False,
        user_sentiment: str | None = None,
        followup_needed: bool | None = None,
        improvement_note: str | None = None,
        prompt: str | None = None,
        extra: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        intent_label = intent.get("intent") if isinstance(intent, dict) else str(intent)

        resolved_model = model_used or getattr(self.model_router, "last_model_used", None) or "unknown"

        sentiment_label = user_sentiment or self._sentiment_label(user_text)
        needs_followup = followup_needed if followup_needed is not None else self._followup_needed(response_text)
        confidence = self._estimate_confidence(response_text, memory_used)

        values_alignment = self._values_alignment(response_text)
        improvement = improvement_note or self._improvement_note(confidence, memory_used)

        meta = {
            "intent": intent_label,
            "model_used": resolved_model,
            "model_best": resolved_model,
            "confidence": round(confidence, 2),
            "memory_used": bool(memory_used),
            "user_sentiment": sentiment_label,
            "followup_needed": bool(needs_followup),
            "values_alignment": values_alignment,
            "improvement_note": improvement,
            "response_length": len(response_text or ""),
        }

        state_tags = self._response_state_tags(
            response_text=response_text,
            confidence=confidence,
            followup_needed=bool(needs_followup),
        )
        meta["response_state_tags"] = state_tags

        prompt_text = prompt or (extra or {}).get("prompt")
        if prompt_text:
            counterfactual = self._counterfactual_compare(
                prompt_text=prompt_text,
                original_response=response_text,
                model_used=resolved_model,
            )
            if counterfactual:
                meta.update(counterfactual)

        if extra:
            for key, value in extra.items():
                if key not in meta:
                    meta[key] = value

        try:
            self.memory_store.save_meta_observation(meta, episode_id=episode_id, user=user)
        except Exception as exc:
            print("[MetaObserver] Save failed:", exc)

        return meta

    def _counterfactual_compare(self, *, prompt_text: str, original_response: str, model_used: str) -> Dict[str, Any] | None:
        if not self.model_router:
            return None

        alt_model = self._select_counterfactual_model(model_used)
        if not alt_model:
            return None

        try:
            alt_response = self.model_router.generate_with_model(
                alt_model,
                prompt_text,
                max_tokens=256,
                temperature=0.6,
                record=False,
            )
        except Exception as exc:
            print("[MetaObserver] Counterfactual failed:", exc)
            return None

        note = self._summarize_delta(original_response, alt_response, model_used, alt_model)
        return {
            "counterfactual_model": alt_model,
            "counterfactual_response": (alt_response or "")[:240],
            "counterfactual_note": note,
        }

    def _select_counterfactual_model(self, model_used: str) -> str | None:
        m = (model_used or "").lower()
        if "logic" in m or "mistral" in m:
            return "fast_brain"
        if "fast" in m or "phi" in m:
            return "logic_brain"
        if "code" in m:
            return "logic_brain"
        return "fast_brain"

    def _summarize_delta(self, original: str, alt: str, model_used: str, alt_model: str) -> str:
        original = original or ""
        alt = alt or ""

        orig_len = len(original)
        alt_len = len(alt)

        orig_tone = self._tone_label(original)
        alt_tone = self._tone_label(alt)

        note_parts = []
        if alt_len < orig_len * 0.8:
            note_parts.append("Alt is more concise")
        elif alt_len > orig_len * 1.2:
            note_parts.append("Alt is more detailed")

        if orig_tone != alt_tone:
            note_parts.append(f"Tone shift: {orig_tone} → {alt_tone}")

        if not note_parts:
            note_parts.append("Minor differences")

        return f"Best blend could be {model_used} tone + {alt_model} structure. " + "; ".join(note_parts)

    def _tone_label(self, text: str) -> str:
        t = text.lower()
        warm_markers = ["glad", "happy", "sorry", "understand", "thanks", "appreciate", "let's"]
        cold_markers = ["execute", "command", "error", "traceback", "strict", "must", "only"]
        score = 0
        if any(m in t for m in warm_markers):
            score += 1
        if any(m in t for m in cold_markers):
            score -= 1
        if score > 0:
            return "warm"
        if score < 0:
            return "cold"
        return "neutral"

    def _sentiment_label(self, text: str) -> str:
        score = 0.0
        try:
            if self.social:
                score = self.social.sentiment_score(text)
        except Exception:
            score = 0.0

        if score >= 0.35:
            return "positive"
        if score >= 0.15:
            return "neutral-positive"
        if score <= -0.35:
            return "negative"
        if score <= -0.15:
            return "neutral-negative"
        return "neutral"

    def _estimate_confidence(self, response_text: str, memory_used: bool) -> float:
        return self.estimate_confidence(response_text, memory_used)

    @staticmethod
    def estimate_confidence(response_text: str, memory_used: bool) -> float:
        t = (response_text or "").lower()
        score = 0.6

        if memory_used:
            score += 0.08

        uncertain_markers = [
            "not sure", "i think", "maybe", "might", "uncertain", "guess", "probably", "hard to say",
            "can’t be sure", "can't be sure",
        ]
        confident_markers = [
            "definitely", "certainly", "here's", "do this", "follow these", "the answer", "you should",
            "steps:", "step 1", "first,",
        ]

        if any(m in t for m in uncertain_markers):
            score -= 0.15
        if any(m in t for m in confident_markers):
            score += 0.1
        if len(t.split()) < 20:
            score -= 0.05

        return max(0.2, min(0.95, score))

    def _followup_needed(self, response_text: str) -> bool:
        t = (response_text or "").lower()
        if "?" in t:
            return True
        followup_markers = [
            "let me know", "do you want", "would you like", "should i", "want me to", "need me to",
            "if you'd like",
        ]
        return any(m in t for m in followup_markers)

    def _values_alignment(self, response_text: str) -> str:
        if not response_text:
            return "needs_review"
        low_signal = ["[error]", "exception", "traceback"]
        if any(tok in (response_text or "").lower() for tok in low_signal):
            return "needs_review"
        return "aligned"

    def _improvement_note(self, confidence: float, memory_used: bool) -> str:
        if confidence < 0.55 and not memory_used:
            return "Seek corroborating memory or ask a clarifying question earlier."
        if confidence < 0.55:
            return "Clarify assumptions earlier."
        return "Keep responses concise and verify assumptions."

    def _response_state_tags(self, *, response_text: str, confidence: float, followup_needed: bool) -> list[str]:
        tags: list[str] = []
        t = (response_text or "").lower()

        if confidence < 0.55:
            tags.append("unsure")
        elif confidence > 0.78:
            tags.append("confident")

        defer_markers = [
            "i can't", "i cannot", "not sure", "unsure", "can't", "unable", "i don't know",
            "might be wrong", "hard to say",
        ]
        if any(m in t for m in defer_markers):
            tags.append("deferred")

        proactive_markers = [
            "would you like", "i can also", "next step", "if you want", "want me to",
            "i can go ahead", "i can set up", "i can draft",
        ]
        if any(m in t for m in proactive_markers):
            tags.append("took_initiative")

        if followup_needed:
            tags.append("asked_followup")

        if len(t.split()) > 160:
            tags.append("verbose")

        if not tags:
            tags.append("neutral")

        # De-dup while preserving order
        seen = set()
        deduped = []
        for tag in tags:
            if tag not in seen:
                deduped.append(tag)
                seen.add(tag)
        return deduped