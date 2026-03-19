import sys
import json
import traceback
from datetime import datetime
from pathlib import Path


class DebugEngine:

    def __init__(self, error_store="logs/jessica_errors.jsonl"):
        self.error_store = Path(error_store).resolve()

    def analyze_exception(self, exc_info):

        exc_type, exc_value, exc_traceback = exc_info

        tb = traceback.extract_tb(exc_traceback)

        last = tb[-1]

        file = last.filename
        line = last.lineno
        function = last.name

        return {
            "error": str(exc_value),
            "file": file,
            "line": line,
            "function": function
        }

    def record_exception(self, exc_info, module_hint=None):

        info = self.analyze_exception(exc_info)
        module = (module_hint or Path(info["file"]).stem).replace(".py", "")

        entry = {
            "module": module,
            "function": info["function"],
            "line": info["line"],
            "error": info["error"],
            "file": info["file"],
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }

        self.error_store.parent.mkdir(parents=True, exist_ok=True)
        with self.error_store.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

        return info

    def read_recent_errors(self, module=None, limit=20):

        if not self.error_store.exists():
            return []

        module_name = None
        if module:
            module_name = module.lower().replace(".py", "")

        results = []
        lines = self.error_store.read_text(encoding="utf-8").splitlines()

        for raw in reversed(lines):
            if not raw.strip():
                continue

            try:
                entry = json.loads(raw)
            except Exception:
                continue

            if module_name and str(entry.get("module", "")).lower() != module_name:
                continue

            results.append(entry)
            if len(results) >= limit:
                break

        return results

    def suggest_fix(self, error_message):

        error_lower = str(error_message).lower()

        if "division by zero" in error_lower:
            return {
                "cause": "Potential divide operation with a zero denominator.",
                "patch": "if denominator == 0:\n    return 0"
            }

        if "keyerror" in error_lower:
            return {
                "cause": "Dictionary key may be missing at runtime.",
                "patch": "value = data.get(key, default_value)"
            }

        if "indexerror" in error_lower:
            return {
                "cause": "List access may exceed available bounds.",
                "patch": "if 0 <= index < len(items):\n    return items[index]"
            }

        if "nonetype" in error_lower:
            return {
                "cause": "Operation attempted on a None value.",
                "patch": "if value is None:\n    return fallback_value"
            }

        return {
            "cause": "Unhandled runtime exception pattern.",
            "patch": "Add targeted guard checks and input validation around the failing line."
        }
