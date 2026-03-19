import time
from jessica.cognition.self_improvement import analyze_logs
from jessica.cognition.telemetry import get_telemetry, pop_next_insight


def background_thinking():

    queued_insight = pop_next_insight()

    if queued_insight:
        return queued_insight

    data = get_telemetry()

    if data["state"] == "IDLE":

        insight = analyze_logs()

        if insight:
            return insight

        # Example background reflection
        insight = "Background check complete. System stable."

        return insight

    return None
