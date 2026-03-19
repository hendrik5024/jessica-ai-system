import os
import subprocess
import platform

def can_handle(intent: dict) -> bool:
    return intent.get("intent") in ("open_file", "open_app")

def run(intent: dict, context=None, relevant=None, manager=None):
    target = intent.get("target") or intent.get("text")
    if not target:
        return {"status": "error", "error": "No target specified"}
    path = target.strip()
    try:
        if os.path.exists(path):
            if platform.system() == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return {"status": "ok", "action": f"opened {path}"}
        else:
            return {"status": "not_found", "target": path}
    except Exception as e:
        return {"status": "error", "error": str(e), "relevant_used": bool(relevant)}
