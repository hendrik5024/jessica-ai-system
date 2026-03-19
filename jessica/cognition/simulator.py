def simulate_action(action, parameters=None):
    """
    Basic simulation layer.
    Predicts possible outcomes before execution.
    """

    if action == "delete_logs":
        return {
            "risk": "high",
            "message": "Deleting logs will permanently remove debugging history."
        }

    if action == "run_heavy_task":
        return {
            "risk": "medium",
            "message": "This task may use significant CPU and memory."
        }

    return {
        "risk": "low",
        "message": "No significant risks predicted."
    }
