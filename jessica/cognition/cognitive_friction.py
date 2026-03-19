def apply_cognitive_friction(alerts, intent):
    """
    Applies deliberation when risk is detected.
    """

    if not alerts:
        return None

    if intent == "delete_logs":
        return "High risk action detected. Please confirm before proceeding."

    if len(alerts) > 1:
        return "Multiple risk signals detected. Jessica recommends reviewing this action."

    return None
