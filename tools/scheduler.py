import os
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

import datasets
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from evaluate import load as load_metric

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PY = os.environ.get("VENV_PY", str((REPO_ROOT / ".venv" / "Scripts" / "python.exe")))
CONFIG_PATH = REPO_ROOT / "tools" / "selflearn_config.json"
STATE_PATH = REPO_ROOT / "tools" / "selflearn_state.json"


def load_config():
    if not CONFIG_PATH.exists():
        return {"models": {}, "training": {}, "evaluation": {}}
    try:
        return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    except Exception as e:
        print(f"[scheduler] config load error: {e}")
        return {"models": {}, "training": {}, "evaluation": {}}


def load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.load(open(STATE_PATH, "r", encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run_self_learn(model_type: str, cfg: dict):
    """Delegate to self_learn.py for a specific model type."""
    env = os.environ.copy()
    env["JESSICA_MODEL_TYPE"] = model_type
    
    model_cfg = cfg.get("models", {}).get(model_type, {})
    env["JESSICA_BASE_HF_MODEL"] = model_cfg.get("base_model", "")
    env["JESSICA_BASE_HF_MODEL_DIR"] = model_cfg.get("base_model_dir", "")
    
    train_cfg = cfg.get("training", {})
    for key, val in train_cfg.items():
        env[f"JESSICA_{key.upper()}"] = str(val)
    
    eval_cfg = cfg.get("evaluation", {})
    for key, val in eval_cfg.items():
        env[f"JESSICA_{key.upper()}"] = str(val)

    cmd = [VENV_PY, str(REPO_ROOT / "tools" / "self_learn.py")]
    print(f"[scheduler] Running {model_type}: {' '.join(cmd)}")
    return os.system(" ".join(cmd))


def main():
    cfg = load_config()
    state = load_state()
    
    enabled_models = []
    for model_type, model_cfg in cfg.get("models", {}).items():
        if model_cfg.get("enabled"):
            enabled_models.append(model_type)
    
    if not enabled_models:
        print("[scheduler] No models enabled in config.")
        return
    
    print(f"[scheduler] Running self-learning for: {enabled_models}")
    results = {}
    for model_type in enabled_models:
        rc = run_self_learn(model_type, cfg)
        results[model_type] = "success" if rc == 0 else "failed"
    
    state["last_run"] = time.time()
    state["results"] = results
    save_state(state)
    print(f"[scheduler] Results: {results}")


if __name__ == "__main__":
    main()
