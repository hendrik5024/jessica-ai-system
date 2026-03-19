"""
Phase 94: Calculator Tool

Safe mathematical expression evaluator using AST parsing.
"""

import ast
import operator
from jessica.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    """
    Perform safe mathematical calculations.

    Uses AST parsing to allow only basic arithmetic operations.
    Blocks dangerous operations like imports, exec, functions.
    """

    name = "calculate"
    description = "Perform mathematical calculations"
    risk = "low"

    def execute(self, input_data):
        """
        Execute a mathematical calculation.

        Args:
            input_data: User input potentially containing math expression

        Returns:
            str: Calculation result or error message
        """
        try:
            # Extract expression from user input
            expression = self._extract_expression(input_data)

            if not expression:
                return "No expression provided."

            # Safely evaluate the expression
            result = self._safe_eval(expression)
            return f"The answer is {result}"
        except Exception:
            return "I could not evaluate that expression."

    def _extract_expression(self, user_input):
        """
        Extract mathematical expression from user input.

        Strips common trigger words like "calculate", "compute", etc.

        Args:
            user_input: Raw user input string

        Returns:
            str: Cleaned expression
        """
        if not user_input:
            return ""

        text = user_input.lower()

        # Remove common trigger words
        for word in ["calculate", "compute", "evaluate", "what is", "what's"]:
            text = text.replace(word, "")

        return text.strip()

    def _safe_eval(self, expr):
        """
        Safely evaluate a mathematical expression using AST parsing.

        Only allows basic arithmetic operations (add, subtract, multiply, divide).
        Blocks imports, exec, function calls, and variable access.

        Args:
            expr: Mathematical expression string

        Returns:
            Numeric result

        Raises:
            ValueError: If expression contains disallowed operations
        """
        allowed = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

        def eval_(node):
            if isinstance(node, ast.Num):  # Python 3.7 compatibility
                return node.n
            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.BinOp):
                if type(node.op) not in allowed:
                    raise ValueError("Operation not allowed")
                return allowed[type(node.op)](eval_(node.left), eval_(node.right))
            else:
                raise ValueError("Invalid expression")

        return eval_(ast.parse(expr, mode='eval').body)
