from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.skill_definition import SkillDefinition
from jessica.capability_gap_analyzer import CapabilityGapAnalyzer
from jessica.skill_planner import SkillPlanner
from jessica.skill_registry import SkillRegistry
from jessica.skill_planning_audit import SkillPlanningAudit


def _skill(skill_id: str) -> SkillDefinition:
    return SkillDefinition(
        skill_id=skill_id,
        name=skill_id,
        description="desc",
        capability_domain="domain",
        prerequisites=["prereq"],
        estimated_complexity="medium",
        created_at=datetime(2026, 2, 9, 12, 0, 0),
    )


def test_skill_definition_immutable():
    skill = _skill("s1")
    with pytest.raises(FrozenInstanceError):
        skill.name = "new"


def test_gap_detection_deterministic():
    analyzer = CapabilityGapAnalyzer()
    gaps1 = analyzer.detect_missing_capabilities({"missing_capabilities": ["a", "b"]})
    gaps2 = analyzer.detect_missing_capabilities({"missing_capabilities": ["a", "b"]})
    assert gaps1 == gaps2


def test_gap_ranking_deterministic():
    analyzer = CapabilityGapAnalyzer()
    ranked = analyzer.rank_capability_gaps(["b", "a"]) 
    assert ranked == ["a", "b"]


def test_skill_planning_deterministic():
    planner = SkillPlanner()
    plan1 = planner.generate_skill_plan("gap")
    plan2 = planner.generate_skill_plan("gap")
    assert plan1["steps"] == plan2["steps"]


def test_estimate_learning_steps():
    planner = SkillPlanner()
    skill = _skill("s1")
    steps = planner.estimate_learning_steps(skill)
    assert "study" in steps[1]


def test_generate_learning_sequence():
    planner = SkillPlanner()
    skill = _skill("s1")
    assert planner.generate_learning_sequence(skill) == planner.estimate_learning_steps(skill)


def test_registry_register_known_skill():
    registry = SkillRegistry()
    skill = _skill("s1")
    registry.register_skill(skill)
    assert registry.list_known_skills()[0].skill_id == "s1"


def test_registry_register_proposed_skill():
    registry = SkillRegistry()
    skill = _skill("s2")
    registry.register_skill(skill, proposed=True)
    assert registry.list_proposed_skills()[0].skill_id == "s2"


def test_registry_get_skill_from_known_or_proposed():
    registry = SkillRegistry()
    skill = _skill("s3")
    registry.register_skill(skill, proposed=True)
    assert registry.get_skill("s3") == skill


def test_registry_append_only():
    registry = SkillRegistry()
    skill = _skill("s1")
    registry.register_skill(skill)
    with pytest.raises(ValueError):
        registry.register_skill(skill)


def test_audit_logging():
    audit = SkillPlanningAudit()
    audit.record_skill_plan("s1", "plan1", datetime(2026, 2, 9, 12, 0, 0))
    assert audit.count() == 1


def test_audit_history():
    audit = SkillPlanningAudit()
    audit.record_skill_plan("s1", "plan1", datetime(2026, 2, 9, 12, 0, 0))
    history = audit.get_skill_planning_history()
    assert history[0].skill_id == "s1"


def test_audit_gap_statistics():
    audit = SkillPlanningAudit()
    audit.record_skill_plan("s1", "plan1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_skill_plan("s1", "plan2", datetime(2026, 2, 9, 12, 1, 0))
    stats = audit.get_capability_gap_statistics()
    assert stats["s1"] == 2


def test_backward_compatibility_no_side_effects():
    registry = SkillRegistry()
    registry.register_skill(_skill("s1"))
    assert registry.get_skill("s1") is not None


def test_skill_plan_advisory_only():
    planner = SkillPlanner()
    plan = planner.generate_skill_plan("gap")
    assert isinstance(plan["steps"], list)


def test_gap_analyzer_analyze_task_failure():
    analyzer = CapabilityGapAnalyzer()
    gaps = analyzer.analyze_task_failure({"missing_capabilities": ["x"]})
    assert gaps == ["x"]


def test_registry_order_deterministic():
    registry = SkillRegistry()
    registry.register_skill(_skill("s1"))
    registry.register_skill(_skill("s2"))
    assert [s.skill_id for s in registry.list_known_skills()] == ["s1", "s2"]


def test_proposed_order_deterministic():
    registry = SkillRegistry()
    registry.register_skill(_skill("s1"), proposed=True)
    registry.register_skill(_skill("s2"), proposed=True)
    assert [s.skill_id for s in registry.list_proposed_skills()] == ["s1", "s2"]


def test_audit_append_only():
    audit = SkillPlanningAudit()
    audit.record_skill_plan("s1", "plan1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_skill_plan("s1", "plan2", datetime(2026, 2, 9, 12, 1, 0))
    assert audit.count() == 2


def test_skill_plan_has_created_at():
    planner = SkillPlanner()
    plan = planner.generate_skill_plan("gap")
    assert plan["created_at"] == datetime(2026, 2, 9, 12, 0, 0)


def test_gap_detection_empty():
    analyzer = CapabilityGapAnalyzer()
    assert analyzer.detect_missing_capabilities({}) == []


def test_skill_registry_get_none_for_missing():
    registry = SkillRegistry()
    assert registry.get_skill("missing") is None


def test_skill_planner_steps_consistent():
    planner = SkillPlanner()
    plan1 = planner.generate_skill_plan("gap")
    plan2 = planner.generate_skill_plan("gap")
    assert plan1["steps"] == plan2["steps"]


def test_skill_audit_deterministic_stats():
    audit = SkillPlanningAudit()
    audit.record_skill_plan("s1", "plan1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_skill_plan("s1", "plan2", datetime(2026, 2, 9, 12, 1, 0))
    assert audit.get_capability_gap_statistics()["s1"] == 2


def test_skill_registry_known_list_empty():
    registry = SkillRegistry()
    assert registry.list_known_skills() == []


def test_skill_registry_proposed_list_empty():
    registry = SkillRegistry()
    assert registry.list_proposed_skills() == []
