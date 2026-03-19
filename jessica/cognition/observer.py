def observe(monologue, intent):
    """
    Meta-cognitive observer.
    Reviews Jessica's reasoning and flags potential issues.
    """

    alerts = []

    if intent == "delete_logs":
        alerts.append("Observer: destructive command detected.")

    if "Potentially destructive" in " ".join(monologue):
        alerts.append("Observer: high risk reasoning detected.")

    if intent is None:
        alerts.append("Observer: intent detection failure.")

    return alerts
