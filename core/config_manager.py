import json
import os


class ConfigManager:
    _config = None

    @classmethod
    def load_config(cls, path="config/config.json"):
        if cls._config is None:
            full_path = os.path.abspath(path)

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Config file not found: {full_path}")

            with open(full_path, "r") as file:
                cls._config = json.load(file)

        return cls._config

    @classmethod
    def get(cls, *keys, default=None):
        config = cls.load_config()

        value = config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

        return default if value is None else value
