import os
from jessica.llama_cpp_engine.llama_runner import LlamaRunner


class ModelRouter:
    """Multi-brain router with hierarchical model management.
    
    - fast_brain (Phi-3.5 Mini): Intent dispatcher and simple queries
    - logic_brain (Mistral 7B): Recipes and general reasoning
    - code_brain (CodeLlama 13B): Terminal and spreadsheet tasks
    """
    
    def __init__(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # Prefer top-level `models/` if present, else `jessica/models/`
        top_models = os.path.join(repo_root, "models")
        pkg_models = os.path.join(repo_root, "jessica", "models")
        base = top_models if os.path.isdir(top_models) else pkg_models

        # Resolve adapter paths: env overrides, else look for current-pointer files
        chat_lora = os.environ.get("JESSICA_CHAT_LORA")
        if not chat_lora:
            ptr = os.path.join(repo_root, "adapters_gguf", "chat-lora.current")
            if os.path.isfile(ptr):
                try:
                    with open(ptr, "r", encoding="utf-8") as f:
                        chat_lora = f.read().strip()
                except Exception:
                    chat_lora = None

        code_lora = os.environ.get("JESSICA_CODE_LORA")
        if not code_lora:
            ptr = os.path.join(repo_root, "adapters_gguf", "code-lora.current")
            if os.path.isfile(ptr):
                try:
                    with open(ptr, "r", encoding="utf-8") as f:
                        code_lora = f.read().strip()
                except Exception:
                    code_lora = None

        # Fast Brain: Phi-3.5 Mini for intent dispatching and simple chat
        print("[ModelRouter] Loading fast_brain (Phi-3.5 Mini)...")
        self.fast_brain = LlamaRunner(
            model_path=os.path.join(base, "Phi-3.5-mini-instruct-Q4_K_M.gguf"),
            lora_path=None,
            default_n_gpu_layers=32,  # Optimized for speed
        )
        
        # Logic Brain: Mistral 7B for recipes and general reasoning
        print("[ModelRouter] Loading logic_brain (Mistral 7B)...")
        self.logic_brain = LlamaRunner(
            model_path=os.path.join(base, "capybarahermes-2.5-mistral-7b.Q4_K_M.gguf"),
            lora_path=chat_lora,
            default_n_gpu_layers=35,
        )

        # Code Brain: CodeLlama 13B for terminal and spreadsheet tasks
        print("[ModelRouter] Loading code_brain (CodeLlama 13B)...")
        self.code_brain = LlamaRunner(
            model_path=os.path.join(base, "codellama-13b-instruct.Q4_K_M.gguf"),
            lora_path=code_lora,
            default_n_gpu_layers=43,
        )
        
        # Legacy aliases for backward compatibility
        self.chat_model = self.logic_brain
        self.code_model = self.code_brain
        
        print("[ModelRouter] Multi-brain system ready.")
        self.last_model_used: str | None = None
        self.last_route_category: str | None = None

    def record_usage(self, model_used: str, route_category: str | None = None) -> None:
        self.last_model_used = model_used
        self.last_route_category = route_category

    def categorize_intent(self, user_input: str) -> str:
        """Use fast_brain to categorize user intent.
        
        Returns: 'SMALL_TALK', 'CODING', or 'GENERAL_KNOWLEDGE'
        """
        # Fast heuristic for very short inputs (skip model inference)
        if len(user_input.split()) < 5:
            t = user_input.lower()
            greetings = ["hi", "hello", "hey", "thanks", "bye"]
            if any(g in t for g in greetings):
                return "SMALL_TALK"
        
        categorization_prompt = f"""Classify: {user_input}

Reply with ONE word only:
- CHAT (for greetings, small talk)
- CODE (for programming)
- KNOWLEDGE (for facts, advice)

Category:"""
        
        result = self.fast_brain.generate(categorization_prompt, max_tokens=5, temperature=0.0)
        category = result.strip().upper()
        
        # Map to standard categories
        if "CHAT" in category or "SMALL" in category or "TALK" in category:
            return "SMALL_TALK"
        elif "COD" in category or "PROGRAM" in category:
            return "CODING"
        else:
            return "GENERAL_KNOWLEDGE"

    def jessica_think(self, user_input: str, max_tokens: int = 128, temperature: float = 0.7) -> str:
        """Multi-brain inference with intelligent routing.
        
        Workflow:
        1. Fast categorization using fast_brain
        2. Route to specialist brain based on category
        3. Return response
        """
        # Step 1: Fast categorization
        category = self.categorize_intent(user_input)
        print(f"[ModelRouter] Intent: {category}")
        
        # Step 2: Route to appropriate brain
        if category == "SMALL_TALK":
            # Fast brain handles simple chat directly (with reduced tokens)
            self.record_usage("fast_brain", category)
            return self.fast_brain.generate(user_input, max_tokens=min(max_tokens, 80), temperature=temperature)
        
        elif category == "CODING":
            # Deep coding with code_brain
            self.record_usage("code_brain", category)
            return self.code_brain.generate(user_input, max_tokens=max_tokens, temperature=temperature)
        
        else:  # GENERAL_KNOWLEDGE
            # General reasoning with logic_brain
            self.record_usage("logic_brain", category)
            return self.logic_brain.generate(user_input, max_tokens=max_tokens, temperature=temperature)

    def jessica_think_stream(self, user_input: str, max_tokens: int = 128, temperature: float = 0.7):
        """Streaming version of multi-brain inference."""
        # Step 1: Fast categorization
        category = self.categorize_intent(user_input)
        print(f"[ModelRouter] Intent: {category}")
        
        # Step 2: Stream from appropriate brain
        if category == "SMALL_TALK":
            # Use fewer tokens for fast responses
            self.record_usage("fast_brain", category)
            yield from self.fast_brain.generate_stream(user_input, max_tokens=min(max_tokens, 80), temperature=temperature)
        elif category == "CODING":
            self.record_usage("code_brain", category)
            yield from self.code_brain.generate_stream(user_input, max_tokens=max_tokens, temperature=temperature)
        else:  # GENERAL_KNOWLEDGE
            self.record_usage("logic_brain", category)
            yield from self.logic_brain.generate_stream(user_input, max_tokens=max_tokens, temperature=temperature)

    def set_adapter(self, mode: str, lora_path: str | None):
        if mode == "code":
            self.code_brain.lora_path = lora_path
        else:
            self.logic_brain.lora_path = lora_path

    def generate(self, prompt: str, mode: str = "chat", use_router: bool = False):
        """Generate response with optional multi-brain routing.
        
        Args:
            prompt: User input
            mode: 'chat' or 'code' (for direct routing)
            use_router: If True, use intelligent multi-brain routing
        """
        if use_router:
            return self.jessica_think(prompt)
        
        # Legacy direct routing
        if mode == "code":
            self.record_usage("code_brain", "CODING")
            return self.code_brain.generate(prompt)
        self.record_usage("logic_brain", "GENERAL_KNOWLEDGE")
        return self.logic_brain.generate(prompt)

    def generate_with_model(
        self,
        model_key: str,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        record: bool = False,
    ) -> str:
        model_key = (model_key or "").lower()

        if model_key in {"fast", "fast_brain", "phi", "phi-3.5", "phi3"}:
            if record:
                self.record_usage("fast_brain", "SMALL_TALK")
            return self.fast_brain.generate(prompt, max_tokens=max_tokens, temperature=temperature)

        if model_key in {"code", "code_brain", "codellama", "codellama-13b"}:
            if record:
                self.record_usage("code_brain", "CODING")
            return self.code_brain.generate(prompt, max_tokens=max_tokens, temperature=temperature)

        # Default to logic brain
        if record:
            self.record_usage("logic_brain", "GENERAL_KNOWLEDGE")
        return self.logic_brain.generate(prompt, max_tokens=max_tokens, temperature=temperature)

    def generate_stream(self, prompt: str, mode: str = "chat", use_router: bool = False):
        """Stream tokens with optional multi-brain routing."""
        if use_router:
            yield from self.jessica_think_stream(prompt)
            return
        
        # Legacy direct routing
        if mode == "code":
            self.record_usage("code_brain", "CODING")
            yield from self.code_brain.generate_stream(prompt)
        else:
            self.record_usage("logic_brain", "GENERAL_KNOWLEDGE")
            yield from self.logic_brain.generate_stream(prompt)
