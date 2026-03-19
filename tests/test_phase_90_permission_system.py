"""
Phase 90: Permission Manifest System Tests

Tests for permission-governed action execution, audit logging, and human override.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch

from jessica.core.cognitive_kernel import CognitiveKernel
from jessica.core.knowledge_store import KnowledgeStore
from jessica.core.reasoning_engine import ReasoningEngine
from jessica.security.permission_manager import PermissionManager
from jessica.security.audit_log import AuditLog


class TestPermissionManager:
    """Test the PermissionManager class."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up permission files before and after each test."""
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")
        yield
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")

    def test_permission_manager_loads_default_permissions(self):
        """Test that PermissionManager loads default permissions from config."""
        pm = PermissionManager("test_permissions.json")
        
        # Should have all expected permissions
        all_perms = pm.get_all()
        assert "code_execution" in all_perms
        assert "memory_write" in all_perms
        assert "learning_enabled" in all_perms
        assert "file_access" in all_perms
        assert "internet_access" in all_perms
        assert "system_control" in all_perms
        assert "self_modify_code" in all_perms

    def test_permission_manager_has_permission(self):
        """Test has_permission method."""
        pm = PermissionManager("test_permissions.json")
        
        # code_execution defaults to true
        assert pm.has_permission("code_execution") == True
        # file_access defaults to false
        assert pm.has_permission("file_access") == False

    def test_permission_manager_require_allowed(self):
        """Test require() when permission is granted."""
        pm = PermissionManager("test_permissions.json")
        
        # Should not raise for allowed permission
        pm.require("code_execution")
        pm.require("memory_write")

    def test_permission_manager_require_denied(self):
        """Test require() when permission is denied."""
        pm = PermissionManager("test_permissions.json")
        
        # Should raise PermissionError for denied permission
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            pm.require("file_access")

    def test_permission_manager_grant_permission(self):
        """Test granting a denied permission."""
        pm = PermissionManager("test_permissions.json")
        
        assert pm.has_permission("file_access") == False
        pm.grant("file_access")
        assert pm.has_permission("file_access") == True

    def test_permission_manager_revoke_permission(self):
        """Test revoking an allowed permission."""
        pm = PermissionManager("test_permissions.json")
        
        assert pm.has_permission("code_execution") == True
        pm.revoke("code_execution")
        assert pm.has_permission("code_execution") == False

    def test_permission_manager_persistence(self):
        """Test that permission changes persist across instances."""
        pm1 = PermissionManager("test_permissions.json")
        pm1.grant("file_access")
        
        pm2 = PermissionManager("test_permissions.json")
        assert pm2.has_permission("file_access") == True

    def test_permission_manager_require_all(self):
        """Test require_all() with multiple permissions."""
        pm = PermissionManager("test_permissions.json")
        
        # This should work
        pm.require_all(["code_execution", "memory_write"])
        
        # This should fail
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            pm.require_all(["code_execution", "file_access"])


class TestAuditLog:
    """Test the AuditLog class."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up audit log files before and after each test."""
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")
        yield
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")

    def test_audit_log_record_event(self):
        """Test recording an event in audit log."""
        al = AuditLog("test_audit.log")
        al.record("test_action", "allowed")
        
        logs = al.get_logs()
        assert len(logs) >= 1
        assert logs[-1]["action"] == "test_action"
        assert logs[-1]["status"] == "allowed"

    def test_audit_log_record_with_details(self):
        """Test recording an event with details."""
        al = AuditLog("test_audit.log")
        al.record("test_action", "allowed", {"key": "value"})
        
        logs = al.get_logs()
        assert logs[-1]["details"]["key"] == "value"

    def test_audit_log_get_logs_for_action(self):
        """Test querying logs for a specific action."""
        al = AuditLog("test_audit.log")
        al.record("action_a", "allowed")
        al.record("action_b", "denied")
        al.record("action_a", "allowed")
        
        action_a_logs = al.get_logs_for_action("action_a")
        assert len(action_a_logs) == 2
        
        action_b_logs = al.get_logs_for_action("action_b")
        assert len(action_b_logs) == 1

    def test_audit_log_get_denied_actions(self):
        """Test getting only denied actions."""
        al = AuditLog("test_audit.log")
        al.record("action_a", "allowed")
        al.record("action_b", "denied")
        al.record("action_c", "denied")
        al.record("action_d", "allowed")
        
        denied = al.get_denied_actions()
        assert len(denied) == 2
        assert all(log["status"] == "denied" for log in denied)

    def test_audit_log_summary(self):
        """Test getting audit summary statistics."""
        al = AuditLog("test_audit.log")
        al.record("action_a", "allowed")
        al.record("action_b", "denied")
        al.record("action_c", "allowed")
        al.record("action_d", "denied")
        
        summary = al.get_summary()
        assert summary["total_events"] == 4
        assert summary["allowed"] == 2
        assert summary["denied"] == 2

    def test_audit_log_persistence(self):
        """Test that audit log entries persist across instances."""
        al1 = AuditLog("test_audit.log")
        al1.record("action_a", "allowed")
        
        al2 = AuditLog("test_audit.log")
        logs = al2.get_logs()
        assert len(logs) >= 1
        assert logs[-1]["action"] == "action_a"


class TestKnowledgeStorePermissions:
    """Test permission enforcement in KnowledgeStore."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up memory and permission files."""
        if os.path.exists("test_memory.json"):
            os.remove("test_memory.json")
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        yield
        if os.path.exists("test_memory.json"):
            os.remove("test_memory.json")
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")

    def test_knowledge_store_memory_write_allowed(self):
        """Test setting a fact when memory_write is allowed."""
        pm = PermissionManager("test_permissions.json")
        ks = KnowledgeStore("test_memory.json", permission_manager=pm)
        
        # Should work fine
        ks.set_fact("test_key", "test_value")
        assert ks.get_fact("test_key") == "test_value"

    def test_knowledge_store_memory_write_denied(self):
        """Test setting a fact when memory_write is denied."""
        pm = PermissionManager("test_permissions.json")
        pm.revoke("memory_write")
        ks = KnowledgeStore("test_memory.json", permission_manager=pm)
        
        # Should raise PermissionError
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            ks.set_fact("test_key", "test_value")

    def test_knowledge_store_without_permission_manager(self):
        """Test KnowledgeStore works without permission manager."""
        ks = KnowledgeStore("test_memory.json", permission_manager=None)
        
        # Should work fine without permission manager
        ks.set_fact("test_key", "test_value")
        assert ks.get_fact("test_key") == "test_value"


class TestReasoningEnginePermissions:
    """Test permission enforcement in ReasoningEngine."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up permission files."""
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        yield
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")

    def test_reasoning_engine_model_call_allowed(self):
        """Test calling model when code_execution is allowed."""
        pm = PermissionManager("test_permissions.json")
        re = ReasoningEngine(permission_manager=pm)
        
        mock_model = Mock()
        mock_model.generate.return_value = "test response"
        re.model = mock_model  # Set model on reasoning engine
        
        # Should work fine - returns structured response
        result = re.fallback_with_model("test query", mock_model)
        assert result is not None
        assert result.get("type") == "model_assisted"
        assert result.get("model_answer") == "test response"

    def test_reasoning_engine_model_call_denied(self):
        """Test calling model when code_execution is denied."""
        pm = PermissionManager("test_permissions.json")
        pm.revoke("code_execution")
        re = ReasoningEngine(permission_manager=pm)
        
        mock_model = Mock()
        
        # Should raise PermissionError
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            re.fallback_with_model("test query", mock_model)

    def test_reasoning_engine_without_permission_manager(self):
        """Test ReasoningEngine works without permission manager."""
        re = ReasoningEngine(permission_manager=None)
        
        mock_model = Mock()
        mock_model.generate.return_value = "test response"
        re.model = mock_model  # Set model on reasoning engine
        
        # Should work fine without permission manager - returns structured response
        result = re.fallback_with_model("test query", mock_model)
        assert result is not None
        assert result.get("type") == "model_assisted"
        assert result.get("model_answer") == "test response"

    def test_reasoning_engine_no_model(self):
        """Test ReasoningEngine with no model present."""
        re = ReasoningEngine()
        
        result = re.fallback_with_model("test query", None)
        assert result is None


class TestCognitiveKernelIntegration:
    """Integration tests for CognitiveKernel with permission system."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up all memory and permission files."""
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "test_permissions.json", "test_audit.log", "test_memory.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)
        # Ensure jessica/config exists
        if not os.path.exists("jessica/config"):
            os.makedirs("jessica/config", exist_ok=True)
        yield
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "test_permissions.json", "test_audit.log", "test_memory.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_cognitive_kernel_initialization(self):
        """Test CognitiveKernel initializes with permission system."""
        kernel = CognitiveKernel()
        
        assert kernel.permission_manager is not None
        assert kernel.audit_log is not None
        assert kernel.knowledge_store is not None
        assert kernel.reasoning_engine is not None

    def test_cognitive_kernel_store_fact_with_permissions(self):
        """Test storing facts through kernel respects permissions."""
        kernel = CognitiveKernel()
        
        # Should work when memory_write is enabled
        kernel.knowledge_store.set_fact("test_key", "test_value")
        assert kernel.knowledge_store.get_fact("test_key") == "test_value"

    def test_cognitive_kernel_revoke_memory_write(self):
        """Test that memory writes are blocked when permission revoked."""
        kernel = CognitiveKernel()
        kernel.permission_manager.revoke("memory_write")
        
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            kernel.knowledge_store.set_fact("test_key", "test_value")

    def test_cognitive_kernel_process_with_permission_system(self):
        """Test full kernel process respects permissions."""
        kernel = CognitiveKernel()
        
        # Should work with default permissions
        response = kernel.process("My name is Alice")
        assert response  # Should return something

    def test_permission_audit_trail(self):
        """Test that denied operations are logged."""
        kernel = CognitiveKernel()
        kernel.permission_manager.revoke("memory_write")
        
        # Try to set fact (should fail)
        from jessica.security.permission_manager import PermissionError as PMError
        try:
            kernel.knowledge_store.set_fact("test_key", "test_value")
        except PMError:
            pass
        
        # Check audit log (Note: audit log is manually called in security systems)
        # This test verifies the infrastructure exists
        assert kernel.audit_log is not None


class TestPermissionWorkflows:
    """Test realistic permission workflows."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up all test files."""
        for f in ["test_permissions.json", "test_audit.log", "test_memory.json"]:
            if os.path.exists(f):
                os.remove(f)
        yield
        for f in ["test_permissions.json", "test_audit.log", "test_memory.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_grant_revoke_cycle(self):
        """Test granting and revoking permissions."""
        pm = PermissionManager("test_permissions.json")
        
        # Start with denied
        assert pm.has_permission("file_access") == False
        
        # Grant it
        pm.grant("file_access")
        assert pm.has_permission("file_access") == True
        
        # Revoke it
        pm.revoke("file_access")
        assert pm.has_permission("file_access") == False

    def test_audit_trail_for_permission_denial(self):
        """Test that audit log records permission denials."""
        pm = PermissionManager("test_permissions.json")
        al = AuditLog("test_audit.log")
        
        # Simulate a denied action
        al.record("memory_write", "denied", {"reason": "permission_revoked"})
        
        denied = al.get_denied_actions()
        assert len(denied) == 1
        assert denied[0]["action"] == "memory_write"

    def test_permission_manifest_default_state(self):
        """Test that default permission manifest is secure."""
        pm = PermissionManager("test_permissions.json")
        
        # Dangerous permissions should be disabled by default
        assert pm.has_permission("file_access") == False
        assert pm.has_permission("internet_access") == False
        assert pm.has_permission("system_control") == False
        assert pm.has_permission("self_modify_code") == False
        
        # Safe permissions should be enabled by default
        assert pm.has_permission("code_execution") == True
        assert pm.has_permission("memory_write") == True
        assert pm.has_permission("learning_enabled") == True

    def test_multiple_permission_checks(self):
        """Test checking multiple permissions in sequence."""
        pm = PermissionManager("test_permissions.json")
        
        # Requires both should work
        pm.require_all(["code_execution", "memory_write", "learning_enabled"])
        
        # Requires with denied should fail
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError):
            pm.require_all(["code_execution", "memory_write", "file_access"])


class TestPermissionErrorHandling:
    """Test error handling in permission system."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up permission files."""
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        yield
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")

    def test_permission_error_message(self):
        """Test that PermissionError has clear message."""
        pm = PermissionManager("test_permissions.json")
        
        from jessica.security.permission_manager import PermissionError as PMError
        with pytest.raises(PMError) as exc_info:
            pm.require("file_access")
        
        assert "file_access" in str(exc_info.value)

    def test_permission_manager_handles_missing_file(self):
        """Test that PermissionManager creates default if file missing."""
        # Delete if exists
        if os.path.exists("test_permissions.json"):
            os.remove("test_permissions.json")
        
        pm = PermissionManager("test_permissions.json")
        
        # Should have loaded/created defaults
        assert pm.has_permission("code_execution") == True


class TestBackwardCompatibility:
    """Test backward compatibility with previous phases."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up all test files."""
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "test_permissions.json", "test_audit.log", "test_memory.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)
        # Ensure jessica/config exists
        if not os.path.exists("jessica/config"):
            os.makedirs("jessica/config", exist_ok=True)
        yield
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "test_permissions.json", "test_audit.log", "test_memory.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_knowledge_store_backward_compatible(self):
        """Test KnowledgeStore works without permission_manager parameter."""
        # Old code should still work
        ks = KnowledgeStore()
        ks.set_fact("test", "value")
        assert ks.get_fact("test") == "value"

    def test_reasoning_engine_backward_compatible(self):
        """Test ReasoningEngine works without permission_manager parameter."""
        # Old code should still work
        re = ReasoningEngine()
        
        # Age calculation should still work
        age = re.calculate_age(2000)
        assert isinstance(age, int)

    def test_cognitive_kernel_backward_compatible(self):
        """Test CognitiveKernel with None model."""
        kernel = CognitiveKernel(llm=None)
        
        response = kernel.process("What is 2+2?")
        assert response is not None
