import os
import re


TOOLS_FOLDER = "jessica/tools/generated"

STOPWORDS = {
    "create",
    "tool",
    "to",
    "a",
    "an",
    "the",
    "for",
    "that",
    "which",
    "with",
    "and",
    "from",
    "of",
    "in",
}


def _tokenize(description):
    text = description.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [token for token in text.split() if token]


def _ensure_valid_identifier(name):
    cleaned = re.sub(r"[^a-z0-9_]", "_", name.lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    if not cleaned:
        cleaned = "generated_tool"

    if cleaned[0].isdigit():
        cleaned = f"tool_{cleaned}"

    return cleaned


def _ensure_unique_name(base_name):
    candidate = base_name
    counter = 2

    while os.path.exists(os.path.join(TOOLS_FOLDER, f"{candidate}.py")):
        candidate = f"{base_name}_{counter}"
        counter += 1

    return candidate


def create_tool_name(description):
    tokens = _tokenize(description)
    token_set = set(tokens)

    if {"read", "text"}.issubset(token_set) or (
        "text" in token_set and {"load", "open"}.intersection(token_set)
    ):
        return "text_reader"

    if "csv" in token_set and {"analyze", "analyse", "analysis"}.intersection(token_set):
        return "csv_analyzer"

    if "file" in token_set and {"read", "load", "open"}.intersection(token_set):
        return "file_reader"

    content_tokens = [token for token in tokens if token not in STOPWORDS]

    if not content_tokens:
        return "generated_tool"

    if len(content_tokens) == 1:
        base_name = f"{content_tokens[0]}_tool"
    else:
        base_name = "_".join(content_tokens[:2])

    return _ensure_valid_identifier(base_name)


def generate_tool(description):

    if not os.path.exists(TOOLS_FOLDER):
        os.makedirs(TOOLS_FOLDER)

    tool_name = create_tool_name(description)
    tool_name = _ensure_unique_name(tool_name)

    filename = f"{tool_name}.py"

    path = os.path.join(TOOLS_FOLDER, filename)

    code = f'''
def {tool_name}(*args, **kwargs):

    \"\"\"
    Auto-generated tool
    Purpose: {description}
    \"\"\"

    print("Running tool: {tool_name}")

    return \"Tool '{tool_name}' executed successfully.\"
'''

    with open(path, "w") as f:
        f.write(code)

    return tool_name, filename
