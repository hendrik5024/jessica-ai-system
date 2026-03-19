"""Phase 94 action executor compatibility surface."""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

from jessica.execution.keyboard_mouse_executor import ActionExecutor as _EmbodiedActionExecutor
from jessica.tools.analysis.calculator_tool import CalculatorTool
from jessica.tools.data.file_tool import FileTool
from jessica.tools.data.internet_tool import InternetTool
from jessica.tools.tool_registry import ToolRegistry


class ActionExecutor(_EmbodiedActionExecutor):
  """Backward-compatible executor spanning Phase 5.2 and Phase 94 APIs."""

  def __init__(
    self,
    permission_manager: Optional[Any] = None,
    audit_log: Optional[Any] = None,
    enabled: bool = True,
  ):
    self.permission_manager = permission_manager
    self.audit_log = audit_log
    super().__init__(enabled=enabled)
    self.registry = ToolRegistry()
    self._register_default_tools()

  def _register_default_tools(self) -> None:
    self.registry.register(CalculatorTool())
    self.registry.register(InternetTool())
    self.registry.register(FileTool())

  def list_available_tools(self) -> List[str]:
    return self.registry.list_tools()

  def get_tool_info(self) -> dict:
    return self.registry.get_tool_info()

  def execute(self, actions: Iterable[str], user_input: str) -> List[str]:
    results: List[str] = []
    for action in actions:
      tool = self.registry.get(action)
      if tool is None:
        results.append(f"Unknown tool: {action}")
        continue
      try:
        outcome = tool.execute(user_input)
        results.append(str(outcome))
      except Exception as exc:
        results.append(f"Tool execution failed for {action}: {exc}")
    return results
