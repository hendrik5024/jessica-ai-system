def can_handle(intent):
    return intent.get("intent") == "code"


def run(intent, context, relevant, manager):
    code_request = intent["text"]

    prompt = f"""
You are Jessica, an offline AI coding assistant. Refer to yourself only as Jessica (never Phi or model names).
Generate correct code only.

User request:
{code_request}

Code:
"""

    return manager.model_router.generate(prompt, mode="code")
