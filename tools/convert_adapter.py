import os
import subprocess
import sys

"""
Convenience wrapper to convert a trained HF LoRA adapter into a GGUF LoRA file
usable by llama.cpp. Requires llama.cpp repo present.

Env vars:
- JESSICA_BASE_HF_MODEL_DIR: local path to base HF model folder
- JESSICA_LORA_OUT: path to saved PEFT adapter folder (from train_lora.py)
- JESSICA_GGUF_OUT: output GGUF file path (default: adapters_gguf/chat-lora.gguf)
"""


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    conv_script = os.path.join(repo_root, "llama.cpp", "convert_lora_to_gguf.py")
    base_dir = os.environ.get("JESSICA_BASE_HF_MODEL_DIR")
    lora_dir = os.environ.get("JESSICA_LORA_OUT", os.path.join(repo_root, "adapters", "chat", "latest"))
    gguf_out = os.environ.get("JESSICA_GGUF_OUT", os.path.join(repo_root, "adapters_gguf", "chat-lora.gguf"))

    if not base_dir or not os.path.isdir(base_dir):
        print("[convert_adapter] Set JESSICA_BASE_HF_MODEL_DIR to local base model folder (downloaded HF model).")
        sys.exit(1)
    if not os.path.isfile(conv_script):
        print(f"[convert_adapter] Missing llama.cpp conversion script at {conv_script}")
        sys.exit(1)

    os.makedirs(os.path.dirname(gguf_out), exist_ok=True)

    cmd = [
        sys.executable,
        conv_script,
        "--model-base", base_dir,
        "--lora-model", lora_dir,
        "--outfile", gguf_out,
    ]
    print("[convert_adapter] Running:", " ".join(cmd))
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
