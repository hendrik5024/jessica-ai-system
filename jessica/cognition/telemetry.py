from collections import deque
from threading import Lock


telemetry = {
    "state": "IDLE",
    "intent": None,
    "persona": None,
    "risk": "normal",
    "insights": deque(),
    "last_queued_insight": None,
}

telemetry_lock = Lock()


def update_state(state):
    with telemetry_lock:
        telemetry["state"] = state


def update_intent(intent):
    with telemetry_lock:
        telemetry["intent"] = intent


def update_persona(persona):
    with telemetry_lock:
        telemetry["persona"] = persona


def update_risk(risk):
    with telemetry_lock:
        telemetry["risk"] = risk


def queue_insight(insight):
    message = (insight or "").strip()

    if not message:
        return False

    with telemetry_lock:
        if telemetry["last_queued_insight"] == message:
            return False

        telemetry["insights"].append(message)
        telemetry["last_queued_insight"] = message
        return True


def pop_next_insight():
    with telemetry_lock:
        if not telemetry["insights"]:
            return None

        return telemetry["insights"].popleft()


def get_telemetry():
    with telemetry_lock:
        return {
            "state": telemetry["state"],
            "intent": telemetry["intent"],
            "persona": telemetry["persona"],
            "risk": telemetry["risk"],
            "pending_insights": len(telemetry["insights"]),
        }
