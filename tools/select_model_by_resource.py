# tools/select_model_by_resource.py
# Simple helper to choose a model from your local collection based on available GPU VRAM
# Usage: python tools/select_model_by_resource.py

import subprocess
import shutil

# Your local model "inventory" (adjust paths or names if you change filenames)
MODELS = {
    "phi-mini": {"name": "Phi-3.5-mini-instruct-Q4_K_M", "min_vram_gb": 0.0, "type": "assistant"},
    "capybara-7b": {"name": "capybarahermes-2.5-mistral-7b", "min_vram_gb": 6.0, "type": "assistant"},
    "codellama-13b": {"name": "codellama-13b-instruct", "min_vram_gb": 12.0, "type": "code"},
    # sd_xl is for images, handle separately
}


def get_nvidia_vram_gb():
    "Return free VRAM in GB for the first GPU, or None if nvidia-smi not found or no GPU."
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True,
        )
        # take first gpu value
        first = out.strip().splitlines()[0]
        return float(first) / 1024.0
    except Exception:
        return None


def choose_model(prefer="assistant"):
    vram = get_nvidia_vram_gb()
    print(
        f"[model-selector] detected GPU free VRAM: {vram} GB"
        if vram is not None
        else "[model-selector] No GPU detected (CPU-only)."
    )
    # Prefer models with lowest min_vram that satisfy vram (or CPU-only if vram None)
    candidates = []
    for key, meta in MODELS.items():
        if prefer and meta["type"] != prefer:
            continue
        min_vram = meta["min_vram_gb"]
        if vram is None:
            # CPU-only: allow only very small models
            if min_vram <= 1.0:
                candidates.append((min_vram, key, meta))
        else:
            if vram >= min_vram:
                candidates.append((min_vram, key, meta))
    # sort by descending min_vram (prefer bigger model that fits)
    candidates.sort(reverse=True)
    if not candidates:
        # fallback: choose phi-mini if exists
        return MODELS["phi-mini"]["name"]
    return candidates[0][2]["name"]


if __name__ == "__main__":
    # choose assistant model (default)
    model = choose_model(prefer="assistant")
    print("[model-selector] recommended model:", model)
    # also show code specialist if GPU big enough
    code_model = None
    vram = get_nvidia_vram_gb()
    if vram is not None and vram >= MODELS["codellama-13b"]["min_vram_gb"]:
        code_model = MODELS["codellama-13b"]["name"]
    print(
        "[model-selector] recommended code model:",
        code_model or "none (use remote or smaller model)",
    )
