"""
Tests for continual learning system (Phase 4).

Verifies:
- Streaming learning pipeline
- Online safety verification
- Catastrophic forgetting detection
- Rollback mechanisms
- Convergence detection
"""

import pytest
from datetime import datetime
from jessica.unified_world_model import (
    WorldModel,
    Actor, Goal, Constraint, State, CausalLink,
    ContinualLearningEngine,
    LearningSignal,
    ModelSnapshot,
    SafetyVerifier,
    CatastrophicForgettingDetector,
    ValidationResult,
    LearningMode
)


@pytest.fixture
def world():
    """Create test world model."""
    w = WorldModel()
    
    # Register chess domain
    w.register_domain("chess")
    player = Actor("player", capabilities=["strategic_thinking"])
    w.add_entity(player)
    
    # Register cooking domain
    w.register_domain("cooking")
    chef = Actor("chef", capabilities=["recipe_execution"])
    w.add_entity(chef)
    
    return w


@pytest.fixture
def learning_engine(world):
    """Create test learning engine."""
    return ContinualLearningEngine(world)


# ===========================
# Test: Learning Signal Collection
# ===========================

def test_learning_signal_creation():
    """Test creating a learning signal."""
    signal = LearningSignal(
        signal_id="sig_1",
        domain="chess",
        input_context={"position": "e4"},
        predicted_output="Nf3",
        actual_output="d4",
        error_magnitude=0.3
    )
    
    assert signal.signal_id == "sig_1"
    assert signal.domain == "chess"
    assert signal.error_magnitude == 0.3
    assert signal.compute_loss() == 0.3  # Different outputs


def test_collect_learning_signal(learning_engine):
    """Test collecting a learning signal."""
    signal_id = learning_engine.collect_learning_signal(
        domain="chess",
        input_context={"position": "e4"},
        predicted="Nf3",
        actual="d4",
        error=0.3
    )
    
    assert signal_id == "signal_0"
    assert len(learning_engine.streaming_buffer) == 1
    assert len(learning_engine.batch_buffer) == 1  # Hybrid mode


def test_streaming_buffer_threshold(learning_engine):
    """Test that streaming buffer triggers update at threshold."""
    # Collect 10 signals (threshold)
    for i in range(10):
        learning_engine.collect_learning_signal(
            domain="chess",
            input_context={"move": i},
            predicted=f"move_{i}",
            actual=f"move_{i+1}",
            error=0.1
        )
    
    # Buffer should be processed and cleared
    assert len(learning_engine.streaming_buffer) == 0
    # Should have created candidate snapshot
    assert len(learning_engine.snapshots) > 1


# ===========================
# Test: Catastrophic Forgetting Detection
# ===========================

def test_forgetting_detector_baseline():
    """Test setting baseline performance."""
    detector = CatastrophicForgettingDetector(threshold=0.05)
    
    detector.set_baseline("chess", 0.75)
    assert detector.baseline_performance["chess"] == 0.75


def test_forgetting_detection_no_degradation():
    """Test no forgetting when performance stable."""
    detector = CatastrophicForgettingDetector(threshold=0.05)
    detector.set_baseline("chess", 0.75)
    
    is_forgetting, delta = detector.check_forgetting("chess", 0.76)
    
    assert not is_forgetting
    assert delta == pytest.approx(0.01)


def test_forgetting_detection_with_degradation():
    """Test forgetting detected when performance drops."""
    detector = CatastrophicForgettingDetector(threshold=0.05)
    detector.set_baseline("chess", 0.75)
    
    is_forgetting, delta = detector.check_forgetting("chess", 0.65)
    
    assert is_forgetting
    assert delta == pytest.approx(-0.10)


def test_forgetting_report():
    """Test getting forgetting report across domains."""
    detector = CatastrophicForgettingDetector(threshold=0.05)
    
    detector.set_baseline("chess", 0.75)
    detector.set_baseline("cooking", 0.70)
    detector.set_baseline("travel", 0.68)
    
    detector.check_forgetting("chess", 0.60)  # Degraded
    detector.check_forgetting("cooking", 0.71)  # Stable
    detector.check_forgetting("travel", 0.75)  # Improved
    
    report = detector.get_forgetting_report()
    
    assert report["domains_tracked"] == 3
    assert len(report["forgetting_detected"]) == 1
    assert report["forgetting_detected"][0]["domain"] == "chess"
    assert "cooking" in report["stable_domains"]
    assert len(report["improved_domains"]) == 1


# ===========================
# Test: Safety Verification
# ===========================

def test_safety_verifier_creation():
    """Test creating safety verifier."""
    verifier = SafetyVerifier()
    
    verifier.register_test_suite("chess", [
        {"input": "e4", "expected": "e5"}
    ])
    
    assert "chess" in verifier.test_suites


def test_safety_verification_valid_update():
    """Test verifying a valid model update."""
    verifier = SafetyVerifier()
    
    baseline = ModelSnapshot(
        snapshot_id="base",
        version="v1",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.75, "cooking": 0.70},
        safety_verification=True
    )
    
    candidate = ModelSnapshot(
        snapshot_id="candidate",
        version="v2",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.80, "cooking": 0.71},  # Both improved
        safety_verification=False
    )
    
    result = verifier.verify(candidate, baseline)
    
    assert result.valid
    assert not result.catastrophic_forgetting
    assert len(result.safety_violations) == 0
    assert result.performance_delta["chess"] == pytest.approx(0.05)


def test_safety_verification_forgetting():
    """Test detecting catastrophic forgetting."""
    verifier = SafetyVerifier()
    
    baseline = ModelSnapshot(
        snapshot_id="base",
        version="v1",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.75, "cooking": 0.70},
        safety_verification=True
    )
    
    candidate = ModelSnapshot(
        snapshot_id="candidate",
        version="v2",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.80, "cooking": 0.60},  # Cooking degraded
        safety_verification=False
    )
    
    result = verifier.verify(candidate, baseline)
    
    assert not result.valid
    assert result.catastrophic_forgetting
    assert "cooking" in result.forgetting_domains


def test_safety_verification_with_constraints():
    """Test safety verification with custom constraints."""
    verifier = SafetyVerifier()
    
    # Add safety constraint
    def no_negative_performance(snapshot):
        return all(v >= 0 for v in snapshot.performance_metrics.values())
    
    verifier.add_safety_constraint(no_negative_performance)
    
    baseline = ModelSnapshot(
        snapshot_id="base",
        version="v1",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.75},
        safety_verification=True
    )
    
    candidate = ModelSnapshot(
        snapshot_id="candidate",
        version="v2",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.80},
        safety_verification=False
    )
    
    result = verifier.verify(candidate, baseline)
    
    assert result.valid
    assert len(result.safety_violations) == 0


# ===========================
# Test: Continual Learning Engine
# ===========================

def test_engine_initialization(learning_engine):
    """Test engine initializes with base model."""
    assert learning_engine.deployed_version == "base_v1"
    assert "base_v1" in learning_engine.snapshots
    assert learning_engine.mode == LearningMode.HYBRID


def test_streaming_learning_flow(learning_engine):
    """Test end-to-end streaming learning."""
    initial_version = learning_engine.deployed_version
    
    # Collect signals that show improvement needed
    for i in range(10):
        learning_engine.collect_learning_signal(
            domain="chess",
            input_context={"move": i},
            predicted=f"pred_{i}",
            actual=f"actual_{i}",
            error=0.2  # Significant error
        )
    
    # Should have created and possibly deployed update
    assert len(learning_engine.snapshots) > 1
    # Streaming buffer should be processed
    assert len(learning_engine.streaming_buffer) == 0


def test_rollback_mechanism(learning_engine):
    """Test rolling back to previous version."""
    # Collect signals to trigger update
    for i in range(10):
        learning_engine.collect_learning_signal(
            domain="chess",
            input_context={"move": i},
            predicted="pred",
            actual="actual",
            error=0.2
        )
    
    initial_version = learning_engine.deployed_version
    
    # Manually create and deploy another update
    candidate = ModelSnapshot(
        snapshot_id="manual_v2",
        version="manual_v2",
        timestamp=datetime.now().timestamp(),
        parameters={},
        performance_metrics={"chess": 0.80},
        safety_verification=True
    )
    learning_engine.snapshots["manual_v2"] = candidate
    learning_engine._deploy_update(candidate)
    
    deployed_after_update = learning_engine.deployed_version
    assert deployed_after_update == "manual_v2"
    
    # Rollback
    success = learning_engine.rollback(to_version=initial_version)
    
    assert success
    assert learning_engine.deployed_version == initial_version


def test_model_validation(learning_engine):
    """Test validating current model."""
    result = learning_engine.validate_current_model()
    
    assert isinstance(result, ValidationResult)
    # Base model validates against itself - no improvement but also no degradation
    # Should be considered valid as a baseline
    assert not result.catastrophic_forgetting
    assert len(result.safety_violations) == 0


def test_distribution_drift_detection(learning_engine):
    """Test detecting distribution drift."""
    # Create signals with consistent errors
    historical_signals = [
        LearningSignal(
            signal_id=f"hist_{i}",
            domain="chess",
            input_context={},
            predicted_output="",
            actual_output="",
            error_magnitude=0.1
        )
        for i in range(60)
    ]
    
    # Add recent signals with much higher error
    for i in range(20):
        historical_signals.append(
            LearningSignal(
                signal_id=f"recent_{i}",
                domain="chess",
                input_context={},
                predicted_output="",
                actual_output="",
                error_magnitude=0.3  # 3x higher
            )
        )
    
    drift_report = learning_engine.detect_distribution_drift(
        domain="chess",
        recent_signals=historical_signals,
        window_size=20
    )
    
    assert drift_report["drift_detected"]
    assert drift_report["recent_error_rate"] > drift_report["historical_error_rate"]


def test_learning_curve_tracking(learning_engine):
    """Test tracking learning curve over time."""
    # Simulate multiple learning cycles
    for cycle in range(5):
        # Create improving performance
        candidate = ModelSnapshot(
            snapshot_id=f"cycle_{cycle}",
            version=f"v{cycle}",
            timestamp=datetime.now().timestamp(),
            parameters={},
            performance_metrics={"chess": 0.70 + cycle * 0.05},
            safety_verification=True
        )
        learning_engine.snapshots[candidate.snapshot_id] = candidate
        learning_engine._deploy_update(candidate)
    
    curve = learning_engine.get_learning_curve("chess")
    
    assert len(curve) == 5
    # Should show improvement
    assert curve[-1] > curve[0]


def test_convergence_detection_not_converged(learning_engine):
    """Test detecting when learning has not converged."""
    # Simulate steady improvement
    for cycle in range(5):
        candidate = ModelSnapshot(
            snapshot_id=f"cycle_{cycle}",
            version=f"v{cycle}",
            timestamp=datetime.now().timestamp(),
            parameters={},
            performance_metrics={"chess": 0.70 + cycle * 0.05},  # 5% improvement each
            safety_verification=True
        )
        learning_engine.snapshots[candidate.snapshot_id] = candidate
        learning_engine._deploy_update(candidate)
    
    convergence = learning_engine.check_convergence("chess", window=5)
    
    assert not convergence["converged"]
    assert convergence["recent_improvement_rate"] > 0.01


def test_convergence_detection_converged(learning_engine):
    """Test detecting when learning has converged."""
    # Simulate plateau
    for cycle in range(5):
        candidate = ModelSnapshot(
            snapshot_id=f"cycle_{cycle}",
            version=f"v{cycle}",
            timestamp=datetime.now().timestamp(),
            parameters={},
            performance_metrics={"chess": 0.90 + cycle * 0.001},  # Minimal improvement
            safety_verification=True
        )
        learning_engine.snapshots[candidate.snapshot_id] = candidate
        learning_engine._deploy_update(candidate)
    
    convergence = learning_engine.check_convergence("chess", window=5)
    
    assert convergence["converged"]
    assert convergence["recent_improvement_rate"] < 0.01


def test_statistics(learning_engine):
    """Test getting learning system statistics."""
    stats = learning_engine.get_statistics()
    
    assert "deployed_version" in stats
    assert "total_snapshots" in stats
    assert "streaming_buffer_size" in stats
    assert "batch_buffer_size" in stats
    assert "learning_events" in stats
    assert "forgetting_report" in stats
    assert "current_performance" in stats


# ===========================
# Benchmark Tests (Phase 4 Gates)
# ===========================

def test_benchmark_zero_shot_improvement(learning_engine):
    """
    Benchmark: System improves without manual intervention.
    Gate: >60% of learning attempts result in improvement
    """
    improvements = 0
    total_attempts = 20
    
    for attempt in range(total_attempts):
        initial_perf = learning_engine.snapshots[learning_engine.deployed_version].performance_metrics.get("chess", 0)
        
        # Collect signals showing errors
        for i in range(10):
            learning_engine.collect_learning_signal(
                domain="chess",
                input_context={"move": i},
                predicted="pred",
                actual="actual",
                error=0.15
            )
        
        final_perf = learning_engine.snapshots[learning_engine.deployed_version].performance_metrics.get("chess", 0)
        
        if final_perf > initial_perf:
            improvements += 1
    
    success_rate = improvements / total_attempts
    assert success_rate > 0.60, f"Zero-shot improvement rate {success_rate:.2%} below 60% threshold"


def test_benchmark_safe_rollback(learning_engine):
    """
    Benchmark: System can safely rollback bad updates.
    Gate: 100% of rollback attempts succeed
    """
    rollback_successes = 0
    total_rollbacks = 10
    
    for rollback in range(total_rollbacks):
        # Create a version
        version_before = learning_engine.deployed_version
        
        # Deploy a new version
        candidate = ModelSnapshot(
            snapshot_id=f"test_{rollback}",
            version=f"test_{rollback}",
            timestamp=datetime.now().timestamp(),
            parameters={},
            performance_metrics={"chess": 0.75},
            safety_verification=True
        )
        learning_engine.snapshots[candidate.snapshot_id] = candidate
        learning_engine._deploy_update(candidate)
        
        # Rollback
        success = learning_engine.rollback(to_version=version_before)
        
        if success and learning_engine.deployed_version == version_before:
            rollback_successes += 1
    
    success_rate = rollback_successes / total_rollbacks
    assert success_rate == 1.0, f"Rollback success rate {success_rate:.2%} below 100% threshold"


def test_benchmark_forgetting_prevention(learning_engine):
    """
    Benchmark: System prevents catastrophic forgetting.
    Gate: <10% of updates cause forgetting
    """
    forgetting_count = 0
    total_updates = 20
    
    for update in range(total_updates):
        # Collect signals for chess
        for i in range(10):
            learning_engine.collect_learning_signal(
                domain="chess",
                input_context={"move": i},
                predicted="pred",
                actual="actual",
                error=0.15
            )
        
        # Check if forgetting occurred in other domains
        report = learning_engine.forgetting_detector.get_forgetting_report()
        if len(report["forgetting_detected"]) > 0:
            forgetting_count += 1
    
    forgetting_rate = forgetting_count / total_updates
    assert forgetting_rate < 0.10, f"Forgetting rate {forgetting_rate:.2%} exceeds 10% threshold"


def test_benchmark_convergence_detection(learning_engine):
    """
    Benchmark: System detects when learning has converged.
    Gate: >80% accurate convergence detection
    """
    correct_detections = 0
    total_tests = 10
    
    # Test converged scenarios
    for test in range(total_tests // 2):
        # Create plateau (converged)
        for cycle in range(5):
            candidate = ModelSnapshot(
                snapshot_id=f"plateau_{test}_{cycle}",
                version=f"v{test}_{cycle}",
                timestamp=datetime.now().timestamp(),
                parameters={},
                performance_metrics={"test_domain": 0.90 + cycle * 0.001},
                safety_verification=True
            )
            learning_engine.snapshots[candidate.snapshot_id] = candidate
            learning_engine._deploy_update(candidate)
        
        result = learning_engine.check_convergence("test_domain")
        if result["converged"]:
            correct_detections += 1
    
    # Test non-converged scenarios
    for test in range(total_tests // 2):
        # Create improvement (not converged)
        for cycle in range(5):
            candidate = ModelSnapshot(
                snapshot_id=f"improving_{test}_{cycle}",
                version=f"v{test}_{cycle}",
                timestamp=datetime.now().timestamp(),
                parameters={},
                performance_metrics={"test_domain2": 0.70 + cycle * 0.05},
                safety_verification=True
            )
            learning_engine.snapshots[candidate.snapshot_id] = candidate
            learning_engine._deploy_update(candidate)
        
        result = learning_engine.check_convergence("test_domain2")
        if not result["converged"]:
            correct_detections += 1
    
    accuracy = correct_detections / total_tests
    assert accuracy > 0.80, f"Convergence detection accuracy {accuracy:.2%} below 80% threshold"


def test_benchmark_drift_detection(learning_engine):
    """
    Benchmark: System detects distribution drift.
    Gate: >75% accurate drift detection
    """
    correct_detections = 0
    total_tests = 10
    
    # Test with drift scenarios
    for test in range(total_tests // 2):
        # Create drift (error rate changes significantly)
        signals = []
        for i in range(60):
            signals.append(LearningSignal(
                signal_id=f"drift_hist_{test}_{i}",
                domain="test",
                input_context={},
                predicted_output="",
                actual_output="",
                error_magnitude=0.1
            ))
        for i in range(20):
            signals.append(LearningSignal(
                signal_id=f"drift_recent_{test}_{i}",
                domain="test",
                input_context={},
                predicted_output="",
                actual_output="",
                error_magnitude=0.3  # 3x higher
            ))
        
        result = learning_engine.detect_distribution_drift("test", signals)
        if result["drift_detected"]:
            correct_detections += 1
    
    # Test without drift scenarios
    for test in range(total_tests // 2):
        # No drift (consistent error rate)
        signals = []
        for i in range(80):
            signals.append(LearningSignal(
                signal_id=f"nodrift_{test}_{i}",
                domain="test",
                input_context={},
                predicted_output="",
                actual_output="",
                error_magnitude=0.1
            ))
        
        result = learning_engine.detect_distribution_drift("test", signals)
        if not result["drift_detected"]:
            correct_detections += 1
    
    accuracy = correct_detections / total_tests
    assert accuracy > 0.75, f"Drift detection accuracy {accuracy:.2%} below 75% threshold"
