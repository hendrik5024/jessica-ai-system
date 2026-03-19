"""
Phase 94: Base Tool

Abstract base class for all tools in the tool system.
"""


class BaseTool:
    """
    Base class for all tools.
    
    All tools must define:
    - name: Unique identifier for the tool
    - description: What the tool does
    - risk: Risk level (low/medium/high)
    - execute(input_data): Execute the tool's functionality
    """

    name = "base"
    description = "Base tool"
    risk = "low"

    def execute(self, input_data: str):
        """
        Execute the tool's functionality.
        
        Args:
            input_data: Input string from user
            
        Returns:
            str: Result of execution
        """
        raise NotImplementedError("Tools must implement execute()")
