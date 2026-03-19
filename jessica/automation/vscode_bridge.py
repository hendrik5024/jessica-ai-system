from __future__ import annotations

import json
import os
from typing import Dict, Any


def _tasks_file() -> str:
    # Use explicit env var if provided; else default to cwd
    path = os.environ.get("JESSICA_TASKS_FILE")
    if path:
        return path
    return os.path.join(os.getcwd(), ".jessica_tasks.json")


def enqueue_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Append a VS Code task to the shared JSON queue file.

    Task schema examples:
    - {"type":"vscode.create_file","path":"C:/proj/file.txt","content":"..."}
    - {"type":"vscode.open_file","path":"C:/proj/file.txt"}
    - {"type":"vscode.show_message","message":"Hello"}
    - {"type":"vscode.run_command","command":"workbench.action.reloadWindow"}
    """
    tf = _tasks_file()
    try:
        if not os.path.exists(tf):
            with open(tf, "w", encoding="utf-8") as f:
                f.write("[]")
        with open(tf, "r", encoding="utf-8") as f:
            arr = json.load(f)
            if not isinstance(arr, list):
                arr = []
        arr.append(task)
        with open(tf, "w", encoding="utf-8") as f:
            json.dump(arr, f, ensure_ascii=False, indent=2)
        return {"ok": True, "file": tf, "count": len(arr)}
    except Exception as e:
        return {"ok": False, "error": str(e), "file": tf}
