"""
Phase 4 Production Infrastructure Tests

Tests for configuration management, tracing, and safety systems.
"""

import pytest
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime

from jessica.production.config_manager import (
    ProductionConfig,
    ConfigurationManager,
    SafetyConfig,
    ObservabilityConfig,
    PerformanceConfig,
    OperatorConfig,
    DeploymentMode,
    OperatorVersion,
)

from jessica.production.operator_tracer import (
    OperatorTracer,
    OperatorTrace,
    OperatorChainTrace,
    OperatorType,
    OperatorStatus,
)

from jessica.production.safety_guard import (
    SafetyGuard,
    SafetyViolationType,
    RollbackTrigger,
)


# ============================================================================
# CONFIGURATION MANAGER TESTS
# ============================================================================

class TestConfigurationManager:
    """Test configuration management system."""
    
    def test_default_production_config(self):
        """Test default production configuration."""
        config = ProductionConfig(mode="production")
        is_valid, errors = config.validate()
        
        assert is_valid, f"Config validation failed: {errors}"
        assert config.mode == "production"
        assert config.safety.enabled is True
        assert config.operators.frozen_version == OperatorVersion.PHASE_3_5.value
    
    def test_config_validation_phase_4_constraints(self):
        """Test Phase 4 specific constraints."""
        # Should fail if operator modification is allowed
        config = ProductionConfig(
            operators=OperatorConfig(allow_runtime_modification=True)
        )
        is_valid, errors = config.validate()
        
        assert not is_valid
        assert any("allow_runtime_modification MUST be False" in e for e in errors)
    
    def test_config_validation_safety_limits(self):
        """Test safety configuration validation."""
        # Invalid timeout (too low)
        config = ProductionConfig(
            safety=SafetyConfig(operator_timeout_ms=500)
        )
        is_valid, errors = config.validate()
        assert not is_valid
        
        # Valid timeout
        config = ProductionConfig(
            safety=SafetyConfig(operator_timeout_ms=30000)
        )
        is_valid, errors = config.validate()
        assert is_valid
    
    def test_config_yaml_roundtrip(self):
        """Test YAML save and load roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create and save config
            config = ProductionConfig(
                deployment_id="test_deploy_1",
                safety=SafetyConfig(operator_timeout_ms=60000),
            )
            success, msg = config.to_yaml(str(config_path))
            assert success
            
            # Load config
            loaded_config, errors = ProductionConfig.from_yaml(str(config_path))
            assert loaded_config is not None
            assert len(errors) == 0
            assert loaded_config.deployment_id == "test_deploy_1"
            assert loaded_config.safety.operator_timeout_ms == 60000
    
    def test_configuration_manager_initialization(self):
        """Test ConfigurationManager initialization."""
        manager = ConfigurationManager()
        success = manager.load_configuration(DeploymentMode.PRODUCTION)
        
        assert success
        assert manager._is_initialized
        assert manager.is_production_mode()
        assert not manager.is_test_mode()
    
    def test_configuration_manager_separate_modes(self):
        """Test separate test and production modes."""
        # Production mode
        manager_prod = ConfigurationManager()
        assert manager_prod.load_configuration(DeploymentMode.PRODUCTION)
        assert manager_prod.is_production_mode()
        
        # Test mode (should be different)
        manager_test = ConfigurationManager()
        assert manager_test.load_configuration(DeploymentMode.TEST)
        assert manager_test.is_test_mode()
    
    def test_config_manager_subsystem_access(self):
        """Test accessing sub-configurations."""
        manager = ConfigurationManager()
        assert manager.load_configuration()
        
        safety_cfg = manager.get_safety_config()
        assert isinstance(safety_cfg, SafetyConfig)
        
        obs_cfg = manager.get_observability_config()
        assert isinstance(obs_cfg, ObservabilityConfig)
        
        perf_cfg = manager.get_performance_config()
        assert isinstance(perf_cfg, PerformanceConfig)
        
        op_cfg = manager.get_operator_config()
        assert isinstance(op_cfg, OperatorConfig)


# ============================================================================
# OPERATOR TRACER TESTS
# ============================================================================

class TestOperatorTracer:
    """Test operator tracing system."""
    
    def test_operator_trace_creation(self):
        """Test creating operator trace."""
        tracer = OperatorTracer()
        
        trace = tracer.start_operator_trace(
            OperatorType.DETECT_BOTTLENECK,
            "detect_bottleneck_refined",
            {"input": "test"},
            chain_id="chain_001",
        )
        
        assert trace is not None
        assert trace.operator_type == OperatorType.DETECT_BOTTLENECK.value
        assert trace.status == OperatorStatus.INITIATED.value
    
    def test_operator_trace_completion(self):
        """Test completing operator trace."""
        tracer = OperatorTracer()
        
        trace = tracer.start_operator_trace(
            OperatorType.CONSTRAIN,
            "constrain_op",
            {"constraints": []},
            chain_id="chain_001",
        )
        
        result = {"constrained": True}
        tracer.end_operator_trace(trace, OperatorStatus.SUCCESS, result)
        
        assert trace.status == OperatorStatus.SUCCESS.value
        assert trace.duration_ms is not None
        assert trace.duration_ms > 0
        assert trace.output_result == result
    
    def test_operator_trace_error_handling(self):
        """Test error handling in traces."""
        tracer = OperatorTracer()
        
        trace = tracer.start_operator_trace(
            OperatorType.ADAPT,
            "adapt_op",
            {},
            chain_id="chain_001",
        )
        
        error = ValueError("Test error")
        tracer.end_operator_trace(trace, OperatorStatus.FAILURE, error=error)
        
        assert trace.status == OperatorStatus.FAILURE.value
        assert trace.error_type == "ValueError"
        assert trace.error_message == "Test error"
    
    def test_operator_chain_trace(self):
        """Test tracing complete operator chain."""
        tracer = OperatorTracer()
        
        chain = tracer.start_chain_trace("chain_001", "user query")
        assert chain is not None
        
        # Add operator traces
        for i, op_type in enumerate([
            OperatorType.SEQUENCE,
            OperatorType.DETECT_BOTTLENECK,
            OperatorType.ADAPT,
        ]):
            trace = tracer.start_operator_trace(
                op_type,
                op_type.value.lower(),
                {},
                chain_id="chain_001",
                depth=i,
            )
            tracer.end_operator_trace(trace, OperatorStatus.SUCCESS)
            tracer.add_operator_to_chain(chain, trace)
        
        tracer.end_chain_trace(chain, OperatorStatus.SUCCESS)
        
        assert chain.status == OperatorStatus.SUCCESS.value
        assert chain.total_operators == 3
        assert chain.successful_operators == 3
        assert chain.failed_operators == 0
    
    def test_operator_statistics(self):
        """Test operator statistics collection."""
        tracer = OperatorTracer()
        
        # Create multiple traces for same operator
        for i in range(5):
            trace = tracer.start_operator_trace(
                OperatorType.DETECT_BOTTLENECK,
                "detect_bottleneck_refined",
                {},
                chain_id=f"chain_{i:03d}",
            )
            tracer.end_operator_trace(trace, OperatorStatus.SUCCESS)
        
        stats = tracer.get_operator_stats("detect_bottleneck_refined")
        assert stats['invocations'] == 5
        assert stats['successes'] == 5
        assert stats['failures'] == 0
        assert stats['avg_duration_ms'] > 0
    
    def test_trace_export_json(self):
        """Test exporting traces to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracer = OperatorTracer()
            
            # Create some traces
            trace = tracer.start_operator_trace(
                OperatorType.SEQUENCE,
                "sequence_op",
                {},
                chain_id="chain_001",
            )
            tracer.end_operator_trace(trace, OperatorStatus.SUCCESS)
            
            # Export
            export_path = Path(tmpdir) / "traces.json"
            success, msg = tracer.export_traces_json(str(export_path))
            
            assert success
            assert export_path.exists()
            
            # Verify content
            with open(export_path, 'r') as f:
                data = json.load(f)
            assert 'traces_count' in data
            assert data['traces_count'] == 1
    
    def test_trace_retrieval(self):
        """Test retrieving traces."""
        tracer = OperatorTracer()
        
        # Create traces
        for i in range(3):
            trace = tracer.start_operator_trace(
                OperatorType.ADAPT,
                "adapt_op",
                {},
                chain_id=f"chain_{i:03d}",
            )
            tracer.end_operator_trace(trace, OperatorStatus.SUCCESS)
        
        # Retrieve
        traces = tracer.get_recent_traces(limit=2)
        assert len(traces) == 2
    
    def test_tracer_collection_pause_resume(self):
        """Test pausing and resuming collection."""
        tracer = OperatorTracer()
        
        # Collect one trace
        trace = tracer.start_operator_trace(
            OperatorType.HANDLE,
            "handle_op",
            {},
        )
        tracer.end_operator_trace(trace, OperatorStatus.SUCCESS)
        
        # Pause and try to collect (should return None)
        tracer.pause_collection()
        trace2 = tracer.start_operator_trace(
            OperatorType.HANDLE,
            "handle_op",
            {},
        )
        assert trace2 is None
        
        # Resume
        tracer.resume_collection()
        trace3 = tracer.start_operator_trace(
            OperatorType.HANDLE,
            "handle_op",
            {},
        )
        assert trace3 is not None


# ============================================================================
# SAFETY GUARD TESTS
# ============================================================================

class TestSafetyGuard:
    """Test safety guard system."""
    
    def test_safety_guard_initialization(self):
        """Test SafetyGuard initialization."""
        guard = SafetyGuard(
            memory_limit_mb=500,
            timeout_sec=30,
        )
        
        assert guard.is_enabled()
        status = guard.get_safety_status()
        assert status['enabled'] is True
    
    def test_operator_invariant_registration(self):
        """Test registering operator invariants."""
        guard = SafetyGuard()
        
        # Register invariant: output must have 'result' key
        guard.register_operator_invariant(
            "test_op",
            lambda output: "result" in output,
        )
        
        # Valid output
        is_valid, errors = guard.validate_operator_output(
            "test_op",
            {"result": "value"},
        )
        assert is_valid
        assert len(errors) == 0
        
        # Invalid output
        is_valid, errors = guard.validate_operator_output(
            "test_op",
            {"other": "value"},
        )
        assert not is_valid
        assert len(errors) > 0
    
    def test_resource_constraints_memory(self):
        """Test memory constraint checking."""
        guard = SafetyGuard(memory_limit_mb=1)  # Very low limit
        
        # Current memory usage will exceed this
        is_ok, msg = guard.check_resource_constraints(time.time())
        
        # Should report memory exceeded
        assert not is_ok
        assert "Memory" in msg or "memory" in msg.lower()
    
    def test_resource_constraints_timeout(self):
        """Test timeout constraint checking."""
        import time
        guard = SafetyGuard(timeout_sec=1)  # 1 second timeout
        
        start_time = time.time() - 2  # Started 2 seconds ago
        is_ok, msg = guard.check_resource_constraints(start_time)
        
        assert not is_ok
        assert "Timeout" in msg or "timeout" in msg.lower()
    
    def test_safety_violations_recording(self):
        """Test recording safety violations."""
        guard = SafetyGuard()
        
        guard.handle_violation(
            SafetyViolationType.INVALID_OUTPUT,
            "test_op",
            "Output missing required field",
        )
        
        violations = guard.get_violations()
        assert len(violations) > 0
        assert violations[-1].operator_name == "test_op"
    
    def test_safety_guard_enable_disable(self):
        """Test enabling/disabling safety guard."""
        guard = SafetyGuard()
        
        assert guard.is_enabled()
        guard.disable()
        assert not guard.is_enabled()
        
        guard.enable()
        assert guard.is_enabled()
    
    def test_safety_status_reporting(self):
        """Test safety status reporting."""
        guard = SafetyGuard()
        
        # Record some violations
        guard.handle_violation(
            SafetyViolationType.INVALID_OUTPUT,
            "op1",
            "Test violation",
        )
        
        status = guard.get_safety_status()
        
        assert 'enabled' in status
        assert 'total_violations' in status
        assert 'memory_usage_mb' in status
        assert 'rollback_status' in status
        assert status['total_violations'] >= 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase4Integration:
    """Integration tests for Phase 4 production systems."""
    
    def test_config_and_tracer_integration(self):
        """Test configuration and tracer work together."""
        manager = ConfigurationManager()
        assert manager.load_configuration(DeploymentMode.PRODUCTION)
        
        obs_cfg = manager.get_observability_config()
        tracer = OperatorTracer(buffer_size=obs_cfg.trace_buffer_size)
        
        # Tracer should use config size
        assert tracer.buffer_size == obs_cfg.trace_buffer_size
    
    def test_safety_and_tracer_integration(self):
        """Test safety guard and tracer work together."""
        guard = SafetyGuard()
        tracer = OperatorTracer()
        
        # Create operator trace
        trace = tracer.start_operator_trace(
            OperatorType.DETECT_BOTTLENECK,
            "detect_bottleneck_refined",
            {},
            chain_id="chain_001",
        )
        
        # Validate output
        output = {"bottleneck": "component_1"}
        is_valid, errors = guard.validate_operator_output(
            "detect_bottleneck_refined",
            output,
        )
        
        tracer.end_operator_trace(trace, OperatorStatus.SUCCESS, output)
    
    def test_all_systems_together(self):
        """Test all production systems in concert."""
        # Initialize all systems
        config_mgr = ConfigurationManager()
        assert config_mgr.load_configuration(DeploymentMode.PRODUCTION)
        
        tracer = OperatorTracer()
        guard = SafetyGuard()
        
        # Simulate operator chain
        chain = tracer.start_chain_trace("chain_001", "test query")
        
        for op_type in [OperatorType.SEQUENCE, OperatorType.DETECT_BOTTLENECK]:
            trace = tracer.start_operator_trace(
                op_type,
                op_type.value.lower(),
                {},
                chain_id="chain_001",
            )
            
            # Simulate some work
            import time
            time.sleep(0.001)
            
            # Validate constraints
            is_ok, msg = guard.check_resource_constraints(trace.start_time)
            
            output = {"status": "ok"}
            tracer.end_operator_trace(trace, OperatorStatus.SUCCESS, output)
            tracer.add_operator_to_chain(chain, trace)
        
        tracer.end_chain_trace(chain, OperatorStatus.SUCCESS)
        
        # Verify everything collected correctly
        status = guard.get_safety_status()
        assert 'enabled' in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
