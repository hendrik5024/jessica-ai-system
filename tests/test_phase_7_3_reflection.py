"""Phase 7.3: Reflective Intelligence Layer - Comprehensive Test Suite

Tests all five core components of Phase 7.3:
- ReflectionRecord: Immutable records
- ReflectionFactory: Deterministic generation
- ReflectionAnalyzer: Read-only analysis
- ReflectionRegistry: Append-only storage
- ReflectionOrchestrator: Coordinated workflow

Safety Verification:
- No execution capability
- No proposal generation
- No decision influence
- No learning or memory mutation
- No feedback loops
- No background processing
- No autonomy
"""

import pytest
from datetime import datetime
from jessica.execution import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
    create_reflection_record,
    ReflectionFactory,
    ReflectionAnalyzer,
    ReflectionRegistry,
    ReflectionOrchestrator,
)


# ============================================================================
# ReflectionRecord Tests (Immutability)
# ============================================================================


def test_reflection_record_creation():
    """Test basic reflection record creation"""
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test execution completed",
        identified_risks=["Risk 1"],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    assert record.source_type == SourceType.EXECUTION
    assert record.source_id == "exec_123"
    assert record.summary == "Test execution completed"
    assert len(record.identified_risks) == 1
    assert record.confidence_level == ConfidenceLevel.HIGH
    assert record.reflection_id.startswith("refl_")


def test_reflection_record_immutability():
    """Test that reflection records are truly immutable"""
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.MEDIUM,
    )
    
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        record.summary = "Modified"
    
    with pytest.raises(Exception):
        record.source_id = "new_id"


def test_reflection_record_helper_methods():
    """Test helper methods on reflection records"""
    record = create_reflection_record(
        source_type=SourceType.PROPOSAL,
        source_id="prop_456",
        summary="Test proposal",
        identified_risks=["Risk 1", "Risk 2"],
        anomalies=["Anomaly 1"],
        confidence_level=ConfidenceLevel.LOW,
    )
    
    assert record.has_risks() is True
    assert record.has_anomalies() is True
    assert record.risk_count() == 2
    assert record.anomaly_count() == 1


def test_reflection_record_to_dict():
    """Test conversion to dictionary"""
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_789",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    data = record.to_dict()
    assert data["source_type"] == "execution"
    assert data["source_id"] == "exec_789"
    assert data["confidence_level"] == "high"
    assert "reflection_id" in data
    assert "created_at" in data


# ============================================================================
# ReflectionFactory Tests (Determinism)
# ============================================================================


def test_factory_execution_reflection():
    """Test factory generates execution reflections"""
    factory = ReflectionFactory()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "send_email",
        "status": "success",
        "parameters": {"to": "user@example.com"},
    }
    
    reflection, error = factory.reflect_on_execution(execution_data)
    
    assert error is None
    assert reflection is not None
    assert reflection.source_type == SourceType.EXECUTION
    assert reflection.source_id == "exec_123"
    assert "send_email" in reflection.summary


def test_factory_proposal_reflection():
    """Test factory generates proposal reflections"""
    factory = ReflectionFactory()
    
    proposal_data = {
        "proposal_id": "prop_456",
        "requested_action": "delete_file",
        "approval_status": "denied",
        "denial_reason": "Too risky",
        "risk_level": "high",
    }
    
    reflection, error = factory.reflect_on_proposal(proposal_data)
    
    assert error is None
    assert reflection is not None
    assert reflection.source_type == SourceType.PROPOSAL
    assert reflection.source_id == "prop_456"
    assert reflection.has_risks()


def test_factory_determinism():
    """Test factory generates identical reflections for same input"""
    factory = ReflectionFactory()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "test",
        "status": "success",
    }
    
    reflection1, _ = factory.reflect_on_execution(execution_data)
    reflection2, _ = factory.reflect_on_execution(execution_data)
    
    # Deterministic: same input = same output (except timestamps and IDs)
    assert reflection1.summary == reflection2.summary
    assert reflection1.identified_risks == reflection2.identified_risks
    assert reflection1.anomalies == reflection2.anomalies
    assert reflection1.confidence_level == reflection2.confidence_level


def test_factory_risk_identification():
    """Test factory identifies risks correctly"""
    factory = ReflectionFactory()
    
    # High-risk proposal
    proposal_data = {
        "proposal_id": "prop_789",
        "requested_action": "delete_database",
        "approval_status": "denied",
        "risk_level": "high",
    }
    
    reflection, _ = factory.reflect_on_proposal(proposal_data)
    
    assert reflection.has_risks()
    assert reflection.risk_count() > 0


def test_factory_disable_enable():
    """Test factory safety switches"""
    factory = ReflectionFactory()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "test",
        "status": "success",
    }
    
    # Disable
    factory.disable()
    reflection, error = factory.reflect_on_execution(execution_data)
    assert reflection is None
    assert "disabled" in error.lower()
    
    # Re-enable
    factory.enable()
    reflection, error = factory.reflect_on_execution(execution_data)
    assert reflection is not None
    assert error is None


# ============================================================================
# ReflectionAnalyzer Tests (Read-Only)
# ============================================================================


def test_analyzer_single_analysis():
    """Test analyzer analyzes single reflection"""
    analyzer = ReflectionAnalyzer()
    
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=["Risk 1", "Risk 2"],
        anomalies=["Anomaly 1"],
        confidence_level=ConfidenceLevel.MEDIUM,
    )
    
    analysis = analyzer.analyze_single_reflection(record)
    
    assert analysis["risk_level"] == "medium"
    assert analysis["anomaly_level"] == "low"
    assert analysis["has_issues"] is True
    assert analysis["issue_count"] == 3


def test_analyzer_aggregation():
    """Test analyzer aggregates multiple reflections"""
    analyzer = ReflectionAnalyzer()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary="Test",
            identified_risks=["Risk"] * i,
            anomalies=[],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(3)
    ]
    
    aggregation = analyzer.aggregate_reflections(records)
    
    assert aggregation["total_reflections"] == 3
    assert aggregation["total_risks"] == 0 + 1 + 2
    assert aggregation["by_source_type"]["execution"] == 3


def test_analyzer_filtering():
    """Test analyzer filtering methods"""
    analyzer = ReflectionAnalyzer()
    
    exec_record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_1",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    prop_record = create_reflection_record(
        source_type=SourceType.PROPOSAL,
        source_id="prop_1",
        summary="Test",
        identified_risks=["Risk"],
        anomalies=[],
        confidence_level=ConfidenceLevel.LOW,
    )
    
    records = [exec_record, prop_record]
    
    # Filter by source type
    exec_only = analyzer.filter_by_source_type(records, SourceType.EXECUTION)
    assert len(exec_only) == 1
    assert exec_only[0].source_type == SourceType.EXECUTION
    
    # Filter with risks
    with_risks = analyzer.filter_with_risks(records)
    assert len(with_risks) == 1
    assert with_risks[0].has_risks()
    
    # Filter by confidence
    high_conf = analyzer.filter_by_confidence(records, ConfidenceLevel.HIGH)
    assert len(high_conf) == 1


def test_analyzer_sorting():
    """Test analyzer sorting methods"""
    analyzer = ReflectionAnalyzer()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary="Test",
            identified_risks=["Risk"] * i,
            anomalies=[],
            confidence_level=ConfidenceLevel.MEDIUM,
        )
        for i in [3, 1, 2]
    ]
    
    sorted_records = analyzer.sort_by_risk_count(records, descending=True)
    
    assert sorted_records[0].risk_count() == 3
    assert sorted_records[1].risk_count() == 2
    assert sorted_records[2].risk_count() == 1


def test_analyzer_risk_summary():
    """Test analyzer risk summarization"""
    analyzer = ReflectionAnalyzer()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary="Test",
            identified_risks=["Common Risk", "Unique Risk"],
            anomalies=[],
            confidence_level=ConfidenceLevel.MEDIUM,
        )
        for i in range(2)
    ]
    
    summary = analyzer.get_risk_summary(records)
    
    assert summary["total_risks"] == 4
    assert len(summary["unique_risks"]) == 2  # unique_risks is a set
    assert "Common Risk" in summary["risk_frequency"]
    assert summary["most_common_risk"] in ["Common Risk", "Unique Risk"]


def test_analyzer_read_only():
    """Test analyzer never mutates input data"""
    analyzer = ReflectionAnalyzer()
    
    original = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=["Risk"],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    records = [original]
    
    # Run all operations
    analyzer.analyze_single_reflection(original)
    analyzer.aggregate_reflections(records)
    analyzer.filter_by_source_type(records, SourceType.EXECUTION)
    analyzer.sort_by_risk_count(records)
    
    # Original should be unchanged
    assert original.source_id == "exec_123"
    assert original.risk_count() == 1


# ============================================================================
# ReflectionRegistry Tests (Append-Only)
# ============================================================================


def test_registry_add_reflection():
    """Test registry adds reflections"""
    registry = ReflectionRegistry()
    
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    error = registry.add_reflection(record)
    assert error is None
    assert registry.count_reflections() == 1


def test_registry_duplicate_prevention():
    """Test registry prevents duplicate reflections"""
    registry = ReflectionRegistry()
    
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    error1 = registry.add_reflection(record)
    error2 = registry.add_reflection(record)
    
    assert error1 is None
    assert error2 is not None
    assert "already exists" in error2
    assert registry.count_reflections() == 1


def test_registry_chronological_order():
    """Test registry maintains chronological order"""
    registry = ReflectionRegistry()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id=f"exec_{i}",
            summary="Test",
            identified_risks=[],
            anomalies=[],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(3)
    ]
    
    for record in records:
        registry.add_reflection(record)
    
    all_reflections = registry.get_all_reflections()
    
    for i, reflection in enumerate(all_reflections):
        assert reflection.source_id == f"exec_{i}"


def test_registry_query_by_id():
    """Test registry queries by reflection ID"""
    registry = ReflectionRegistry()
    
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    registry.add_reflection(record)
    
    retrieved = registry.get_reflection_by_id(record.reflection_id)
    assert retrieved is not None
    assert retrieved.reflection_id == record.reflection_id


def test_registry_query_by_source():
    """Test registry queries by source ID"""
    registry = ReflectionRegistry()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION,
            source_id="exec_123",
            summary=f"Test {i}",
            identified_risks=[],
            anomalies=[],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(2)
    ]
    
    for record in records:
        registry.add_reflection(record)
    
    by_source = registry.get_reflections_by_source_id("exec_123")
    assert len(by_source) == 2


def test_registry_statistics():
    """Test registry statistics"""
    registry = ReflectionRegistry()
    
    records = [
        create_reflection_record(
            source_type=SourceType.EXECUTION if i % 2 == 0 else SourceType.PROPOSAL,
            source_id=f"source_{i}",
            summary="Test",
            identified_risks=["Risk"] if i == 0 else [],
            anomalies=["Anomaly"] if i == 1 else [],
            confidence_level=ConfidenceLevel.HIGH,
        )
        for i in range(4)
    ]
    
    for record in records:
        registry.add_reflection(record)
    
    stats = registry.get_registry_stats()
    
    assert stats["total_reflections"] == 4
    assert stats["by_source_type"]["execution"] == 2
    assert stats["by_source_type"]["proposal"] == 2
    assert stats["with_risks"] == 1
    assert stats["with_anomalies"] == 1


def test_registry_append_only():
    """Test registry is truly append-only (no deletion)"""
    registry = ReflectionRegistry()
    
    record = create_reflection_record(
        source_type=SourceType.EXECUTION,
        source_id="exec_123",
        summary="Test",
        identified_risks=[],
        anomalies=[],
        confidence_level=ConfidenceLevel.HIGH,
    )
    
    registry.add_reflection(record)
    initial_count = registry.count_reflections()
    
    # No delete method should exist
    assert not hasattr(registry, "delete_reflection")
    assert not hasattr(registry, "remove_reflection")
    assert not hasattr(registry, "clear")
    
    # Count should remain unchanged
    assert registry.count_reflections() == initial_count


# ============================================================================
# ReflectionOrchestrator Tests (Workflow)
# ============================================================================


def test_orchestrator_execution_workflow():
    """Test orchestrator complete execution workflow"""
    orchestrator = ReflectionOrchestrator()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "send_email",
        "status": "success",
        "parameters": {"to": "user@example.com"},
    }
    
    reflection, error = orchestrator.reflect_on_execution(execution_data)
    
    assert error is None
    assert reflection is not None
    assert reflection.source_type == SourceType.EXECUTION
    assert reflection.source_id == "exec_123"
    assert orchestrator.has_reflection_for_source("exec_123")


def test_orchestrator_proposal_workflow():
    """Test orchestrator complete proposal workflow"""
    orchestrator = ReflectionOrchestrator()
    
    proposal_data = {
        "proposal_id": "prop_456",
        "requested_action": "delete_file",
        "approval_status": "denied",
        "risk_level": "high",
    }
    
    reflection, error = orchestrator.reflect_on_proposal(proposal_data)
    
    assert error is None
    assert reflection is not None
    assert reflection.source_type == SourceType.PROPOSAL
    assert reflection.source_id == "prop_456"


def test_orchestrator_store_option():
    """Test orchestrator store_in_registry option"""
    orchestrator = ReflectionOrchestrator()
    
    execution_data = {
        "execution_id": "exec_789",
        "action": "test",
        "status": "success",
    }
    
    # Don't store
    reflection, error = orchestrator.reflect_on_execution(
        execution_data,
        store_in_registry=False,
    )
    
    assert error is None
    assert reflection is not None
    assert not orchestrator.has_reflection_for_source("exec_789")


def test_orchestrator_query_delegation():
    """Test orchestrator delegates queries to registry"""
    orchestrator = ReflectionOrchestrator()
    
    # Add reflections
    for i in range(3):
        orchestrator.reflect_on_execution({
            "execution_id": f"exec_{i}",
            "action": "test",
            "status": "success",
        })
    
    # Query delegation
    all_reflections = orchestrator.get_all_reflections()
    assert len(all_reflections) == 3
    
    count = orchestrator.count_reflections()
    assert count == 3
    
    stats = orchestrator.get_reflection_stats()
    assert stats["total_reflections"] == 3


def test_orchestrator_disable_enable():
    """Test orchestrator safety switches"""
    orchestrator = ReflectionOrchestrator()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "test",
        "status": "success",
    }
    
    # Disable
    orchestrator.disable()
    reflection, error = orchestrator.reflect_on_execution(execution_data)
    assert reflection is None
    assert "disabled" in error.lower()
    
    # Re-enable
    orchestrator.enable()
    reflection, error = orchestrator.reflect_on_execution(execution_data)
    assert reflection is not None
    assert error is None


def test_orchestrator_coordinates_factory_and_registry():
    """Test orchestrator coordinates factory and registry"""
    orchestrator = ReflectionOrchestrator()
    
    execution_data = {
        "execution_id": "exec_123",
        "action": "test",
        "status": "success",
    }
    
    # Generate and store
    reflection, error = orchestrator.reflect_on_execution(execution_data)
    
    assert error is None
    assert reflection is not None
    
    # Verify stored in registry
    retrieved = orchestrator.get_reflections_for_source("exec_123")
    assert len(retrieved) == 1
    assert retrieved[0].reflection_id == reflection.reflection_id


# ============================================================================
# Safety Constraint Verification
# ============================================================================


def test_no_execution_capability():
    """Verify reflective layer cannot execute actions"""
    orchestrator = ReflectionOrchestrator()
    
    # No execute methods
    assert not hasattr(orchestrator, "execute")
    assert not hasattr(orchestrator, "execute_action")
    assert not hasattr(orchestrator, "run_action")


def test_no_proposal_generation():
    """Verify reflective layer cannot generate proposals"""
    orchestrator = ReflectionOrchestrator()
    
    # No propose methods
    assert not hasattr(orchestrator, "propose")
    assert not hasattr(orchestrator, "generate_proposal")
    assert not hasattr(orchestrator, "create_proposal")


def test_no_decision_influence():
    """Verify reflective layer cannot influence decisions"""
    orchestrator = ReflectionOrchestrator()
    factory = ReflectionFactory()
    
    # No decide/approve methods
    assert not hasattr(orchestrator, "decide")
    assert not hasattr(orchestrator, "approve")
    assert not hasattr(factory, "influence_decision")


def test_no_learning_capability():
    """Verify reflective layer cannot learn or adapt"""
    factory = ReflectionFactory()
    
    # Generate two reflections with same action
    data1 = {"execution_id": "exec_1", "action": "test", "status": "success"}
    data2 = {"execution_id": "exec_1", "action": "test", "status": "success"}  # Same source_id
    
    reflection1, _ = factory.reflect_on_execution(data1)
    reflection2, _ = factory.reflect_on_execution(data2)
    
    # Summaries should be deterministic (no learning)
    assert reflection1.summary == reflection2.summary
    assert reflection1.identified_risks == reflection2.identified_risks


def test_no_background_processing():
    """Verify reflective layer has no background processing"""
    orchestrator = ReflectionOrchestrator()
    
    # No async/background methods
    assert not hasattr(orchestrator, "start_background_reflection")
    assert not hasattr(orchestrator, "watch")
    assert not hasattr(orchestrator, "monitor")


def test_no_autonomy():
    """Verify reflective layer requires explicit human initiation"""
    orchestrator = ReflectionOrchestrator()
    
    # No automatic methods
    assert not hasattr(orchestrator, "auto_reflect")
    assert not hasattr(orchestrator, "reflect_continuously")
    assert not hasattr(orchestrator, "schedule_reflection")
