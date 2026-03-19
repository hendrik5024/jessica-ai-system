import os
from collections import Counter

LOG_FILE = "logs/jessica_internal.log"

last_insight = None


def analyze_logs():

    global last_insight

    if not os.path.exists(LOG_FILE):
        return None

    with open(LOG_FILE, "r") as f:
        logs = f.readlines()

    actions = []

    for line in logs:

        if "intent_detected" in line:
            parts = line.split("intent=")

            if len(parts) > 1:
                actions.append(parts[1].strip())

    if not actions:
        return None

    counts = Counter(actions)

    intent, freq = counts.most_common(1)[0]

    if freq > 5:

        insight = f"Insight: '{intent}' tasks appear frequently ({freq} times). Consider automation."

        if insight == last_insight:
            return None

        last_insight = insight

        return insight

    return None
