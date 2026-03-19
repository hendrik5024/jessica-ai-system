from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model_path: str
    log_file: str


def _parse_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def load_settings(env_file: str = ".env") -> Settings:
    env_values = _parse_env_file(Path(env_file))

    model_path = env_values.get("MODEL_PATH", "models/tinyllama")
    log_file = env_values.get("LOG_FILE", "logs/jessica_internal.log")

    return Settings(model_path=model_path, log_file=log_file)


_DEFAULT_SETTINGS = load_settings()
MODEL_PATH = _DEFAULT_SETTINGS.model_path
LOG_FILE = _DEFAULT_SETTINGS.log_file