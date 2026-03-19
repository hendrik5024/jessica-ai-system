def can_handle(intent: dict) -> bool:
    return intent.get("intent") in ("draft_email", "send_email")


def run(intent: dict, context=None, relevant=None, manager=None):
    to = intent.get("to") or "unknown@domain"
    subject = intent.get("subject") or "No subject"
    body = intent.get("body") or intent.get("text") or ""
    if manager:
        manager.memory.save_episode(user="default", input_text=intent.get("text", ""),
                                    output={"draft": {"to": to, "subject": subject, "body": body}},
                                    meta={"type": "email_draft"})
    return {"status": "ok", "draft": {"to": to, "subject": subject}, "semantic_refs": len(relevant) if relevant else 0}
