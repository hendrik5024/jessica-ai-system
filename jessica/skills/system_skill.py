def can_handle(intent: dict) -> bool:
    return intent.get("intent") == "system_test"

def run(intent: dict, context=None, relevant=None, manager=None):
    return {"ok": True, "message": "System test successful. Skills framework operational."}