def generate_monologue(user_input, intent):
    """
    Internal reasoning layer.
    This text is never shown to the user.
    """

    thoughts = []

    thoughts.append(f"User input received: {user_input}")
    thoughts.append(f"Detected intent: {intent}")

    if intent == "delete_logs":
        thoughts.append("Potentially destructive command detected.")
        thoughts.append("Simulation should verify safety.")

    if intent == "SYSTEM_STATUS":
        thoughts.append("Safe informational query.")

    if intent == "GET_NAME":
        thoughts.append("Memory lookup required.")

    return thoughts
