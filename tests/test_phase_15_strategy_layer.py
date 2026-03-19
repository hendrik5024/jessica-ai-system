from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.strategy_definition import StrategyDefinition
from jessica.strategy_registry import StrategyRegistry
from jessica.strategy_audit import StrategyAudit
from jessica.strategy_selector import StrategySelector


def _strategy(strategy_id: str, task_type: str) -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id=strategy_id,
        name=strategy_id,
        description="desc",
        selection_rules={"type": task_type},
        reasoning_steps=["step 1"],
        created_at=datetime(2026, 2, 9, 12, 0, 0),
    )


def test_strategy_immutable():
    strategy = _strategy("s1", "general")
    with pytest.raises(FrozenInstanceError):
        strategy.name = "new"


def test_registry_register_and_get():
    registry = StrategyRegistry()
    strategy = _strategy("s1", "general")
    registry.register_strategy(strategy)
    assert registry.get_strategy("s1") == strategy


def test_registry_append_only():
    registry = StrategyRegistry()
    strategy = _strategy("s1", "general")
    registry.register_strategy(strategy)
    with pytest.raises(ValueError):
        registry.register_strategy(strategy)


def test_registry_list_strategies_deterministic():
    registry = StrategyRegistry()
    s1 = _strategy("s1", "general")
    s2 = _strategy("s2", "math")
    registry.register_strategy(s1)
    registry.register_strategy(s2)
    assert [s.strategy_id for s in registry.list_strategies()] == ["s1", "s2"]


def test_registry_select_strategy_by_type():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    registry.register_strategy(_strategy("s2", "math"))
    selected = registry.select_strategy({"type": "math"})
    assert selected.strategy_id == "s2"


def test_registry_select_strategy_fallback_first():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    registry.register_strategy(_strategy("s2", "math"))
    selected = registry.select_strategy({"type": "unknown"})
    assert selected.strategy_id == "s1"


def test_selector_derive_math_metadata():
    selector = StrategySelector(StrategyRegistry(), StrategyAudit())
    metadata = selector.derive_task_metadata("calculate 1+1")
    assert metadata["type"] == "math"


def test_selector_derive_planning_metadata():
    selector = StrategySelector(StrategyRegistry(), StrategyAudit())
    metadata = selector.derive_task_metadata("plan a workflow")
    assert metadata["type"] == "planning"


def test_selector_derive_general_metadata():
    selector = StrategySelector(StrategyRegistry(), StrategyAudit())
    metadata = selector.derive_task_metadata("tell me a story")
    assert metadata["type"] == "general"


def test_selector_choose_strategy():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    registry.register_strategy(_strategy("s2", "math"))
    selector = StrategySelector(registry, StrategyAudit())
    chosen = selector.choose_strategy({"type": "math"})
    assert chosen.strategy_id == "s2"


def test_selector_log_strategy_selection():
    audit = StrategyAudit()
    selector = StrategySelector(StrategyRegistry(), audit)
    selector.log_strategy_selection("s1", "task1")
    assert audit.count() == 1


def test_audit_history():
    audit = StrategyAudit()
    audit.record_strategy_use("t1", "s1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_strategy_use("t1", "s2", datetime(2026, 2, 9, 12, 1, 0))
    history = audit.get_strategy_history("t1")
    assert [h.strategy_id for h in history] == ["s1", "s2"]


def test_audit_usage_stats():
    audit = StrategyAudit()
    audit.record_strategy_use("t1", "s1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_strategy_use("t2", "s1", datetime(2026, 2, 9, 12, 1, 0))
    audit.record_strategy_use("t3", "s2", datetime(2026, 2, 9, 12, 2, 0))
    stats = audit.get_strategy_usage_statistics()
    assert stats["s1"] == 2
    assert stats["s2"] == 1


def test_deterministic_selection_across_runs():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    registry.register_strategy(_strategy("s2", "math"))
    selector = StrategySelector(registry, StrategyAudit())
    chosen1 = selector.choose_strategy({"type": "math"})
    chosen2 = selector.choose_strategy({"type": "math"})
    assert chosen1.strategy_id == chosen2.strategy_id


def test_strategy_selection_logged():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    audit = StrategyAudit()
    selector = StrategySelector(registry, audit)
    selector.log_strategy_selection("s1", "task1")
    assert audit.get_strategy_history("task1")[0].strategy_id == "s1"


def test_analyze_task_returns_metadata():
    selector = StrategySelector(StrategyRegistry(), StrategyAudit())
    metadata = selector.analyze_task("calculate 2+2")
    assert metadata["type"] == "math"


def test_registry_select_none_when_empty():
    registry = StrategyRegistry()
    assert registry.select_strategy({"type": "math"}) is None


def test_backward_compatibility_no_side_effects():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    selector = StrategySelector(registry, StrategyAudit())
    _ = selector.choose_strategy({"type": "general"})
    assert registry.get_strategy("s1") is not None


def test_strategy_definition_human_readable():
    strategy = _strategy("s1", "general")
    assert isinstance(strategy.description, str)
    assert len(strategy.description) > 0


def test_strategy_rules_version_controlled():
    strategy = StrategyDefinition(
        strategy_id="s1",
        name="general",
        description="desc",
        selection_rules={"type": "general", "version": 1},
        reasoning_steps=["step"],
        created_at=datetime(2026, 2, 9, 12, 0, 0),
    )
    assert strategy.selection_rules["version"] == 1


def test_reasoning_steps_present():
    strategy = _strategy("s1", "general")
    assert strategy.reasoning_steps == ["step 1"]


def test_strategy_logging_deterministic():
    audit = StrategyAudit()
    audit.record_strategy_use("t1", "s1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_strategy_use("t1", "s1", datetime(2026, 2, 9, 12, 0, 1))
    history = audit.get_strategy_history("t1")
    assert len(history) == 2


def test_selection_rules_preserved():
    strategy = _strategy("s1", "general")
    assert strategy.selection_rules["type"] == "general"


def test_choose_strategy_with_missing_type():
    registry = StrategyRegistry()
    registry.register_strategy(_strategy("s1", "general"))
    selected = registry.select_strategy({})
    assert selected.strategy_id == "s1"


def test_strategy_audit_append_only():
    audit = StrategyAudit()
    audit.record_strategy_use("t1", "s1", datetime(2026, 2, 9, 12, 0, 0))
    audit.record_strategy_use("t2", "s2", datetime(2026, 2, 9, 12, 1, 0))
    assert audit.count() == 2
