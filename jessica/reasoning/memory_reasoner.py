"""
Phase 99: Memory Reasoning Engine

Jessica can reason over dynamic stored facts and answer naturally
without relying on model fallback.
"""

from typing import Optional


class MemoryReasoner:
    def __init__(self, belief_store):
        self.beliefs = belief_store

    def answer(self, question: str) -> Optional[str]:
        if not question:
            return None

        q = question.lower()
        facts = self.beliefs.get_all_facts()

        responses = []
        handled_keys = set()

        # --- specific checks ---
        if "favorite color" in q:
            color = facts.get("favorite_color")
            if color:
                responses.append(f"Your favorite color is {color}.")
                handled_keys.add("favorite_color")

        if "name" in q:
            name = facts.get("user_name")
            if name:
                responses.append(f"Your name is {name}.")
                handled_keys.add("user_name")

        # --- generic detection ---
        for key, value in facts.items():
            if key in handled_keys:
                continue
            readable_key = key.replace("_", " ")
            if readable_key in q:
                if key == "city":
                    text = f"You live in {value}."
                elif key == "age":
                    text = f"You are {value} years old."
                elif key == "job":
                    text = f"Your job is {value}."
                else:
                    text = f"{readable_key.capitalize()} is {value}."
                if text not in responses:
                    responses.append(text)

        # --- combine answers ---
        if len(responses) == 1:
            return responses[0]

        if len(responses) > 1:
            return " ".join(responses)

        return None
