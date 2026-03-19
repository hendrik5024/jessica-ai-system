def check_for_missing_information(intent, user_input):
    """
    Inquiry engine checks if the request lacks necessary details.
    """

    if intent == "delete_file":
        if "file" in user_input.lower() and len(user_input.split()) < 3:
            return "Which file would you like me to delete?"

    if intent == "run_program":
        if len(user_input.split()) < 2:
            return "Which program should I run?"

    return None
