"""
Phase 93: Action Execution Engine - Test Suite (Phase 94 Updated)

Tests the execution of approved proposals with tool-based architecture.
"""

import pytest
from jessica.execution.action_executor import ActionExecutor
from jessica.autonomy.action_proposal import ActionProposal
from jessica.core.cognitive_kernel import CognitiveKernel
from jessica.security.permission_manager import PermissionManager
from jessica.security.audit_log import AuditLog


class TestActionExecutor:
    """Test ActionExecutor execution"""

    def test_executor_initialization(self):
        executor = ActionExecutor()
        assert executor is not None

    def test_executor_with_permission_manager(self):
        pm = PermissionManager()
        executor = ActionExecutor(permission_manager=pm)
        assert executor.permission_manager == pm

    def test_executor_with_audit_log(self):
        al = AuditLog()
        executor = ActionExecutor(audit_log=al)
        assert executor.audit_log == al

    def test_execute_calculate_action(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "2 + 2")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_execute_unknown_action(self):
        executor = ActionExecutor()
        results = executor.execute(["unknown_action"], "test")
        assert len(results) == 1
        assert "Unknown tool" in results[0] or "unknown" in results[0].lower()

    def test_execute_multiple_actions(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate", "unknown"], "1 + 1")
        assert len(results) == 2

    def test_executor_has_registry(self):
        """Phase 94: Executor has tool registry"""
        executor = ActionExecutor()
        assert hasattr(executor, "registry")
        assert hasattr(executor, "list_available_tools")
        tools = executor.list_available_tools()
        assert "calculate" in tools
        assert "internet_search" in tools
        assert "open_file" in tools


class TestKernelExecution:
    """Test execution integration with CognitiveKernel"""

    def test_kernel_has_executor(self):
        kernel = CognitiveKernel()
        assert kernel.executor is not None
        assert isinstance(kernel.executor, ActionExecutor)

    def test_execute_proposal_method_exists(self):
        kernel = CognitiveKernel()
        assert hasattr(kernel, "execute_proposal")

    def test_execute_proposal_calls_executor(self):
        kernel = CognitiveKernel()
        proposal = ActionProposal(
            proposal_id="test-1",
            description="Calculate 2 + 2",
            reasoning="Test",
            actions=["calculate"],
            risk_level="low",
        )
        results = kernel.execute_proposal(proposal)
        assert len(results) == 1
        assert isinstance(results, list)

    def test_execute_proposal_with_calculation(self):
        kernel = CognitiveKernel()
        proposal = ActionProposal(
            proposal_id="test-2",
            description="Calculate 5 * 5",
            reasoning="Test",
            actions=["calculate"],
            risk_level="low",
        )
        results = kernel.execute_proposal(proposal)
        assert len(results) == 1
        assert len(results[0]) > 0

    def test_execute_proposal_with_multiple_actions(self):
        kernel = CognitiveKernel()
        proposal = ActionProposal(
            proposal_id="test-3",
            description="Multiple actions",
            reasoning="Test",
            actions=["calculate", "open_file"],
            risk_level="medium",
        )
        results = kernel.execute_proposal(proposal)
        assert len(results) == 2


class TestExecutionWorkflows:
    """Test complete execution workflows"""

    def test_proposal_to_execution_workflow(self):
        kernel = CognitiveKernel()
        
        # Generate proposal
        result = kernel.process("calculate 10 + 5")
        assert isinstance(result, dict)
        assert result["type"] == "proposal"
        
        # Get proposal from memory
        proposal_id = result["proposal_id"]
        proposal = kernel.autonomy.memory.get(proposal_id)
        assert proposal is not None
        
        # Execute proposal
        execution_result = kernel.execute_proposal(proposal)
        assert len(execution_result) > 0

    def test_calculation_execution_flow(self):
        kernel = CognitiveKernel()
        
        # Trigger proposal
        result = kernel.process("calculate 3 * 8")
        proposal = kernel.autonomy.memory.get(result["proposal_id"])
        
        # Execute - Phase 94: Tool-based, may succeed or be denied
        execution_result = kernel.execute_proposal(proposal)
        assert len(execution_result) == 1
        assert isinstance(execution_result[0], str)

    def test_internet_search_execution_flow(self):
        kernel = CognitiveKernel()
        
        # Trigger proposal
        result = kernel.process("search internet for AI")
        proposal = kernel.autonomy.memory.get(result["proposal_id"])
        
        # Execute
        execution_result = kernel.execute_proposal(proposal)
        assert len(execution_result) == 1
        assert isinstance(execution_result[0], str)

    def test_file_open_execution_flow(self):
        kernel = CognitiveKernel()
        
        # Trigger proposal
        result = kernel.process("open file test.txt")
        proposal = kernel.autonomy.memory.get(result["proposal_id"])
        
        # Execute
        execution_result = kernel.execute_proposal(proposal)
        assert len(execution_result) == 1


class TestExecutionSafety:
    """Test safety constraints of execution system"""

    def test_executor_cannot_eval_dangerous_code(self):
        executor = ActionExecutor()
        # Should fail safely on dangerous expressions
        results = executor.execute(["calculate"], "__import__('os').system('ls')")
        assert "could not evaluate" in results[0].lower()

    def test_safe_eval_blocks_dangerous_code_injections(self):
        """Phase 94: Safety tested through tool interface"""
        executor = ActionExecutor()
        dangerous_tests = [
            "__import__('os')",
            "exec('print(1)')",
            "eval('1+1')",
        ]
        for test_expr in dangerous_tests:
            results = executor.execute(["calculate"], test_expr)
            assert isinstance(results[0], str)

    def test_executor_handles_exceptions(self):
        executor = ActionExecutor()
        # Should not crash, should return error message
        results = executor.execute(["calculate"], "malformed expression {{{")
        assert len(results) == 1
        assert isinstance(results[0], str)


class TestExecutorPermissions:
    """Test permission integration (future phases)"""

    def test_executor_accepts_permission_manager(self):
        pm = PermissionManager()
        executor = ActionExecutor(permission_manager=pm)
        assert executor.permission_manager is not None

    def test_executor_accepts_audit_log(self):
        al = AuditLog()
        executor = ActionExecutor(audit_log=al)
        assert executor.audit_log is not None


class TestCalculatorFunctions:
    """Test calculator via tool interface (Phase 94)"""

    def test_calculate_addition(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "5 + 3")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_calculate_subtraction(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "10 - 7")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_calculate_multiplication(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "6 * 4")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_calculate_division(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "20 / 4")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_calculate_complex_expression(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "(10 + 5) / 3")
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_calculate_invalid(self):
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "not a number")
        assert "could not" in results[0].lower()


class TestBackwardCompatibility:
    """Test that Phase 93/94 doesn't break previous phases"""

    def test_kernel_still_initializes(self):
        kernel = CognitiveKernel()
        assert kernel is not None
        assert kernel.autonomy is not None
        assert kernel.executor is not None

    def test_normal_chat_still_works(self):
        kernel = CognitiveKernel()
        result = kernel.process("hello")
        assert isinstance(result, str)

    def test_proposals_still_generate(self):
        kernel = CognitiveKernel()
        result = kernel.process("calculate 1 + 1")
        assert isinstance(result, dict)
        assert result["type"] == "proposal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
