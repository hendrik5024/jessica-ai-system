"""
Model Orchestrator - Intelligent Multi-Model Routing & VRAM Management

Manages a 4-model stack:
1. Phi-3.5-mini (Router) - Intent classification
2. Mistral-7b (General) - Chat, personality, general queries
3. CodeLlama-13b (Technical) - Coding, robotics, math
4. SDXL-Turbo (Visual) - Image generation

Features:
- Intelligent intent-based routing
- VRAM management with automatic unloading
- LRU-based model eviction
- Lazy loading for efficiency
- Thread-safe model management
"""

import logging
import torch
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model types in the orchestration stack."""
    ROUTER = "phi-3.5-mini"
    GENERAL = "mistral-7b"
    TECHNICAL = "codellama-13b"
    VISUAL = "sdxl-turbo"


class IntentCategory(Enum):
    """Intent categories for routing."""
    SIMPLE_CHAT = "simple_chat"
    CODING = "coding"
    ROBOTICS = "robotics"
    MATH = "math"
    VISUAL = "visual"
    DESIGN = "design"
    UNKNOWN = "unknown"


@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    model_type: ModelType
    model_path: Optional[Path] = None
    vram_mb: int = 0  # Estimated VRAM usage in MB
    idle_timeout: int = 600  # Seconds before unloading (10 minutes default)
    always_loaded: bool = False  # Keep loaded (for router)


@dataclass
class ModelState:
    """Runtime state of a model."""
    config: ModelConfig
    model: Any = None
    last_used: float = 0.0
    load_count: int = 0
    is_loaded: bool = False


class VRAMManager:
    """
    VRAM Manager - Intelligent memory management for model stack.
    
    Features:
    - Monitors model usage timestamps
    - Unloads idle models after timeout
    - LRU eviction when VRAM limit reached
    - Thread-safe operations
    """
    
    def __init__(self, max_vram_mb: int = 8192):
        """
        Initialize VRAM manager.
        
        Args:
            max_vram_mb: Maximum VRAM to use (default 8GB)
        """
        self.max_vram_mb = max_vram_mb
        self.models: Dict[ModelType, ModelState] = {}
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.running = False
        
        logger.info(f"VRAM Manager initialized with {max_vram_mb}MB limit")
    
    def register_model(self, config: ModelConfig) -> None:
        """Register a model with the VRAM manager."""
        with self.lock:
            self.models[config.model_type] = ModelState(config=config)
            logger.info(f"Registered {config.name} ({config.vram_mb}MB)")
    
    def get_vram_usage(self) -> int:
        """Get current VRAM usage in MB."""
        with self.lock:
            return sum(
                state.config.vram_mb 
                for state in self.models.values() 
                if state.is_loaded
            )
    
    def get_available_vram(self) -> int:
        """Get available VRAM in MB."""
        return self.max_vram_mb - self.get_vram_usage()
    
    def can_load_model(self, model_type: ModelType) -> bool:
        """Check if model can be loaded within VRAM constraints."""
        with self.lock:
            if model_type not in self.models:
                return False
            
            state = self.models[model_type]
            if state.is_loaded:
                return True
            
            available = self.get_available_vram()
            required = state.config.vram_mb
            
            return available >= required
    
    def make_room_for(self, model_type: ModelType) -> bool:
        """
        Make room for a model by unloading idle models.
        
        Returns True if enough space was freed.
        """
        with self.lock:
            if model_type not in self.models:
                return False
            
            target_state = self.models[model_type]
            required_mb = target_state.config.vram_mb
            
            # Check if already have space
            if self.get_available_vram() >= required_mb:
                return True
            
            # Find candidates for unloading (LRU, not always_loaded)
            candidates = []
            for mtype, state in self.models.items():
                if (state.is_loaded and 
                    not state.config.always_loaded and
                    mtype != model_type):
                    candidates.append((state.last_used, mtype, state))
            
            # Sort by least recently used
            candidates.sort(key=lambda x: x[0])
            
            # Unload until we have enough space
            for _, mtype, state in candidates:
                if self.get_available_vram() >= required_mb:
                    return True
                
                logger.info(f"Unloading {state.config.name} to make room for {target_state.config.name}")
                self._unload_model(mtype)
            
            return self.get_available_vram() >= required_mb
    
    def mark_used(self, model_type: ModelType) -> None:
        """Mark a model as recently used."""
        with self.lock:
            if model_type in self.models:
                self.models[model_type].last_used = time.time()
    
    def mark_loaded(self, model_type: ModelType, model: Any) -> None:
        """Mark a model as loaded."""
        with self.lock:
            if model_type in self.models:
                state = self.models[model_type]
                state.model = model
                state.is_loaded = True
                state.last_used = time.time()
                state.load_count += 1
                logger.info(f"Loaded {state.config.name} - VRAM: {self.get_vram_usage()}/{self.max_vram_mb}MB")
    
    def _unload_model(self, model_type: ModelType) -> None:
        """Internal method to unload a model (must hold lock)."""
        if model_type not in self.models:
            return
        
        state = self.models[model_type]
        if not state.is_loaded:
            return
        
        # Delete model reference
        if state.model is not None:
            del state.model
            state.model = None
        
        state.is_loaded = False
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info(f"Unloaded {state.config.name} - VRAM: {self.get_vram_usage()}/{self.max_vram_mb}MB")
    
    def unload_model(self, model_type: ModelType) -> None:
        """Unload a model (public method)."""
        with self.lock:
            self._unload_model(model_type)
    
    def cleanup_idle_models(self) -> None:
        """Unload models that have been idle beyond their timeout."""
        with self.lock:
            current_time = time.time()
            
            for model_type, state in self.models.items():
                if (state.is_loaded and 
                    not state.config.always_loaded and
                    (current_time - state.last_used) > state.config.idle_timeout):
                    
                    idle_minutes = (current_time - state.last_used) / 60
                    logger.info(f"Unloading idle {state.config.name} (idle for {idle_minutes:.1f}m)")
                    self._unload_model(model_type)
    
    def start_cleanup_thread(self, interval_seconds: int = 60) -> None:
        """Start background thread for automatic cleanup."""
        if self.running:
            return
        
        self.running = True
        
        def cleanup_loop():
            while self.running:
                time.sleep(interval_seconds)
                self.cleanup_idle_models()
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info(f"VRAM cleanup thread started (interval: {interval_seconds}s)")
    
    def stop_cleanup_thread(self) -> None:
        """Stop the cleanup thread."""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=2.0)
        logger.info("VRAM cleanup thread stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current VRAM statistics."""
        with self.lock:
            return {
                'total_vram_mb': self.max_vram_mb,
                'used_vram_mb': self.get_vram_usage(),
                'available_vram_mb': self.get_available_vram(),
                'loaded_models': [
                    {
                        'name': state.config.name,
                        'type': state.config.model_type.value,
                        'vram_mb': state.config.vram_mb,
                        'idle_seconds': time.time() - state.last_used,
                        'load_count': state.load_count
                    }
                    for state in self.models.values() if state.is_loaded
                ]
            }


class ModelOrchestrator:
    """
    Model Orchestrator - Intelligent multi-model routing and management.
    
    Routes queries to the appropriate model based on intent:
    - Phi-3.5-mini: Intent classification (always loaded)
    - Mistral-7b: Simple chat, general queries
    - CodeLlama-13b: Coding, robotics, math
    - SDXL-Turbo: Image generation
    """
    
    def __init__(self, models_dir: Path, max_vram_mb: int = 8192):
        """
        Initialize the model orchestrator.
        
        Args:
            models_dir: Directory containing model files
            max_vram_mb: Maximum VRAM to use (default 8GB)
        """
        self.models_dir = Path(models_dir)
        self.vram_manager = VRAMManager(max_vram_mb=max_vram_mb)
        
        # Configure models
        self._configure_models()
        
        # Start VRAM cleanup
        self.vram_manager.start_cleanup_thread(interval_seconds=60)
        
        logger.info("ModelOrchestrator initialized")
    
    def _configure_models(self) -> None:
        """Configure all models in the stack."""
        # Router: Phi-3.5-mini (always loaded)
        self.vram_manager.register_model(ModelConfig(
            name="Phi-3.5-mini",
            model_type=ModelType.ROUTER,
            model_path=self.models_dir / "phi-3.5-mini-instruct-q4_k_m.gguf",
            vram_mb=500,  # Small model
            always_loaded=True
        ))
        
        # General: Mistral-7b
        self.vram_manager.register_model(ModelConfig(
            name="Mistral-7b",
            model_type=ModelType.GENERAL,
            model_path=self.models_dir / "mistral-7b-instruct-v0.2.Q5_K_M.gguf",
            vram_mb=2048,  # ~2GB
            idle_timeout=600  # 10 minutes
        ))
        
        # Technical: CodeLlama-13b
        self.vram_manager.register_model(ModelConfig(
            name="CodeLlama-13b",
            model_type=ModelType.TECHNICAL,
            model_path=self.models_dir / "codellama-13b-instruct.Q5_K_M.gguf",
            vram_mb=4096,  # ~4GB
            idle_timeout=600  # 10 minutes
        ))
        
        # Visual: SDXL-Turbo
        self.vram_manager.register_model(ModelConfig(
            name="SDXL-Turbo",
            model_type=ModelType.VISUAL,
            model_path=self.models_dir / "sdxl-turbo",  # Directory with safetensors
            vram_mb=4500,  # ~4.5GB
            idle_timeout=300  # 5 minutes (unload faster)
        ))
    
    def classify_intent(self, user_query: str) -> IntentCategory:
        """
        Classify user intent using Phi-3.5-mini router.
        
        Args:
            user_query: User's input query
            
        Returns:
            IntentCategory for routing
        """
        # Load router if needed
        router = self._ensure_model_loaded(ModelType.ROUTER)
        
        # Classification prompt
        prompt = f"""Classify the user's intent into ONE category:
- SIMPLE_CHAT: Greetings, casual conversation, personality, feelings, general questions
- CODING: Programming, debugging, code generation, software development
- ROBOTICS: Robot control, kinematics, motion planning, hardware
- MATH: Mathematical calculations, equations, problem solving
- VISUAL: Image generation, drawing, visualization, design
- DESIGN: Creative visual design, UI/UX, graphics

User query: "{user_query}"

Category (one word only):"""
        
        # Get classification (simplified for now)
        response = self._query_router(router, prompt)
        
        # Parse response
        response_lower = response.lower().strip()
        
        if 'visual' in response_lower or 'design' in response_lower:
            return IntentCategory.VISUAL
        elif 'coding' in response_lower or 'code' in response_lower or 'programming' in response_lower:
            return IntentCategory.CODING
        elif 'robotics' in response_lower or 'robot' in response_lower:
            return IntentCategory.ROBOTICS
        elif 'math' in response_lower or 'calculation' in response_lower:
            return IntentCategory.MATH
        else:
            return IntentCategory.SIMPLE_CHAT
    
    def _query_router(self, router, prompt: str) -> str:
        """
        Query the router model (simplified).
        
        In production, this would use llama.cpp inference.
        """
        # Mark as used
        self.vram_manager.mark_used(ModelType.ROUTER)
        
        # Simplified keyword-based classification for now
        # Extract the actual user query from the classification prompt
        if "User query:" in prompt:
            query_line = prompt.split("User query:")[1].strip()
            # Remove quotes and trailing text
            user_query = query_line.split('"')[1] if '"' in query_line else query_line
        else:
            user_query = prompt
        
        query_lower = user_query.lower()
        
        # Priority-based classification (check specific before general)
        if any(kw in query_lower for kw in ['robot', 'kinematics', 'joint', 'motion', 'arm', 'inverse']):
            return "ROBOTICS"
        elif any(kw in query_lower for kw in ['code', 'program', 'function', 'debug', 'python', 'javascript', 'write', 'implement']):
            return "CODING"
        elif any(kw in query_lower for kw in ['calculate', 'solve', 'equation', 'math', 'integral', 'derivative', 'multiply']):
            return "MATH"
        elif any(kw in query_lower for kw in ['image', 'picture', 'draw', 'visualize', 'generate', 'create', 'design']) and \
             any(kw in query_lower for kw in ['of', 'a', 'an', 'the', 'me']):
            # Only classify as visual if it's requesting image generation (has image keywords + article)
            return "VISUAL"
        else:
            return "SIMPLE_CHAT"
    
    def _ensure_model_loaded(self, model_type: ModelType) -> Any:
        """
        Ensure a model is loaded, loading it if necessary.
        
        Args:
            model_type: Type of model to load
            
        Returns:
            The loaded model
        """
        state = self.vram_manager.models[model_type]
        
        # Already loaded?
        if state.is_loaded and state.model is not None:
            self.vram_manager.mark_used(model_type)
            return state.model
        
        # Check if we can load
        if not self.vram_manager.can_load_model(model_type):
            # Try to make room
            if not self.vram_manager.make_room_for(model_type):
                raise RuntimeError(
                    f"Cannot load {state.config.name}: insufficient VRAM "
                    f"({self.vram_manager.get_available_vram()}MB available, "
                    f"{state.config.vram_mb}MB required)"
                )
        
        # Load the model
        logger.info(f"Loading {state.config.name}...")
        model = self._load_model(state.config)
        
        # Mark as loaded
        self.vram_manager.mark_loaded(model_type, model)
        
        return model
    
    def _load_model(self, config: ModelConfig) -> Any:
        """
        Load a model from disk.
        
        Args:
            config: Model configuration
            
        Returns:
            Loaded model
        """
        if config.model_type == ModelType.VISUAL:
            # Load SDXL-Turbo pipeline
            return self._load_sdxl_model(config.model_path)
        else:
            # Load llama.cpp model
            return self._load_llama_model(config.model_path)
    
    def _load_llama_model(self, model_path: Path):
        """Load a llama.cpp model."""
        try:
            from llama_cpp import Llama
            
            return Llama(
                model_path=str(model_path),
                n_ctx=2048,
                n_gpu_layers=-1 if torch.cuda.is_available() else 0,
                verbose=False
            )
        except ImportError:
            logger.warning("llama-cpp-python not available, using mock")
            return f"Mock-{model_path.name}"
    
    def _load_sdxl_model(self, model_path: Path):
        """Load SDXL-Turbo pipeline."""
        try:
            from diffusers import AutoPipelineForText2Image
            
            pipeline = AutoPipelineForText2Image.from_pretrained(
                "stabilityai/sdxl-turbo",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                variant="fp16" if torch.cuda.is_available() else None
            )
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pipeline = pipeline.to(device)
            pipeline.enable_attention_slicing()
            
            return pipeline
        except ImportError:
            logger.warning("diffusers not available, using mock")
            return "Mock-SDXL"
    
    def process_query(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query through the orchestration stack.
        
        Args:
            user_query: User's input
            context: Optional context dictionary
            
        Returns:
            Response dictionary with model output and metadata
        """
        start_time = time.time()
        
        # Step 1: Classify intent
        intent = self.classify_intent(user_query)
        logger.info(f"Classified intent: {intent.value}")
        
        # Step 2: Route to appropriate model
        if intent in [IntentCategory.VISUAL, IntentCategory.DESIGN]:
            response = self._handle_visual(user_query)
            model_used = ModelType.VISUAL
        elif intent in [IntentCategory.CODING, IntentCategory.ROBOTICS, IntentCategory.MATH]:
            response = self._handle_technical(user_query, intent)
            model_used = ModelType.TECHNICAL
        else:
            response = self._handle_general(user_query)
            model_used = ModelType.GENERAL
        
        # Step 3: Prepare response
        elapsed = time.time() - start_time
        
        return {
            'response': response,
            'intent': intent.value,
            'model_used': model_used.value,
            'elapsed_seconds': round(elapsed, 2),
            'vram_stats': self.vram_manager.get_stats()
        }
    
    def _handle_visual(self, query: str) -> str:
        """Handle visual/design queries with SDXL-Turbo."""
        # Use existing image generation skill
        from jessica.skills.image_generation_skill import can_handle, run
        
        intent = {"text": query}
        
        if can_handle(intent):
            result = run(intent)
            return result.get('reply', 'Image generation failed')
        else:
            return "I can generate images, but I need a description. Try: 'Generate an image of...'"
    
    def _handle_technical(self, query: str, intent: IntentCategory) -> str:
        """Handle technical queries with CodeLlama-13b."""
        model = self._ensure_model_loaded(ModelType.TECHNICAL)
        
        # Use llama.cpp model
        if isinstance(model, str) and model.startswith("Mock-"):
            return f"[CodeLlama-13b] Technical response for: {query}"
        
        try:
            # Real llama.cpp inference
            response = model(
                prompt=f"<s>[INST] {query} [/INST]",
                max_tokens=512,
                temperature=0.7,
                top_p=0.9,
                stop=["</s>"]
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"CodeLlama inference error: {e}")
            return f"Error processing technical query: {str(e)}"
    
    def _handle_general(self, query: str) -> str:
        """Handle general queries with Mistral-7b."""
        model = self._ensure_model_loaded(ModelType.GENERAL)
        
        # Use llama.cpp model
        if isinstance(model, str) and model.startswith("Mock-"):
            return f"[Mistral-7b] General response for: {query}"
        
        try:
            # Real llama.cpp inference
            response = model(
                prompt=f"<s>[INST] {query} [/INST]",
                max_tokens=512,
                temperature=0.8,
                top_p=0.95,
                stop=["</s>"]
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Mistral inference error: {e}")
            return f"Error processing query: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            'orchestrator': 'active',
            'vram': self.vram_manager.get_stats(),
            'models': {
                mtype.value: {
                    'loaded': state.is_loaded,
                    'load_count': state.load_count,
                    'idle_seconds': time.time() - state.last_used if state.is_loaded else None
                }
                for mtype, state in self.vram_manager.models.items()
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown the orchestrator and cleanup resources."""
        logger.info("Shutting down ModelOrchestrator...")
        
        # Stop cleanup thread
        self.vram_manager.stop_cleanup_thread()
        
        # Unload all models
        for model_type in list(self.vram_manager.models.keys()):
            self.vram_manager.unload_model(model_type)
        
        logger.info("ModelOrchestrator shutdown complete")


# Singleton instance
_orchestrator: Optional[ModelOrchestrator] = None


def get_orchestrator(models_dir: Optional[Path] = None, max_vram_mb: int = 8192) -> ModelOrchestrator:
    """Get or create the singleton ModelOrchestrator."""
    global _orchestrator
    
    if _orchestrator is None:
        if models_dir is None:
            models_dir = Path.home() / ".jessica" / "models"
        
        _orchestrator = ModelOrchestrator(models_dir, max_vram_mb)
    
    return _orchestrator
