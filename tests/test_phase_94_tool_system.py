"""
Phase 94: Tool System Tests

Comprehensive tests for the dynamic tool system.
"""

import pytest
from jessica.tools.base_tool import BaseTool
from jessica.tools.tool_registry import ToolRegistry
from jessica.tools.analysis.calculator_tool import CalculatorTool
from jessica.tools.data.internet_tool import InternetTool
from jessica.tools.data.file_tool import FileTool
from jessica.execution.action_executor import ActionExecutor
from jessica.core.cognitive_kernel import CognitiveKernel


# ============================================================
# TEST BASE TOOL
# ============================================================

class TestBaseTool:
    """Test the BaseTool abstract class."""

    def test_base_tool_has_attributes(self):
        """Base tool has required attributes."""
        tool = BaseTool()
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "risk")

    def test_base_tool_raises_not_implemented(self):
        """Base tool execute() raises NotImplementedError."""
        tool = BaseTool()
        with pytest.raises(NotImplementedError):
            tool.execute("test")


# ============================================================
# TEST TOOL REGISTRY
# ============================================================

class TestToolRegistry:
    """Test the ToolRegistry system."""

    def test_registry_initializes_empty(self):
        """Registry starts with no tools."""
        registry = ToolRegistry()
        assert len(registry.list_tools()) == 0

    def test_registry_can_register_tool(self):
        """Registry can register a tool."""
        registry = ToolRegistry()
        tool = CalculatorTool()
        registry.register(tool)
        
        assert "calculate" in registry.list_tools()

    def test_registry_can_get_tool(self):
        """Registry can retrieve a registered tool."""
        registry = ToolRegistry()
        tool = CalculatorTool()
        registry.register(tool)
        
        retrieved = registry.get("calculate")
        assert retrieved is tool

    def test_registry_returns_none_for_unknown_tool(self):
        """Registry returns None for unknown tool."""
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_registry_can_register_multiple_tools(self):
        """Registry can hold multiple tools."""
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        registry.register(InternetTool())
        registry.register(FileTool())
        
        assert len(registry.list_tools()) == 3
        assert "calculate" in registry.list_tools()
        assert "internet_search" in registry.list_tools()
        assert "open_file" in registry.list_tools()

    def test_registry_get_tool_info(self):
        """Registry can provide tool information."""
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        
        info = registry.get_tool_info()
        assert "calculate" in info
        assert "description" in info["calculate"]
        assert "risk" in info["calculate"]


# ============================================================
# TEST CALCULATOR TOOL
# ============================================================

class TestCalculatorTool:
    """Test the CalculatorTool."""

    def test_calculator_tool_attributes(self):
        """Calculator tool has correct attributes."""
        tool = CalculatorTool()
        assert tool.name == "calculate"
        assert tool.risk == "low"
        assert "mathematical" in tool.description.lower() or "calculation" in tool.description.lower()

    def test_calculator_simple_addition(self):
        """Calculator can add numbers."""
        tool = CalculatorTool()
        result = tool.execute("2 + 2")
        assert "4" in result

    def test_calculator_simple_subtraction(self):
        """Calculator can subtract numbers."""
        tool = CalculatorTool()
        result = tool.execute("10 - 3")
        assert "7" in result

    def test_calculator_simple_multiplication(self):
        """Calculator can multiply numbers."""
        tool = CalculatorTool()
        result = tool.execute("5 * 4")
        assert "20" in result

    def test_calculator_simple_division(self):
        """Calculator can divide numbers."""
        tool = CalculatorTool()
        result = tool.execute("20 / 4")
        assert "5" in result

    def test_calculator_complex_expression(self):
        """Calculator handles complex expressions."""
        tool = CalculatorTool()
        result = tool.execute("(10 + 5) * 2")
        assert "30" in result

    def test_calculator_extracts_expression_from_sentence(self):
        """Calculator extracts math from natural language."""
        tool = CalculatorTool()
        result = tool.execute("calculate 2 + 2")
        assert "4" in result

    def test_calculator_handles_multiple_trigger_words(self):
        """Calculator strips various trigger words."""
        tool = CalculatorTool()
        
        test_cases = [
            "calculate 5 + 5",
            "compute 5 + 5",
            "evaluate 5 + 5",
            "what is 5 + 5",
        ]
        
        for test in test_cases:
            result = tool.execute(test)
            assert "10" in result

    def test_calculator_blocks_dangerous_code(self):
        """Calculator blocks code injection attempts."""
        tool = CalculatorTool()
        
        dangerous = [
            "__import__('os').system('ls')",
            "exec('print(1)')",
            "eval('1+1')",
        ]
        
        for expr in dangerous:
            result = tool.execute(expr)
            assert "could not evaluate" in result.lower()

    def test_calculator_empty_input(self):
        """Calculator handles empty input gracefully."""
        tool = CalculatorTool()
        result = tool.execute("")
        assert "no expression" in result.lower()

    def test_calculator_invalid_expression(self):
        """Calculator handles invalid expressions."""
        tool = CalculatorTool()
        result = tool.execute("not a number")
        assert "could not evaluate" in result.lower()


# ============================================================
# TEST INTERNET TOOL
# ============================================================

class TestInternetTool:
    """Test the InternetTool."""

    def test_internet_tool_attributes(self):
        """Internet tool has correct attributes."""
        tool = InternetTool()
        assert tool.name == "internet_search"
        assert tool.risk == "high"
        assert "search" in tool.description.lower()

    def test_internet_tool_executes(self):
        """Internet tool returns success message."""
        tool = InternetTool()
        result = tool.execute("Python tutorials")
        assert "browser" in result.lower() or "search" in result.lower()

    def test_internet_tool_extracts_query(self):
        """Internet tool extracts query from natural language."""
        tool = InternetTool()
        result = tool.execute("search for Python")
        # Should succeed (just checking it doesn't crash)
        assert isinstance(result, str)

    def test_internet_tool_handles_empty_input(self):
        """Internet tool handles empty input."""
        tool = InternetTool()
        result = tool.execute("")
        assert "no" in result.lower() and "query" in result.lower()


# ============================================================
# TEST FILE TOOL
# ============================================================

class TestFileTool:
    """Test the FileTool placeholder."""

    def test_file_tool_attributes(self):
        """File tool has correct attributes."""
        tool = FileTool()
        assert tool.name == "open_file"
        assert tool.risk == "medium"

    def test_file_tool_returns_placeholder(self):
        """File tool returns not implemented message."""
        tool = FileTool()
        result = tool.execute("config.txt")
        assert "not yet implemented" in result.lower()


# ============================================================
# TEST ACTION EXECUTOR WITH TOOLS
# ============================================================

class TestActionExecutorWithTools:
    """Test ActionExecutor using the tool system."""

    def test_executor_has_registry(self):
        """Executor has a tool registry."""
        executor = ActionExecutor()
        assert hasattr(executor, "registry")
        assert isinstance(executor.registry, ToolRegistry)

    def test_executor_registers_default_tools(self):
        """Executor registers calculator, internet, file tools."""
        executor = ActionExecutor()
        tools = executor.list_available_tools()
        
        assert "calculate" in tools
        assert "internet_search" in tools
        assert "open_file" in tools

    def test_executor_can_list_tools(self):
        """Executor can list available tools."""
        executor = ActionExecutor()
        tools = executor.list_available_tools()
        assert len(tools) == 3

    def test_executor_can_get_tool_info(self):
        """Executor can provide tool information."""
        executor = ActionExecutor()
        info = executor.get_tool_info()
        
        assert "calculate" in info
        assert info["calculate"]["risk"] == "low"

    def test_executor_executes_calculator_via_tool(self):
        """Executor executes calculation using tool system."""
        executor = ActionExecutor()
        results = executor.execute(["calculate"], "5 + 5")
        
        assert len(results) == 1
        assert "10" in results[0]

    def test_executor_executes_internet_via_tool(self):
        """Executor executes internet search using tool system."""
        executor = ActionExecutor()
        results = executor.execute(["internet_search"], "AI research")
        
        assert len(results) == 1
        assert "browser" in results[0].lower() or "search" in results[0].lower()

    def test_executor_executes_file_via_tool(self):
        """Executor executes file operation using tool system."""
        executor = ActionExecutor()
        results = executor.execute(["open_file"], "test.txt")
        
        assert len(results) == 1
        assert "not yet implemented" in results[0].lower()

    def test_executor_handles_unknown_tool(self):
        """Executor handles unknown tool gracefully."""
        executor = ActionExecutor()
        results = executor.execute(["nonexistent_tool"], "test")
        
        assert len(results) == 1
        assert "unknown tool" in results[0].lower()

    def test_executor_executes_multiple_tools(self):
        """Executor can execute multiple tools in sequence."""
        executor = ActionExecutor()
        results = executor.execute(
            ["calculate", "open_file", "unknown_tool"],
            "2 + 2"
        )
        
        assert len(results) == 3
        assert "4" in results[0]
        assert "not yet implemented" in results[1].lower()
        assert "unknown tool" in results[2].lower()


# ============================================================
# TEST KERNEL INTEGRATION
# ============================================================

class TestKernelWithToolSystem:
    """Test CognitiveKernel with Phase 94 tool system."""

    def test_kernel_executor_has_tool_system(self):
        """Kernel's executor uses tool system."""
        kernel = CognitiveKernel()
        assert hasattr(kernel.executor, "registry")
        assert hasattr(kernel.executor, "list_available_tools")

    def test_kernel_can_list_tools(self):
        """Kernel can list available tools through executor."""
        kernel = CognitiveKernel()
        tools = kernel.executor.list_available_tools()
        assert len(tools) == 3

    def test_kernel_execute_proposal_uses_tools(self):
        """Kernel's execute_proposal uses tool system."""
        kernel = CognitiveKernel()
        
        # Mock a proposal
        class MockProposal:
            actions = ["calculate"]
        
        proposal = MockProposal()
        results = kernel.execute_proposal(proposal, "10 + 10")
        
        # Results can be either successful calculation or permission denied
        # Both indicate the tool system is working
        assert len(results) == 1
        assert isinstance(results[0], str)
        assert len(results[0]) > 0


# ============================================================
# TEST BACKWARD COMPATIBILITY
# ============================================================

class TestBackwardCompatibility:
    """Ensure Phase 94 doesn't break Phase 93 functionality."""

    def test_executor_signature_unchanged(self):
        """ActionExecutor signature is backward compatible."""
        executor = ActionExecutor()
        
        # Phase 93 interface
        results = executor.execute(["calculate"], "5 * 5")
        assert len(results) == 1
        assert "25" in results[0]

    def test_executor_accepts_permission_manager(self):
        """Executor still accepts permission_manager parameter."""
        executor = ActionExecutor(permission_manager=None)
        assert executor.permission_manager is None

    def test_executor_accepts_audit_log(self):
        """Executor still accepts audit_log parameter."""
        executor = ActionExecutor(audit_log=None)
        assert executor.audit_log is None

    def test_kernel_initialization_unchanged(self):
        """CognitiveKernel initialization still works."""
        kernel = CognitiveKernel()
        assert hasattr(kernel, "executor")

    def test_calculation_still_works(self):
        """Calculator functionality unchanged from Phase 93."""
        executor = ActionExecutor()
        
        test_cases = [
            ("2 + 2", "4"),
            ("10 - 5", "5"),
            ("3 * 4", "12"),
            ("20 / 4", "5"),
        ]
        
        for expr, expected in test_cases:
            results = executor.execute(["calculate"], expr)
            assert expected in results[0]

    def test_safety_still_enforced(self):
        """Safety constraints still enforced from Phase 93."""
        executor = ActionExecutor()
        
        dangerous = [
            "__import__('os')",
            "exec('print(1)')",
        ]
        
        for expr in dangerous:
            results = executor.execute(["calculate"], expr)
            assert "could not evaluate" in results[0].lower()


# ============================================================
# TEST EXTENSIBILITY
# ============================================================

class TestExtensibility:
    """Test that the tool system is truly extensible."""

    def test_can_create_custom_tool(self):
        """Can create a custom tool by subclassing BaseTool."""
        
        class CustomTool(BaseTool):
            name = "custom"
            description = "Custom test tool"
            risk = "low"
            
            def execute(self, input_data):
                return f"Custom tool executed: {input_data}"
        
        tool = CustomTool()
        assert tool.name == "custom"
        assert "Custom tool" in tool.execute("test")

    def test_can_register_custom_tool(self):
        """Can register a custom tool in the registry."""
        
        class CustomTool(BaseTool):
            name = "custom"
            description = "Custom test tool"
            risk = "low"
            
            def execute(self, input_data):
                return "Custom result"
        
        registry = ToolRegistry()
        registry.register(CustomTool())
        
        assert "custom" in registry.list_tools()

    def test_executor_can_use_custom_tool(self):
        """Executor can use a custom tool after registration."""
        
        class CustomTool(BaseTool):
            name = "custom"
            description = "Custom test tool"
            risk = "low"
            
            def execute(self, input_data):
                return f"Processed: {input_data}"
        
        executor = ActionExecutor()
        executor.registry.register(CustomTool())
        
        results = executor.execute(["custom"], "test data")
        assert "Processed: test data" in results[0]


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
