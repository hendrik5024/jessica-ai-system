import json
from pathlib import Path


class SettingsManager:

    def __init__(self):

        self.settings_path = Path("jessica/config/system_settings.json")

        if not self.settings_path.exists():
            raise FileNotFoundError("system_settings.json not found")

        self.settings = self.load()

    def load(self):

        with open(self.settings_path, "r") as f:
            return json.load(f)

    def save(self):

        with open(self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):

        return self.settings.get(key)

    def set(self, key, value):

        self.settings[key] = value
        self.save()

    def get_model(self, model_type):

        return self.settings["models"].get(model_type)
