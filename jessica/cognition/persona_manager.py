def select_persona(intent, user_input):
    """
    Selects the reasoning persona based on the request.
    """

    text = user_input.lower()

    if "explain" in text or "teach" in text:
        return "TEACHER"

    if "code" in text or "debug" in text or "python" in text:
        return "ENGINEER"

    if "analyze" in text or "report" in text:
        return "ANALYST"

    if intent == "SYSTEM_STATUS":
        return "SYSTEM"

    return "GENERAL"
