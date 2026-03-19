import os
import subprocess
from typing import Optional


class LlamaRunner:
    def __init__(
        self,
        model_path: str,
        llama_path: str = "llama.cpp/build/bin/",
        lora_path: str | None = None,
        default_n_gpu_layers: int | None = None,
    ):
        # Normalize relative paths against the repository root so callers don't
        # depend on the current working directory.
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        self.model = (
            os.path.abspath(os.path.join(repo_root, model_path))
            if model_path and not os.path.isabs(model_path)
            else model_path
        )

        resolved_llama_path = (
            os.path.abspath(os.path.join(repo_root, llama_path))
            if llama_path and not os.path.isabs(llama_path)
            else llama_path
        )

        self.llama = self._resolve_llama_exe(resolved_llama_path)
        self.lora_path = lora_path
        self.default_n_gpu_layers = default_n_gpu_layers

    def _resolve_llama_exe(self, llama_path: str) -> str:
        """Resolve llama.cpp CLI binary path.

        llama.cpp has used different binary names across versions:
        - newer: `llama-cli` / `llama-cli.exe`
        - older: `main` / `main.exe`

        Builds on Windows via CMake often place binaries under `.../bin/Release/`.
        """
        # Allow overriding via env var (absolute path)
        env_exe = os.environ.get("LLAMA_CPP_EXE")
        if env_exe and os.path.isfile(env_exe):
            return env_exe

        candidates = []
        base = llama_path

        # If a directory like llama.cpp/build was passed, try common bin folders
        if os.path.isdir(base) and os.path.basename(base).lower() == "build":
            base = os.path.join(base, "bin")

        # Prefer passing `llama.cpp/build/bin` as llama_path; support both.
        bin_dirs = [base]
        # Windows Release/Debug subfolders
        bin_dirs.extend([os.path.join(base, "Release"), os.path.join(base, "Debug")])

        if os.name == "nt":
            exe_names = ["llama-cli.exe", "main.exe", "llama.exe"]
        else:
            exe_names = ["llama-cli", "main", "llama"]

        for d in bin_dirs:
            for name in exe_names:
                candidates.append(os.path.join(d, name))

        for c in candidates:
            if os.path.isfile(c):
                return c

        # Fall back to original path expectation (may not exist)
        return candidates[0] if candidates else os.path.join(llama_path, exe_names[0])

    def generate(self, prompt: str, max_tokens: int = 384, temperature: float = 0.7, extra_args: Optional[list] = None) -> str:
        if not os.path.isfile(self.model):
            return f"[model not found] {self.model}"

        cmd = [
            self.llama,
            "-m", self.model,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-p", prompt,
        ]

        # Performance optimizations for low-RAM CPU systems
        env_ngl = os.environ.get("LLAMA_GPU_LAYERS")
        n_gpu_layers = env_ngl if env_ngl is not None else str(self.default_n_gpu_layers or 0)
        cmd.extend([
            "-ngl", n_gpu_layers,   # GPU layers: 0 = CPU only
            "-t", "8",              # CPU threads: Use 8 cores (adjust to your CPU)
            "-b", "64",             # Batch size: Small for low RAM (128MB overhead per token)
            "-c", "2048",           # Context size: Reduced from 4096
            "--mlock",              # Lock model in RAM to prevent swapping
        ])

        # Newer llama.cpp builds auto-enable chat/conversation mode when a chat
        # template is present, which also enables interactive mode and can cause
        # subprocess calls to hang waiting for user input. Force single-shot
        # generation by disabling conversation and hiding the prompt.
        cmd.extend(["-no-cnv", "--no-display-prompt"])

        # Attach LoRA adapter if provided
        if self.lora_path and os.path.isfile(os.path.abspath(self.lora_path)):
            cmd.extend(["-lora", os.path.abspath(self.lora_path)])

        if extra_args:
            cmd.extend(extra_args)

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # Suppress llama.cpp debug output
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                stdin=subprocess.DEVNULL,
            )
            out = (result.stdout or "").strip()
            
            if result.returncode != 0 and not out:
                return "[Error] Model failed to generate a response. Try rephrasing your question."

            # If the model starts producing a fabricated multi-turn transcript,
            # keep only the first assistant reply.
            for marker in ["\nUser:", "\nUSER:", "\n<|im_start|> user", "\n### User:"]:
                idx = out.find(marker)
                if idx != -1:
                    out = out[:idx].strip()
                    break

            for prefix in ["Assistant:", "ASSISTANT:"]:
                if out.startswith(prefix):
                    out = out[len(prefix):].lstrip()

            return out
        except FileNotFoundError:
            return (
                "[llama.cpp not found] No llama.cpp executable found. "
                "Build llama.cpp (CMake) so `llama-cli.exe` or `main.exe` exists under "
                "llama.cpp/build/bin/(Release). Or set LLAMA_CPP_EXE to the full path."
            )
        except Exception as e:
            return f"[llama.cpp exception] {e}"

    def generate_stream(self, prompt: str, max_tokens: int = 128, temperature: float = 0.7, extra_args: Optional[list] = None):
        """Stream tokens as they are generated."""
        if not os.path.isfile(self.model):
            yield f"[model not found] {self.model}"
            return

        cmd = [
            self.llama,
            "-m", self.model,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-p", prompt,
        ]

        # Performance optimizations for low-RAM CPU systems
        env_ngl = os.environ.get("LLAMA_GPU_LAYERS")
        n_gpu_layers = env_ngl if env_ngl is not None else str(self.default_n_gpu_layers or 0)
        cmd.extend([
            "-ngl", n_gpu_layers,   # GPU layers
            "-t", "8",              # CPU threads: Use 8 cores
            "-b", "64",             # Batch size
            "-c", "2048",           # Context size
            "--mlock",              # Lock model in RAM
        ])

        cmd.extend(["-no-cnv", "--no-display-prompt"])

        # Attach LoRA adapter
        if self.lora_path and os.path.isfile(os.path.abspath(self.lora_path)):
            cmd.extend(["-lora", os.path.abspath(self.lora_path)])

        if extra_args:
            cmd.extend(extra_args)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdin=subprocess.DEVNULL,
                bufsize=1,
            )

            # Stream output token by token
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line

            process.wait()

        except FileNotFoundError:
            yield (
                "[llama.cpp not found] No llama.cpp executable found. "
                "Build llama.cpp (CMake) so `llama-cli.exe` or `main.exe` exists under "
                "llama.cpp/build/bin/(Release). Or set LLAMA_CPP_EXE to the full path."
            )
        except Exception as e:
            yield f"[llama.cpp exception] {e}"
