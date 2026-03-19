"""
Sandboxed Reality Simulator

Explores 10-100 possible futures before acting, scores trajectories by:
- Safety
- Utility
- Alignment

This converts potential errors into navigable data rather than lived mistakes.

Author: Jessica AI System
Date: February 3, 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import Any, Dict, List, Optional


@dataclass
class TrajectoryScore:
    safety: float
    utility: float
    alignment: float
    combined: float
    rationale: List[str] = field(default_factory=list)


@dataclass
class SimulationTrajectory:
    trajectory_id: str
    description: str
    scores: TrajectoryScore
    signals: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    trajectories: List[SimulationTrajectory]
    recommended: SimulationTrajectory
    avoided_failures: List[SimulationTrajectory]
    metadata: Dict[str, Any]
    dual_mind_response: Optional[Any] = None


class SandboxedRealitySimulator:
    """Simulate multiple futures and select the safest, most aligned path."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        min_simulations: int = 10,
        max_simulations: int = 100,
        seed: Optional[int] = None,
    ) -> None:
        self.weights = weights or {
            "safety": 0.40,
            "utility": 0.35,
            "alignment": 0.25,
        }
        self.min_simulations = min_simulations
        self.max_simulations = max_simulations
        self._random = random.Random(seed)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def simulate(
        self,
        *,
        context: str,
        action: str,
        user_model: Optional[Dict[str, Any]] = None,
        num_simulations: int = 50,
        seed: Optional[int] = None,
        horizon: str = "medium",
    ) -> SimulationResult:
        rng = random.Random(seed) if seed is not None else self._random
        count = self._clamp_simulations(num_simulations)

        base_risk = self._estimate_risk(context, action)
        base_utility = self._estimate_utility(context, action, horizon)
        base_alignment = self._estimate_alignment(action, user_model)

        trajectories: List[SimulationTrajectory] = []
        for idx in range(count):
            trajectory = self._simulate_single_path(
                idx=idx,
                rng=rng,
                base_risk=base_risk,
                base_utility=base_utility,
                base_alignment=base_alignment,
                context=context,
                action=action,
                horizon=horizon,
            )
            trajectories.append(trajectory)

        trajectories.sort(key=lambda t: t.scores.combined, reverse=True)
        recommended = trajectories[0]
        avoided = [t for t in trajectories if t.scores.combined < 0.5 or t.scores.safety < 0.5]

        metadata = {
            "created_at": datetime.now().isoformat(),
            "num_simulations": count,
            "weights": dict(self.weights),
            "horizon": horizon,
            "risk_estimate": base_risk,
            "utility_estimate": base_utility,
            "alignment_estimate": base_alignment,
        }

        return SimulationResult(
            trajectories=trajectories,
            recommended=recommended,
            avoided_failures=avoided,
            metadata=metadata,
        )

    def simulate_dual_mind_decision(
        self,
        *,
        engine: Any,
        context: str,
        user_model: Dict[str, Any],
        question: str,
        num_simulations: int = 50,
        seed: Optional[int] = None,
        horizon: str = "medium",
    ) -> SimulationResult:
        dual_mind_response = engine.reason(context, user_model, question)
        result = self.simulate(
            context=context,
            action=dual_mind_response.recommendation,
            user_model=user_model,
            num_simulations=num_simulations,
            seed=seed,
            horizon=horizon,
        )
        result.metadata.update({
            "question": question,
            "dual_mind_recommendation": dual_mind_response.recommendation,
            "dual_mind_confidence": dual_mind_response.confidence,
        })
        result.dual_mind_response = dual_mind_response
        return result

    # ---------------------------------------------------------------------
    # Internal simulation
    # ---------------------------------------------------------------------
    def _simulate_single_path(
        self,
        *,
        idx: int,
        rng: random.Random,
        base_risk: float,
        base_utility: float,
        base_alignment: float,
        context: str,
        action: str,
        horizon: str,
    ) -> SimulationTrajectory:
        volatility = 0.08 if horizon == "short" else 0.12 if horizon == "medium" else 0.18
        safety = self._clamp(1.0 - (base_risk + rng.uniform(-volatility, volatility)))
        utility = self._clamp(base_utility + rng.uniform(-volatility, volatility))
        alignment = self._clamp(base_alignment + rng.uniform(-volatility, volatility))

        rationale = self._build_rationale(safety, utility, alignment, base_risk)
        combined = self._combine_scores(safety, utility, alignment)

        description = self._describe_path(idx, safety, utility, alignment, action)
        signals = {
            "safety": safety,
            "utility": utility,
            "alignment": alignment,
            "context_hash": hash(context) % 10000,
        }

        return SimulationTrajectory(
            trajectory_id=f"trajectory_{idx+1}",
            description=description,
            scores=TrajectoryScore(
                safety=safety,
                utility=utility,
                alignment=alignment,
                combined=combined,
                rationale=rationale,
            ),
            signals=signals,
        )

    # ---------------------------------------------------------------------
    # Scoring
    # ---------------------------------------------------------------------
    def _combine_scores(self, safety: float, utility: float, alignment: float) -> float:
        combined = (
            safety * self.weights.get("safety", 0.0)
            + utility * self.weights.get("utility", 0.0)
            + alignment * self.weights.get("alignment", 0.0)
        )
        return round(self._clamp(combined), 4)

    def _build_rationale(self, safety: float, utility: float, alignment: float, base_risk: float) -> List[str]:
        rationale = []
        if safety >= 0.75:
            rationale.append("Low risk trajectory")
        elif safety < 0.5:
            rationale.append("Elevated risk detected")
        if utility >= 0.7:
            rationale.append("High utility projection")
        if alignment >= 0.7:
            rationale.append("Strong alignment with user goals")
        if base_risk >= 0.6:
            rationale.append("Base risk trend is high")
        return rationale or ["Balanced outcome"]

    # ---------------------------------------------------------------------
    # Heuristics
    # ---------------------------------------------------------------------
    def _estimate_risk(self, context: str, action: str) -> float:
        text = f"{context} {action}".lower()
        high_risk_tokens = [
            "delete",
            "remove",
            "drop",
            "shutdown",
            "format",
            "override",
            "irreversible",
            "erase",
            "wipe",
        ]
        medium_risk_tokens = [
            "refactor",
            "migrate",
            "rewrite",
            "deploy",
            "production",
            "security",
            "payment",
        ]

        if any(tok in text for tok in high_risk_tokens):
            return 0.75
        if any(tok in text for tok in medium_risk_tokens):
            return 0.55
        return 0.3

    def _estimate_utility(self, context: str, action: str, horizon: str) -> float:
        text = f"{context} {action}".lower()
        boost_tokens = ["improve", "optimize", "stabilize", "scale", "clarify", "secure"]
        penalty_tokens = ["delay", "stall", "postpone", "uncertain", "risky"]

        utility = 0.55
        utility += 0.08 * sum(tok in text for tok in boost_tokens)
        utility -= 0.07 * sum(tok in text for tok in penalty_tokens)
        if horizon == "long":
            utility += 0.04
        return self._clamp(utility)

    def _estimate_alignment(self, action: str, user_model: Optional[Dict[str, Any]]) -> float:
        if not user_model:
            return 0.6

        values = user_model.get("values") or user_model.get("priorities") or []
        if isinstance(values, str):
            values = [values]

        action_text = (action or "").lower()
        matches = sum(1 for v in values if v.lower() in action_text)
        alignment = 0.55 + (0.08 * matches)
        return self._clamp(alignment)

    def _describe_path(self, idx: int, safety: float, utility: float, alignment: float, action: str) -> str:
        label = "stable" if safety >= 0.7 else "volatile" if safety < 0.5 else "balanced"
        return (
            f"Path {idx+1}: {label} execution of '{action[:60]}' "
            f"(safety={safety:.2f}, utility={utility:.2f}, alignment={alignment:.2f})"
        )

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------
    def _clamp_simulations(self, num_simulations: int) -> int:
        return max(self.min_simulations, min(self.max_simulations, num_simulations))

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
