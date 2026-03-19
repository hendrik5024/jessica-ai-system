"""
Meaning Engine

Builds a Meaning Graph and evaluates actions by human-like tradeoffs:
- User well-being
- Long-term value
- Trust
- Growth
- Creation

This enables decision-making based on meaning, not emotion.

Author: Jessica AI System
Date: February 3, 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MeaningNode:
    name: str
    description: str
    weight: float = 1.0


@dataclass
class MeaningEdge:
    source: str
    target: str
    relation: str
    description: str
    weight: float = 1.0


@dataclass
class MeaningDecision:
    meaning_score: float
    node_impacts: Dict[str, float]
    tradeoffs: List[str]
    dominant_values: List[str]
    narrative: str
    timestamp: str


class MeaningGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, MeaningNode] = {}
        self.edges: List[MeaningEdge] = []

    def add_node(self, node: MeaningNode) -> None:
        self.nodes[node.name] = node

    def add_edge(self, edge: MeaningEdge) -> None:
        self.edges.append(edge)

    def get_node(self, name: str) -> Optional[MeaningNode]:
        return self.nodes.get(name)


class MeaningEngine:
    """Evaluate actions by meaning tradeoffs using a Meaning Graph."""

    def __init__(self) -> None:
        self.graph = self._build_default_graph()
        self.keyword_map = self._build_keyword_map()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def evaluate_action(
        self,
        *,
        action: str,
        context: str = "",
        user_model: Optional[Dict[str, Any]] = None,
        signals: Optional[Dict[str, float]] = None,
    ) -> MeaningDecision:
        text = f"{context} {action}".lower()
        node_impacts = self._score_nodes(text, signals)
        tradeoffs = self._identify_tradeoffs(text, node_impacts)
        meaning_score = self._combine_scores(node_impacts)
        dominant_values = self._dominant_values(node_impacts)
        narrative = self._build_narrative(action, node_impacts, tradeoffs, user_model)

        return MeaningDecision(
            meaning_score=meaning_score,
            node_impacts=node_impacts,
            tradeoffs=tradeoffs,
            dominant_values=dominant_values,
            narrative=narrative,
            timestamp=datetime.now().isoformat(),
        )

    def choose_best_action(
        self,
        *,
        actions: List[str],
        context: str = "",
        user_model: Optional[Dict[str, Any]] = None,
        signals_list: Optional[List[Dict[str, float]]] = None,
    ) -> Tuple[str, MeaningDecision, List[Tuple[str, MeaningDecision]]]:
        scored: List[Tuple[str, MeaningDecision]] = []
        for idx, action in enumerate(actions):
            signals = signals_list[idx] if signals_list and idx < len(signals_list) else None
            decision = self.evaluate_action(
                action=action,
                context=context,
                user_model=user_model,
                signals=signals,
            )
            scored.append((action, decision))

        scored.sort(key=lambda item: item[1].meaning_score, reverse=True)
        best_action, best_decision = scored[0]
        return best_action, best_decision, scored

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def _build_default_graph(self) -> MeaningGraph:
        graph = MeaningGraph()
        graph.add_node(MeaningNode("user_well_being", "Protect and improve the user's well-being", weight=1.3))
        graph.add_node(MeaningNode("long_term_value", "Maximize durable, long-term value", weight=1.2))
        graph.add_node(MeaningNode("trust", "Preserve and grow trust", weight=1.25))
        graph.add_node(MeaningNode("growth", "Enable learning and growth", weight=1.0))
        graph.add_node(MeaningNode("creation", "Create new value or artifacts", weight=0.9))

        graph.add_edge(MeaningEdge(
            source="creation",
            target="trust",
            relation="tradeoff",
            description="Fast creation can erode trust if quality drops",
            weight=0.7,
        ))
        graph.add_edge(MeaningEdge(
            source="long_term_value",
            target="user_well_being",
            relation="reinforces",
            description="Long-term value reinforces user well-being",
            weight=0.8,
        ))
        graph.add_edge(MeaningEdge(
            source="growth",
            target="creation",
            relation="enables",
            description="Growth enables higher-quality creation",
            weight=0.6,
        ))
        graph.add_edge(MeaningEdge(
            source="user_well_being",
            target="short_term_gain",
            relation="tradeoff",
            description="Short-term gain can harm well-being",
            weight=0.9,
        ))
        return graph

    def _build_keyword_map(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            "user_well_being": {
                "positive": ["safe", "healthy", "support", "reduce stress", "protect", "care"],
                "negative": ["harm", "risk", "burnout", "overwhelm", "unsafe", "stress"],
            },
            "long_term_value": {
                "positive": ["long-term", "sustainable", "durable", "scalable", "future-proof"],
                "negative": ["short-term", "quick win", "temporary", "patch", "band-aid"],
            },
            "trust": {
                "positive": ["transparent", "honest", "reliable", "consistent", "trust"],
                "negative": ["hide", "mislead", "inconsistent", "risky", "uncertain"],
            },
            "growth": {
                "positive": ["learn", "grow", "improve", "iterate", "feedback"],
                "negative": ["stagnate", "avoid", "ignore", "complacent"],
            },
            "creation": {
                "positive": ["build", "create", "design", "develop", "ship"],
                "negative": ["delete", "destroy", "remove", "erase"],
            },
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def _score_nodes(self, text: str, signals: Optional[Dict[str, float]]) -> Dict[str, float]:
        node_impacts: Dict[str, float] = {}
        for node_name, keywords in self.keyword_map.items():
            impact = 0.0
            for token in keywords.get("positive", []):
                if token in text:
                    impact += 0.2
            for token in keywords.get("negative", []):
                if token in text:
                    impact -= 0.2
            if signals and node_name in signals:
                impact = signals[node_name]

            node = self.graph.get_node(node_name)
            weight = node.weight if node else 1.0
            node_impacts[node_name] = self._clamp(impact * weight)
        return node_impacts

    def _combine_scores(self, node_impacts: Dict[str, float]) -> float:
        if not node_impacts:
            return 0.0
        total_weight = sum(self.graph.nodes[n].weight for n in node_impacts)
        combined = sum(node_impacts[n] for n in node_impacts) / max(total_weight, 1e-6)
        return self._clamp(combined)

    # ------------------------------------------------------------------
    # Tradeoffs & narrative
    # ------------------------------------------------------------------
    def _identify_tradeoffs(self, text: str, node_impacts: Dict[str, float]) -> List[str]:
        tradeoffs: List[str] = []
        if "short-term" in text and "long-term" in text:
            tradeoffs.append("Short-term gain vs long-term value")

        for edge in self.graph.edges:
            if edge.relation != "tradeoff":
                continue
            source = node_impacts.get(edge.source)
            target = node_impacts.get(edge.target)
            if source is None or target is None:
                continue
            if (source > 0.2 and target < -0.2) or (source < -0.2 and target > 0.2):
                tradeoffs.append(edge.description)
        return tradeoffs

    def _dominant_values(self, node_impacts: Dict[str, float]) -> List[str]:
        ranked = sorted(node_impacts.items(), key=lambda x: x[1], reverse=True)
        return [name for name, score in ranked[:2] if score > 0]

    def _build_narrative(
        self,
        action: str,
        node_impacts: Dict[str, float],
        tradeoffs: List[str],
        user_model: Optional[Dict[str, Any]],
    ) -> str:
        top_values = ", ".join(self._dominant_values(node_impacts)) or "balanced values"
        tradeoff_text = "; ".join(tradeoffs) if tradeoffs else "No major tradeoffs detected"
        user_goal = user_model.get("primary_goal") if user_model else "their goals"
        return (
            f"Action '{action[:70]}' prioritizes {top_values}. "
            f"Tradeoffs: {tradeoff_text}. "
            f"Alignment to {user_goal} considered."
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _clamp(value: float) -> float:
        return max(-1.0, min(1.0, value))
