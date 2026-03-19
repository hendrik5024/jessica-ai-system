"""
Tests for autonomous problem discovery system (Phase 5).
"""

import pytest
from jessica.unified_world_model import (
    WorldModel,
    ProblemDiscoveryEngine,
    SignalType,
    OpportunityType
)


@pytest.fixture
def world():
    return WorldModel()


@pytest.fixture
def engine(world):
    return ProblemDiscoveryEngine(world)


def test_detect_missing_knowledge_store(engine):
    logs = []
    metrics = {}
    query_topics = [
        "time management", "time management", "time management",
        "decision making", "decision making"
    ]
    known_stores = ["decision making", "chess", "recipes"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    gaps = [g for g in report.gaps if "time management" in g.title.lower()]
    assert len(gaps) == 1
    assert gaps[0].frequency >= 3


def test_latency_opportunity_detected(engine):
    logs = []
    metrics = {"avg_latency_ms": 210}
    query_topics = []
    known_stores = []

    report = engine.discover(logs, metrics, query_topics, known_stores)

    opportunities = [o for o in report.opportunities if o.opportunity_type == OpportunityType.OPTIMIZATION]
    assert len(opportunities) >= 1
    assert "fast-path" in opportunities[0].title.lower()


def test_opportunity_prioritization(engine):
    logs = [{"had_error": True} for _ in range(5)]
    metrics = {"avg_latency_ms": 180, "failure_rate": 0.3}
    query_topics = ["chess endgame"] * 5
    known_stores = ["chess openings", "chess tactics"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    assert len(report.opportunities) >= 2
    priorities = [o.priority_score for o in report.opportunities]
    assert priorities == sorted(priorities, reverse=True)


def test_proposal_generation(engine):
    logs = []
    metrics = {"avg_latency_ms": 190}
    query_topics = ["time management"] * 4
    known_stores = ["decision making"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    assert len(report.proposals) >= 1
    proposal = report.proposals[0]
    assert len(proposal.validation_plan) >= 3
    assert len(proposal.recommended_actions) >= 3


def test_full_autonomous_cycle(engine):
    logs = [
        {"had_error": True},
        {"had_error": True},
        {"had_error": True},
        {"user_confused": True},
        {"user_confused": True},
        {"user_confused": True}
    ]
    metrics = {"avg_latency_ms": 200, "failure_rate": 0.25, "confusion_rate": 0.2}
    query_topics = ["weekly meal planning"] * 5 + ["travel" for _ in range(2)]
    known_stores = ["recipes", "travel"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    assert report.summary["signals"] >= 2
    assert report.summary["gaps"] >= 1
    assert report.summary["opportunities"] >= 2
    assert report.summary["proposals"] >= 1


# Benchmarks (Phase 5 gates)

def test_benchmark_opportunity_count(engine):
    logs = [{"had_error": True} for _ in range(6)]
    metrics = {"avg_latency_ms": 220, "failure_rate": 0.3, "confusion_rate": 0.2}
    query_topics = ["time management"] * 5 + ["endgame"] * 5 + ["negotiation"] * 5
    known_stores = ["chess", "recipes", "travel"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    assert len(report.opportunities) >= 3


def test_benchmark_gap_actionability(engine):
    logs = []
    metrics = {}
    query_topics = ["time management"] * 4
    known_stores = ["decision making"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    assert any("knowledge store" in o.description.lower() or "gap" in o.title.lower()
               for o in report.opportunities)


def test_benchmark_proposal_validity(engine):
    logs = []
    metrics = {"avg_latency_ms": 200}
    query_topics = ["weekly meal planning"] * 4
    known_stores = ["recipes"]

    report = engine.discover(logs, metrics, query_topics, known_stores)

    for proposal in report.proposals:
        assert proposal.expected_improvement
        assert proposal.validation_plan
        assert proposal.required_resources
