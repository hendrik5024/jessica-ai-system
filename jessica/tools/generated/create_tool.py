import os
import re


TOOLS_FOLDER = "jessica/tools/generated"


def _sanitize_tool_name(tool_name):
    cleaned = re.sub(r"[^a-z0-9_]", "_", (tool_name or "").lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    if not cleaned:
        cleaned = "generated_tool"

    if cleaned[0].isdigit():
        cleaned = f"tool_{cleaned}"

    return cleaned


def _unique_name(base_name):
    candidate = base_name
    counter = 2

    while os.path.exists(os.path.join(TOOLS_FOLDER, f"{candidate}.py")):
        candidate = f"{base_name}_{counter}"
        counter += 1

    return candidate


def _safe_description(description):
    text = str(description or "")
    return text.replace("\x00", " ")


def create_tool(tool_name, description):
    os.makedirs(TOOLS_FOLDER, exist_ok=True)

    safe_name = _sanitize_tool_name(tool_name)
    unique_name = _unique_name(safe_name)
    file_path = os.path.join(TOOLS_FOLDER, f"{unique_name}.py")
    safe_description = _safe_description(description)
    description_literal = repr(safe_description)

    code = f'''PURPOSE = {description_literal}


def {unique_name}(*args, **kwargs):

    """Auto-generated tool."""

    print("Running tool: {unique_name}")

    return "Tool '{unique_name}' executed successfully."
'''

    compile(code, file_path, "exec")

    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(code)

    return unique_name