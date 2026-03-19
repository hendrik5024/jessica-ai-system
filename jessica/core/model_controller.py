"""
Phase 85 — Model Control Layer

Jessica is ALWAYS in control.

Models are used only as tools.
They NEVER speak directly to the user.
"""

from typing import Optional


class ModelController:
    def __init__(self, model=None):
        self.model = model
        self.enabled = True

    def query_model(self, prompt: str) -> Optional[str]:
        """
        Ask the model for information.

        IMPORTANT:
        - Model response is RAW
        - Not returned to user directly
        """
        if not self.enabled or not self.model:
            return None

        try:
            response = self.model.generate(prompt)
            return response
        except Exception:
            return None

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True
