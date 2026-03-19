from pathlib import Path

from jessica.tools import load_generated_tools as loader
from jessica.tools.generated import create_tool as generator
from jessica.tools.tool_manager import TOOLS


def test_loader_skips_bad_modules_and_loads_valid_tool(tmp_path, monkeypatch):
    generated_dir = tmp_path / "generated_tools"
    generated_dir.mkdir(parents=True, exist_ok=True)

    (generated_dir / "good_tool.py").write_text(
        "def good_tool(*args, **kwargs):\n    return 'ok'\n",
        encoding="utf-8",
    )

    (generated_dir / "bad_syntax.py").write_text(
        "def bad_syntax(*args, **kwargs)\n    return 'broken'\n",
        encoding="utf-8",
    )

    (generated_dir / "missing_callable.py").write_text(
        "def something_else(*args, **kwargs):\n    return 'nope'\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(loader, "GENERATED_PATH", str(generated_dir))

    original_tools = dict(TOOLS)
    TOOLS.clear()

    try:
        summary = loader.load_generated_tools()

        assert "good_tool" in TOOLS
        assert "good_tool" in summary["loaded"]

        error_modules = {item["module"] for item in summary["errors"]}
        skipped_modules = {item["module"] for item in summary["skipped"]}

        assert "bad_syntax" in error_modules
        assert "missing_callable" in skipped_modules

    finally:
        TOOLS.clear()
        TOOLS.update(original_tools)


def test_create_tool_escapes_description_safely(tmp_path, monkeypatch):
    monkeypatch.setattr(generator, "TOOLS_FOLDER", str(tmp_path))

    description = 'Quoted "value" with newline\nand triple apostrophes \'\'\''
    tool_name = generator.create_tool("safe_tool", description)

    tool_file = Path(tmp_path) / f"{tool_name}.py"
    assert tool_file.exists()

    source = tool_file.read_text(encoding="utf-8")
    assert "PURPOSE = " in source

    compile(source, str(tool_file), "exec")
