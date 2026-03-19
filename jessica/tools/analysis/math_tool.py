import re


def calculate(expression: str):
    """
    Safe math evaluator
    """

    try:
        # Only allow numbers and operators
        if not re.match(r"^[0-9+\-*/(). ]+$", expression):
            return None

        return eval(expression)
    except Exception:
        return None


def _extract_expression(text: str):
    match = re.search(r"[0-9+\-*/(). ]+", text)
    if not match:
        return None
    return match.group().strip()


class MathTool:
    def can_handle(self, text: str) -> bool:
        return _extract_expression(text) is not None

    def execute(self, text: str) -> str:
        expression = _extract_expression(text)
        if not expression:
            return "I could not evaluate that expression."

        result = calculate(expression)
        if result is None:
            return "I could not evaluate that expression."

        return f"The answer is {result}."
