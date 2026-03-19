TOOLS = {}


def register_tool(name, func):
    TOOLS[name] = func


class ToolManager:

    def __init__(self):
        self.tools = TOOLS


def execute_tool(name, *args, **kwargs):

    if name not in TOOLS:
        return f"Tool '{name}' not found."

    try:
        return TOOLS[name](*args, **kwargs)
    except Exception as e:
        return f"Tool error: {str(e)}"
