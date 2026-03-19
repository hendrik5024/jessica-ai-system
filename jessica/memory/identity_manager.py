import json
import os


IDENTITY_FILE = "jessica/memory/identity.json"


class IdentityManager:

    def __init__(self):

        if not os.path.exists(IDENTITY_FILE):
            raise FileNotFoundError(
                "identity.json not found in jessica/memory/"
            )

        with open(IDENTITY_FILE, "r", encoding="utf-8") as handle:
            self.identity = json.load(handle)

    def get_ai_name(self):
        return self.identity.get("ai_name", "Jessica")

    def get_creator(self):
        return self.identity.get("creator", "Unknown")

    def get_owner(self):
        return self.identity.get("instance_owner", "Unknown")

    def get_architecture(self):
        return self.identity.get(
            "architecture",
            "Cognitive Sovereign Intelligence"
        )