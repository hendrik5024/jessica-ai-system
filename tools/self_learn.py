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
DATASET_PATH = REPO_ROOT / "datasets" / "user_finetune" / "train.jsonl"
ADAPTERS_GGUF_DIR = REPO_ROOT / "adapters_gguf"
STATE_PATH = REPO_ROOT / "tools" / "selflearn_state.json"
CONFIG_PATH = REPO_ROOT / "tools" / "selflearn_config.json"

def get_model_type():
    return os.environ.get("JESSICA_MODEL_TYPE", "chat")

def get_adapters_dir():
    model_type = get_model_type()
    return REPO_ROOT / "adapters" / model_type

MIN_NEW_EXAMPLES = int(os.environ.get("JESSICA_MIN_EXAMPLES", 200))
VAL_SAMPLES = int(os.environ.get("JESSICA_VAL_SAMPLES", 50))
IMPROVEMENT_THRESHOLD = float(os.environ.get("JESSICA_IMPROVEMENT_THRESHOLD", 0.0))


def run_export():
    os.makedirs(DATASET_PATH.parent, exist_ok=True)
    cmd = [VENV_PY, str(REPO_ROOT / "tools" / "export_dataset.py")]
    print("[self_learn] export:", " ".join(cmd))
    return os.system(" ".join(cmd))


def timestamp_dir(base: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    d = base / ts
    d.mkdir(parents=True, exist_ok=True)
    return d


def count_examples(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in open(path, "r", encoding="utf-8"))


def load_dataset_samples(path: Path, k: int):
    ds = datasets.load_dataset("json", data_files={"train": str(path)})
    items = ds["train"]
    n = min(len(items), k)
    return [items[i] for i in range(n)]


def format_prompt(ex):
    instr = ex.get("instruction", "")
    inp = ex.get("input", "")
    return f"### Instruction:\n{instr}\n\n### Input:\n{inp}\n\n### Response:\n"


def generate_outputs(model, tokenizer, samples):
    outs = []
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    for ex in samples:
        prompt = format_prompt(ex)
        toks = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            gen = model.generate(**toks, max_new_tokens=128, do_sample=False)
        text = tokenizer.decode(gen[0], skip_special_tokens=True)
        if "### Response:" in text:
            text = text.split("### Response:")[-1].strip()
        outs.append(text)
    return outs


def eval_rouge(preds, refs):
    rouge = load_metric("rouge")
    res = rouge.compute(predictions=preds, references=refs)
    return float(res.get("rougeL", 0.0))


def train_adapter(base_model: str, out_dir: Path, model_type: str):
    env = os.environ.copy()
    env["JESSICA_BASE_HF_MODEL"] = base_model
    env["JESSICA_DATASET"] = str(DATASET_PATH)
    env["JESSICA_LORA_OUT"] = str(out_dir)
    env["JESSICA_MODEL_TYPE"] = model_type
    cmd = [VENV_PY, str(REPO_ROOT / "tools" / "train_lora.py")]
    print("[self_learn] train:", " ".join(cmd))
    return os.system(" ".join(cmd))


def convert_adapter(base_model_dir: Path, lora_dir: Path, gguf_out: Path):
    os.makedirs(gguf_out.parent, exist_ok=True)
    env = os.environ.copy()
    env["JESSICA_BASE_HF_MODEL_DIR"] = str(base_model_dir)
    env["JESSICA_LORA_OUT"] = str(lora_dir)
    env["JESSICA_GGUF_OUT"] = str(gguf_out)
    cmd = [VENV_PY, str(REPO_ROOT / "tools" / "convert_adapter.py")]
    print("[self_learn] convert:", " ".join(cmd))
    return os.system(" ".join(cmd))


def promote_adapter(gguf_path: Path, model_type: str):
    ADAPTERS_GGUF_DIR.mkdir(parents=True, exist_ok=True)
    ptr = ADAPTERS_GGUF_DIR / f"{model_type}-lora.current"
    with open(ptr, "w", encoding="utf-8") as f:
        f.write(str(gguf_path))
    print(f"[self_learn] promoted {gguf_path} -> {ptr}")


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.load(open(STATE_PATH, "r", encoding="utf-8"))
    except Exception:
        return {}


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    except Exception as e:
        print(f"[self_learn] config load error: {e}")
        return {}


def main():
    model_type = get_model_type()
    print(f"[self_learn] Starting training for model_type={model_type}")
    
    state = load_state()
    base_model = os.environ.get("JESSICA_BASE_HF_MODEL")
    base_model_dir = os.environ.get("JESSICA_BASE_HF_MODEL_DIR")
    
    if not base_model or not base_model_dir:
        print(f"[self_learn] Missing base_model or base_model_dir for {model_type}")
        return

    # 1) Export dataset
    run_export()
    n = count_examples(DATASET_PATH)
    if n < MIN_NEW_EXAMPLES:
        print(f"[self_learn] Not enough data ({n} < {MIN_NEW_EXAMPLES}), skipping.")
        return

    # 2) Train new adapter versioned
    out_dir = timestamp_dir(get_adapters_dir())
    rc = train_adapter(base_model, out_dir, model_type)
    if rc != 0:
        print("[self_learn] training failed.")
        return

    # 3) Evaluate vs base on small validation split
    samples = load_dataset_samples(DATASET_PATH, VAL_SAMPLES)
    refs = [s.get("output", "") for s in samples]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    tok.pad_token = tok.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    base = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=dtype, device_map="auto" if device == "cuda" else None)
    if device != "cuda":
        base.to(device)
    preds_base = generate_outputs(base, tok, samples)
    score_base = eval_rouge(preds_base, refs)

    peft = PeftModel.from_pretrained(base, str(out_dir)).to(device)
    preds_peft = generate_outputs(peft, tok, samples)
    score_peft = eval_rouge(preds_peft, refs)
    print(f"[self_learn] rougeL base={score_base:.4f} peft={score_peft:.4f}")

    if score_peft + 1e-9 < score_base + IMPROVEMENT_THRESHOLD:
        print("[self_learn] Adapter did not improve; keeping current.")
        save_state({"model_type": model_type, "last": time.time(), "score_base": score_base, "score_peft": score_peft, "promoted": False})
        return

    # 4) Convert to GGUF
    gguf_out = ADAPTERS_GGUF_DIR / f"{model_type}-lora-{out_dir.name}.gguf"
    rc = convert_adapter(Path(base_model_dir), out_dir, gguf_out)
    if rc != 0:
        print("[self_learn] conversion failed.")
        return

    # 5) Promote new adapter
    promote_adapter(gguf_out, model_type)
    save_state({"model_type": model_type, "last": time.time(), "score_base": score_base, "score_peft": score_peft, "promoted": True, "adapter": str(gguf_out)})


if __name__ == "__main__":
    main()
