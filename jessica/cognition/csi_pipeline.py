from jessica.cognition.telemetry import update_risk


def run_cognitive_pipeline(user_input, intent, persona, monologue, alerts):
    """
    Central CSI cognitive pipeline.
    This orchestrates reasoning layers before execution.
    """

    pipeline_state = {
        "intent": intent,
        "persona": persona,
        "alerts": alerts,
        "monologue": monologue
    }

    # Observer already triggered alerts
    if alerts:
        pipeline_state["risk_level"] = "elevated"
    else:
        pipeline_state["risk_level"] = "normal"

    update_risk(pipeline_state["risk_level"])

    return pipeline_state
