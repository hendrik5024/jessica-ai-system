"""
Phase 94: Tool Registry

Central registry for managing all available tools.
"""


class ToolRegistry:
    """
    Registers and provides tools dynamically.
    
    Allows Jessica to:
    - Discover available tools
    - Retrieve tools by name
    - List all capabilities
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self.tools = {}

    def register(self, tool):
        """
        Register a tool in the registry.
        
        Args:
            tool: Instance of BaseTool subclass
        """
        self.tools[tool.name] = tool

    def get(self, name):
        """
        Get a tool by name.
        
        Args:
            name: Tool name (e.g., 'calculate', 'internet_search')
            
        Returns:
            BaseTool instance or None if not found
        """
        return self.tools.get(name)

    def list_tools(self):
        """
        List all registered tool names.
        
        Returns:
            List of tool name strings
        """
        return list(self.tools.keys())

    def get_tool_info(self):
        """
        Get information about all registered tools.
        
        Returns:
            Dict mapping tool names to their descriptions
        """
        return {
            name: {
                "description": tool.description,
                "risk": tool.risk
            }
            for name, tool in self.tools.items()
        }
