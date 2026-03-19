import os
import re
import sys
import importlib.util

from logger import log_event
from jessica.tools.tool_manager import register_tool


GENERATED_PATH = "jessica/tools/generated"
IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _iter_generated_files(path):
    for file in sorted(os.listdir(path)):
        if file.endswith(".py") and file != "__init__.py":
            module_name = file[:-3]
            yield module_name, os.path.join(path, file)


def _is_valid_module_name(name):
    return bool(IDENTIFIER_PATTERN.match(name))


def _load_module_from_file(module_name, file_path):
    qualified_name = f"jessica.tools.generated.{module_name}"
    spec = importlib.util.spec_from_file_location(qualified_name, file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load spec for {qualified_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)

    return module


def load_generated_tools():
    summary = {
        "loaded": [],
        "skipped": [],
        "errors": [],
    }

    if not os.path.exists(GENERATED_PATH):
        return summary

    for module_name, file_path in _iter_generated_files(GENERATED_PATH):

        if not _is_valid_module_name(module_name):
            reason = f"Invalid module name: {module_name}"
            summary["skipped"].append({"module": module_name, "reason": reason})
            log_event(f"generated_tool_loader | skipped={module_name} | reason={reason}")
            continue

        try:
            module = _load_module_from_file(module_name, file_path)
        except Exception as exc:
            summary["errors"].append({"module": module_name, "error": str(exc)})
            log_event(f"generated_tool_loader | error={module_name} | message={exc}")
            continue

        func = getattr(module, module_name, None)

        if not callable(func):
            reason = f"Missing callable '{module_name}'"
            summary["skipped"].append({"module": module_name, "reason": reason})
            log_event(f"generated_tool_loader | skipped={module_name} | reason={reason}")
            continue

        register_tool(module_name, func)
        summary["loaded"].append(module_name)

    if summary["loaded"]:
        log_event(f"generated_tool_loader | loaded={','.join(summary['loaded'])}")

    return summary
