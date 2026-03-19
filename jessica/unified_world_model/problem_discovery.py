"""
Autonomous Problem Discovery System (Phase 5).

Enables:
- Introspection over logs and performance metrics
- Gap detection for missing capabilities
- Opportunity discovery and prioritization
- Autonomous problem proposal generation
- Validation planning and expected impact estimation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import statistics
import uuid


class SignalType(Enum):
    """Types of discovery signals."""
    ERROR = "error"
    LATENCY = "latency"
    FAILURE_RATE = "failure_rate"
    USER_CONFUSION = "user_confusion"
    MISSING_CAPABILITY = "missing_capability"
    INTEGRATION_GAP = "integration_gap"


class OpportunityType(Enum):
    """Types of opportunities."""
    NEW_KNOWLEDGE_STORE = "new_knowledge_store"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    QUALITY_IMPROVEMENT = "quality_improvement"
    SAFETY_IMPROVEMENT = "safety_improvement"


@dataclass
class DiscoverySignal:
    """Signal extracted from logs or metrics."""
    signal_id: str
    signal_type: SignalType
    domain: str
    description: str
    severity: float  # 0-1
    frequency: int
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class CapabilityGap:
    """Detected capability gap."""
    gap_id: str
    title: str
    description: str
    domain: str
    severity: float
    frequency: int
    confidence: float
    evidence: List[DiscoverySignal] = field(default_factory=list)


@dataclass
class Opportunity:
    """Prioritized opportunity derived from gaps/signals."""
    opportunity_id: str
    title: str
    description: str
    opportunity_type: OpportunityType
    impact_score: float  # 0-1
    feasibility_score: float  # 0-1
    priority_score: float  # 0-1
    related_gaps: List[str] = field(default_factory=list)
    evidence: List[DiscoverySignal] = field(default_factory=list)


@dataclass
class ProblemProposal:
    """Proposed problem to solve based on opportunities."""
    proposal_id: str
    title: str
    summary: str
    recommended_actions: List[str]
    expected_improvement: Dict[str, float]
    validation_plan: List[str]
    required_resources: List[str]
    risk_level: str


@dataclass
class DiscoveryReport:
    """Full report of discovery cycle."""
    signals: List[DiscoverySignal]
    gaps: List[CapabilityGap]
    opportunities: List[Opportunity]
    proposals: List[ProblemProposal]
    summary: Dict[str, Any]


class GapDetector:
    """Detects capability gaps from signals and logs."""

    def detect_from_query_topics(self,
                                 query_topics: List[str],
                                 known_stores: List[str]) -> List[CapabilityGap]:
        """Detect missing knowledge stores from query topics."""
        gaps: List[CapabilityGap] = []
        known_lower = {k.lower() for k in known_stores}

        topic_counts: Dict[str, int] = {}
        for topic in query_topics:
            t = topic.strip().lower()
            if not t:
                continue
            topic_counts[t] = topic_counts.get(t, 0) + 1

        for topic, count in topic_counts.items():
            if topic not in known_lower and count >= 3:
                gap = CapabilityGap(
                    gap_id=f"gap_{uuid.uuid4().hex[:8]}",
                    title=f"Missing knowledge store: {topic}",
                    description=f"High query frequency for '{topic}' without dedicated store",
                    domain=topic,
                    severity=min(1.0, count / 10.0),
                    frequency=count,
                    confidence=min(1.0, 0.6 + (count / 10.0)),
                    evidence=[]
                )
                gaps.append(gap)

        return gaps

    def detect_from_signals(self, signals: List[DiscoverySignal]) -> List[CapabilityGap]:
        """Detect gaps from discovery signals."""
        gaps: List[CapabilityGap] = []

        grouped: Dict[str, List[DiscoverySignal]] = {}
        for s in signals:
            key = f"{s.signal_type.value}:{s.domain}"
            grouped.setdefault(key, []).append(s)

        for key, items in grouped.items():
            if len(items) < 2:
                continue
            avg_severity = statistics.mean(i.severity for i in items)
            freq = sum(i.frequency for i in items)
            title = f"Gap in {items[0].domain}: {items[0].signal_type.value}"
            gap = CapabilityGap(
                gap_id=f"gap_{uuid.uuid4().hex[:8]}",
                title=title,
                description=f"Repeated signals indicating {items[0].signal_type.value} issues",
                domain=items[0].domain,
                severity=avg_severity,
                frequency=freq,
                confidence=min(1.0, 0.5 + avg_severity),
                evidence=items
            )
            gaps.append(gap)

        return gaps


class OpportunityPrioritizer:
    """Ranks opportunities by impact and feasibility."""

    def score(self, impact: float, feasibility: float) -> float:
        return max(0.0, min(1.0, (impact * 0.6) + (feasibility * 0.4)))

    def prioritize(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        return sorted(opportunities, key=lambda o: o.priority_score, reverse=True)


class IntrospectionAnalyzer:
    """Analyzes logs and performance metrics to generate signals."""

    def analyze_metrics(self, metrics: Dict[str, float]) -> List[DiscoverySignal]:
        signals: List[DiscoverySignal] = []

        latency = metrics.get("avg_latency_ms", 0.0)
        failure_rate = metrics.get("failure_rate", 0.0)
        confusion_rate = metrics.get("confusion_rate", 0.0)

        if latency > 150:
            signals.append(DiscoverySignal(
                signal_id=f"signal_{uuid.uuid4().hex[:8]}",
                signal_type=SignalType.LATENCY,
                domain="system",
                description=f"High latency detected: {latency}ms",
                severity=min(1.0, latency / 300.0),
                frequency=1,
                evidence={"avg_latency_ms": latency}
            ))

        if failure_rate > 0.2:
            signals.append(DiscoverySignal(
                signal_id=f"signal_{uuid.uuid4().hex[:8]}",
                signal_type=SignalType.FAILURE_RATE,
                domain="quality",
                description=f"High failure rate: {failure_rate:.0%}",
                severity=min(1.0, failure_rate),
                frequency=1,
                evidence={"failure_rate": failure_rate}
            ))

        if confusion_rate > 0.15:
            signals.append(DiscoverySignal(
                signal_id=f"signal_{uuid.uuid4().hex[:8]}",
                signal_type=SignalType.USER_CONFUSION,
                domain="ux",
                description=f"User confusion rate high: {confusion_rate:.0%}",
                severity=min(1.0, confusion_rate),
                frequency=1,
                evidence={"confusion_rate": confusion_rate}
            ))

        return signals

    def analyze_logs(self, logs: List[Dict[str, Any]]) -> List[DiscoverySignal]:
        signals: List[DiscoverySignal] = []
        error_count = 0
        confusion_count = 0

        for entry in logs:
            if entry.get("had_error"):
                error_count += 1
            if entry.get("user_confused"):
                confusion_count += 1

        if error_count >= 3:
            signals.append(DiscoverySignal(
                signal_id=f"signal_{uuid.uuid4().hex[:8]}",
                signal_type=SignalType.ERROR,
                domain="system",
                description="Repeated errors in interaction logs",
                severity=min(1.0, error_count / 10.0),
                frequency=error_count,
                evidence={"error_count": error_count}
            ))

        if confusion_count >= 3:
            signals.append(DiscoverySignal(
                signal_id=f"signal_{uuid.uuid4().hex[:8]}",
                signal_type=SignalType.USER_CONFUSION,
                domain="ux",
                description="Repeated user confusion in logs",
                severity=min(1.0, confusion_count / 10.0),
                frequency=confusion_count,
                evidence={"confusion_count": confusion_count}
            ))

        return signals


class ProblemDiscoveryEngine:
    """Main engine for autonomous problem discovery."""

    def __init__(self, world_model):
        self.world_model = world_model
        self.analyzer = IntrospectionAnalyzer()
        self.gap_detector = GapDetector()
        self.prioritizer = OpportunityPrioritizer()

    def discover(self,
                 logs: List[Dict[str, Any]],
                 metrics: Dict[str, float],
                 query_topics: List[str],
                 known_stores: List[str]) -> DiscoveryReport:
        """Run full discovery cycle and return report."""
        signals = []
        signals.extend(self.analyzer.analyze_logs(logs))
        signals.extend(self.analyzer.analyze_metrics(metrics))

        gaps = []
        gaps.extend(self.gap_detector.detect_from_signals(signals))
        gaps.extend(self.gap_detector.detect_from_query_topics(query_topics, known_stores))

        opportunities = self._generate_opportunities(gaps, signals)
        opportunities = self.prioritizer.prioritize(opportunities)

        proposals = [self._proposal_from_opportunity(o) for o in opportunities[:3]]

        summary = {
            "signals": len(signals),
            "gaps": len(gaps),
            "opportunities": len(opportunities),
            "proposals": len(proposals)
        }

        return DiscoveryReport(
            signals=signals,
            gaps=gaps,
            opportunities=opportunities,
            proposals=proposals,
            summary=summary
        )

    def _generate_opportunities(self,
                                gaps: List[CapabilityGap],
                                signals: List[DiscoverySignal]) -> List[Opportunity]:
        opportunities: List[Opportunity] = []

        for gap in gaps:
            impact = min(1.0, (gap.severity + (gap.frequency / 10.0)) / 2)
            feasibility = 0.7 if "knowledge store" in gap.title.lower() else 0.6
            priority = self.prioritizer.score(impact, feasibility)

            opp = Opportunity(
                opportunity_id=f"opp_{uuid.uuid4().hex[:8]}",
                title=f"Address gap: {gap.title}",
                description=gap.description,
                opportunity_type=OpportunityType.NEW_KNOWLEDGE_STORE,
                impact_score=impact,
                feasibility_score=feasibility,
                priority_score=priority,
                related_gaps=[gap.gap_id],
                evidence=gap.evidence
            )
            opportunities.append(opp)

        for sig in signals:
            if sig.signal_type == SignalType.LATENCY:
                impact = min(1.0, sig.severity + 0.2)
                feasibility = 0.8
                priority = self.prioritizer.score(impact, feasibility)
                opportunities.append(Opportunity(
                    opportunity_id=f"opp_{uuid.uuid4().hex[:8]}",
                    title="Implement fast-path for low-complexity queries",
                    description="High latency suggests optimization opportunity",
                    opportunity_type=OpportunityType.OPTIMIZATION,
                    impact_score=impact,
                    feasibility_score=feasibility,
                    priority_score=priority,
                    related_gaps=[],
                    evidence=[sig]
                ))

        return opportunities

    def _proposal_from_opportunity(self, opportunity: Opportunity) -> ProblemProposal:
        expected_improvement = {
            "latency": 0.2 if opportunity.opportunity_type == OpportunityType.OPTIMIZATION else 0.1,
            "accuracy": 0.1 if opportunity.opportunity_type == OpportunityType.NEW_KNOWLEDGE_STORE else 0.05
        }

        validation_plan = [
            "Create synthetic validation set",
            "Run regression tests on existing domains",
            "Measure improvement vs baseline",
            "Verify no safety regressions"
        ]

        actions = [
            f"Design solution for: {opportunity.title}",
            "Implement capability update",
            "Run validation suite",
            "Deploy if gates pass"
        ]

        return ProblemProposal(
            proposal_id=f"proposal_{uuid.uuid4().hex[:8]}",
            title=opportunity.title,
            summary=opportunity.description,
            recommended_actions=actions,
            expected_improvement=expected_improvement,
            validation_plan=validation_plan,
            required_resources=["test_suite", "synthetic_data", "deployment_gate"],
            risk_level="medium"
        )
