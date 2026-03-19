import datetime

def can_handle(intent: dict) -> bool:
    return intent.get("intent") == "set_reminder"

def run(intent: dict, context=None, relevant=None, manager=None):
    text = intent.get("text", "")
    try:
        parts = text.split(" at ")
        reminder_text = parts[0].replace("remind me to", "").replace("remind me", "").strip()
        when = parts[1].strip() if len(parts) > 1 else None
        manager.memory.save_episode(user="default", input_text=text,
                                    output={"reminder": reminder_text, "when": when},
                                    meta={"type": "reminder"})
        return {"status": "ok", "reminder": reminder_text, "when": when}
    except Exception as e:
        return {"status": "error", "error": str(e), "relevant_used": bool(relevant)}
