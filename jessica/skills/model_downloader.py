"""
Autonomous Model Downloader for Jessica
Allows Jessica to discover and download models from HuggingFace, TensorFlow Hub, etc.
without explicit user instruction
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import subprocess
import sys


class ModelDownloader:
    """Autonomous model discovery and downloading system."""
    
    # Model repository sources
    MODEL_SOURCES = {
        "huggingface": {
            "url": "https://huggingface.co/api/models",
            "auth_header": "Authorization",
            "requires_token": True,
            "default_cache": os.path.expanduser("~/.cache/huggingface/hub"),
            "popular_models": {
                "text-generation": ["meta-llama/Llama-2-7b", "gpt2", "facebook/opt-350m"],
                "image-generation": ["runwayml/stable-diffusion-v1-5", "stabilityai/stable-diffusion-3"],
                "text-classification": ["distilbert-base-uncased", "roberta-base"],
                "summarization": ["facebook/bart-large-cnn", "t5-base"],
                "translation": ["Helsinki-NLP/opus-mt-en-es", "facebook/m2m100_418M"],
                "speech": ["openai/whisper-base", "facebook/wav2vec2-base"],
                "embeddings": ["sentence-transformers/all-MiniLM-L6-v2", "all-mpnet-base-v2"],
            }
        },
        "tensorflow-hub": {
            "url": "https://tfhub.dev/api",
            "auth_header": None,
            "requires_token": False,
            "default_cache": os.path.expanduser("~/tensorflow_models"),
            "popular_models": {
                "text-embedding": ["google/universal-sentence-encoder"],
                "image-classification": ["inception_v3", "mobilenet_v2"],
            }
        },
        "pytorch-hub": {
            "url": "https://pytorch.org/hub",
            "auth_header": None,
            "requires_token": False,
            "default_cache": os.path.expanduser("~/.torch/hub"),
            "popular_models": {
                "object-detection": ["yolov5s", "fasterrcnn_resnet50_fpn"],
                "face-recognition": ["face_detection_yunet"],
            }
        }
    }
    
    def __init__(self, hf_token: Optional[str] = None):
        """Initialize model downloader with optional HuggingFace token."""
        self.hf_token = hf_token or self._get_hf_token()
        self.models_cache = {}
        self.download_history = []
    
    @staticmethod
    def _get_hf_token() -> Optional[str]:
        """Try to retrieve HuggingFace token from environment or config."""
        # Check environment variable
        if token := os.environ.get("HUGGINGFACE_TOKEN"):
            return token
        
        # Check HuggingFace CLI config
        hf_config = Path.home() / ".huggingface" / "token"
        if hf_config.exists():
            return hf_config.read_text().strip()
        
        return None
    
    def search_models(
        self,
        task: str,
        source: str = "huggingface",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for models by task/category.
        
        Tasks: "text-generation", "image-generation", "text-classification",
               "summarization", "translation", "speech", "embeddings", etc.
        """
        if source not in self.MODEL_SOURCES:
            return {
                "ok": False,
                "error": f"Unknown source: {source}. Available: {list(self.MODEL_SOURCES.keys())}"
            }
        
        source_config = self.MODEL_SOURCES[source]
        popular = source_config.get("popular_models", {})
        
        if task not in popular:
            return {
                "ok": False,
                "error": f"Task not found. Available: {list(popular.keys())}",
                "available_tasks": list(popular.keys())
            }
        
        models = popular.get(task, [])[:limit]
        return {
            "ok": True,
            "source": source,
            "task": task,
            "models": models,
            "count": len(models),
            "cache_dir": source_config["default_cache"]
        }
    
    def model_info(
        self,
        model_id: str,
        source: str = "huggingface"
    ) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
        try:
            if source == "huggingface":
                return self._get_hf_model_info(model_id)
            elif source == "tensorflow-hub":
                return self._get_tfhub_model_info(model_id)
            else:
                return {"ok": False, "error": f"Info retrieval not implemented for {source}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _get_hf_model_info(self, model_id: str) -> Dict[str, Any]:
        """Fetch model info from HuggingFace API."""
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        try:
            response = requests.get(
                f"https://huggingface.co/api/models/{model_id}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "ok": True,
                "model_id": model_id,
                "name": data.get("modelId"),
                "description": data.get("description", "")[:200],
                "downloads": data.get("downloads"),
                "likes": data.get("likes"),
                "tags": data.get("tags", []),
                "url": f"https://huggingface.co/{model_id}",
                "library": data.get("library_name"),
                "size_gb": self._estimate_model_size(data),
            }
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}
    
    def _get_tfhub_model_info(self, model_id: str) -> Dict[str, Any]:
        """Fetch model info from TensorFlow Hub."""
        return {
            "ok": True,
            "model_id": model_id,
            "url": f"https://tfhub.dev/google/{model_id}",
            "source": "tensorflow-hub",
            "note": "Model info: use model_id directly with tensorflow-hub library"
        }
    
    @staticmethod
    def _estimate_model_size(hf_data: Dict) -> Optional[float]:
        """Estimate model size in GB from HuggingFace metadata."""
        # Very rough estimation based on parameter count if available
        # In real usage, would check actual model files
        if "safetensors" in str(hf_data.get("siblings", [])):
            return 2.0  # Placeholder
        return None
    
    def download_model(
        self,
        model_id: str,
        source: str = "huggingface",
        cache_dir: Optional[str] = None,
        local_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a model autonomously.
        
        Supports automatic download via library managers or direct download.
        """
        try:
            if source == "huggingface":
                return self._download_hf_model(model_id, cache_dir, local_dir)
            elif source == "pytorch-hub":
                return self._download_pytorch_model(model_id)
            else:
                return {"ok": False, "error": f"Download not supported for {source}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _download_hf_model(
        self,
        model_id: str,
        cache_dir: Optional[str] = None,
        local_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download from HuggingFace using transformers/diffusers library."""
        cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface/hub")
        os.makedirs(cache_dir, exist_ok=True)
        
        try:
            # Auto-detect library based on model type
            library = self._detect_hf_library(model_id)
            
            if library == "transformers":
                return self._download_hf_transformers(model_id, cache_dir, local_dir)
            elif library == "diffusers":
                return self._download_hf_diffusers(model_id, cache_dir, local_dir)
            else:
                return self._download_hf_generic(model_id, cache_dir)
        except Exception as e:
            return {"ok": False, "error": str(e), "model_id": model_id}
    
    def _detect_hf_library(self, model_id: str) -> str:
        """Detect which library to use for HuggingFace model."""
        # Simple heuristic based on model name
        model_lower = model_id.lower()
        
        if any(x in model_lower for x in ["stable-diffusion", "latent-diffusion", "controlnet"]):
            return "diffusers"
        elif any(x in model_lower for x in ["llama", "gpt", "bert", "roberta", "t5"]):
            return "transformers"
        else:
            return "transformers"  # Default
    
    def _download_hf_transformers(
        self,
        model_id: str,
        cache_dir: str,
        local_dir: Optional[str]
    ) -> Dict[str, Any]:
        """Download using transformers library."""
        # Check if transformers is installed
        try:
            import transformers
        except ImportError:
            return {
                "ok": False,
                "error": "transformers library not installed",
                "suggestion": "pip install transformers torch",
                "manual_download": f"https://huggingface.co/{model_id}"
            }
        
        try:
            # Import and download
            from transformers import AutoModel, AutoTokenizer
            
            print(f"Downloading {model_id} from HuggingFace...")
            
            # Download model
            model = AutoModel.from_pretrained(model_id, cache_dir=cache_dir)
            
            # Download tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
            
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
                model.save_pretrained(local_dir)
                tokenizer.save_pretrained(local_dir)
            
            return {
                "ok": True,
                "model_id": model_id,
                "source": "huggingface",
                "library": "transformers",
                "cache_dir": cache_dir,
                "local_save": local_dir if local_dir else None,
                "ready_to_use": True,
                "import_code": f"from transformers import AutoModel, AutoTokenizer\nmodel = AutoModel.from_pretrained('{model_id}')\ntokenizer = AutoTokenizer.from_pretrained('{model_id}')"
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "model_id": model_id,
                "manual_download": f"https://huggingface.co/{model_id}"
            }
    
    def _download_hf_diffusers(
        self,
        model_id: str,
        cache_dir: str,
        local_dir: Optional[str]
    ) -> Dict[str, Any]:
        """Download using diffusers library."""
        try:
            import diffusers
        except ImportError:
            return {
                "ok": False,
                "error": "diffusers library not installed",
                "suggestion": "pip install diffusers torch",
                "manual_download": f"https://huggingface.co/{model_id}"
            }
        
        try:
            from diffusers import StableDiffusionPipeline
            
            print(f"Downloading {model_id} from HuggingFace...")
            
            # Download model
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                cache_dir=cache_dir,
                torch_dtype="auto"
            )
            
            if local_dir:
                pipeline.save_pretrained(local_dir)
            
            return {
                "ok": True,
                "model_id": model_id,
                "source": "huggingface",
                "library": "diffusers",
                "cache_dir": cache_dir,
                "local_save": local_dir if local_dir else None,
                "ready_to_use": True,
                "import_code": f"from diffusers import StableDiffusionPipeline\npipeline = StableDiffusionPipeline.from_pretrained('{model_id}')\nimage = pipeline('your prompt').images[0]"
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "model_id": model_id,
                "manual_download": f"https://huggingface.co/{model_id}"
            }
    
    def _download_hf_generic(
        self,
        model_id: str,
        cache_dir: str
    ) -> Dict[str, Any]:
        """Generic download using huggingface_hub library."""
        try:
            from huggingface_hub import snapshot_download
        except ImportError:
            return {
                "ok": False,
                "error": "huggingface_hub library not installed",
                "suggestion": "pip install huggingface-hub",
                "manual_download": f"https://huggingface.co/{model_id}"
            }
        
        try:
            print(f"Downloading {model_id}...")
            local_dir = snapshot_download(
                model_id,
                cache_dir=cache_dir,
                token=self.hf_token
            )
            
            return {
                "ok": True,
                "model_id": model_id,
                "local_path": local_dir,
                "ready_to_use": True
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "model_id": model_id}
    
    def _download_pytorch_model(self, model_id: str) -> Dict[str, Any]:
        """Download from PyTorch Hub."""
        try:
            import torch
        except ImportError:
            return {"ok": False, "error": "torch not installed"}
        
        try:
            print(f"Downloading {model_id} from PyTorch Hub...")
            model = torch.hub.load("pytorch/vision:v0.10", model_id, pretrained=True)
            
            return {
                "ok": True,
                "model_id": model_id,
                "source": "pytorch-hub",
                "ready_to_use": True
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_download_status(self, model_id: str) -> Dict[str, Any]:
        """Check if a model is already downloaded."""
        # Check HuggingFace cache
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
        
        if os.path.exists(hf_cache):
            for item in os.listdir(hf_cache):
                if model_id.replace("/", "--") in item:
                    return {
                        "ok": True,
                        "model_id": model_id,
                        "cached": True,
                        "cache_path": os.path.join(hf_cache, item)
                    }
        
        return {
            "ok": True,
            "model_id": model_id,
            "cached": False,
            "needs_download": True
        }
    
    def suggest_model_for_task(self, task_description: str) -> Dict[str, Any]:
        """
        Autonomously suggest a model based on task description.
        
        Examples:
        - "I want to generate images from text" → Stable Diffusion
        - "Analyze sentiment of tweets" → Distilbert or similar
        - "Generate code completions" → Code LLaMA or similar
        """
        task_lower = task_description.lower()
        
        # Simple keyword matching to suggest models
        suggestions = []
        
        if any(x in task_lower for x in ["image", "generate", "text-to-image", "picture"]):
            suggestions.append({
                "task": "text-to-image",
                "model": "runwayml/stable-diffusion-v1-5",
                "source": "huggingface",
                "reason": "Best for text-to-image generation"
            })
        
        if any(x in task_lower for x in ["sentiment", "classify", "emotion", "opinion"]):
            suggestions.append({
                "task": "text-classification",
                "model": "distilbert-base-uncased-finetuned-sst-2-english",
                "source": "huggingface",
                "reason": "Sentiment analysis model"
            })
        
        if any(x in task_lower for x in ["summarize", "summary", "tldr", "abstract"]):
            suggestions.append({
                "task": "summarization",
                "model": "facebook/bart-large-cnn",
                "source": "huggingface",
                "reason": "Best for text summarization"
            })
        
        if any(x in task_lower for x in ["translate", "language", "spanish", "french"]):
            suggestions.append({
                "task": "translation",
                "model": "Helsinki-NLP/opus-mt-en-es",
                "source": "huggingface",
                "reason": "Language translation model"
            })
        
        if any(x in task_lower for x in ["speech", "audio", "transcribe", "whisper"]):
            suggestions.append({
                "task": "speech-to-text",
                "model": "openai/whisper-base",
                "source": "huggingface",
                "reason": "Speech recognition model"
            })
        
        if any(x in task_lower for x in ["embed", "similarity", "semantic", "vector"]):
            suggestions.append({
                "task": "text-embedding",
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "source": "huggingface",
                "reason": "Text embedding and semantic similarity"
            })
        
        if not suggestions:
            return {
                "ok": False,
                "error": "Could not match task description to known models",
                "hint": "Try using specific keywords like 'image', 'sentiment', 'summarize', 'translate', 'speech', or 'embed'"
            }
        
        return {
            "ok": True,
            "task_description": task_description,
            "suggestions": suggestions,
            "count": len(suggestions),
            "recommended": suggestions[0]  # Most relevant
        }
    
    def autonomous_download(self, requirement: str) -> Dict[str, Any]:
        """
        Main autonomous download method - Jessica uses this to fetch what she needs.
        
        She can call this without explicit user instruction when she needs a model.
        """
        # First try to suggest appropriate model
        suggestions = self.suggest_model_for_task(requirement)
        
        if not suggestions.get("ok"):
            return suggestions
        
        # Get the recommended model
        recommended = suggestions.get("recommended", {})
        model_id = recommended.get("model")
        source = recommended.get("source", "huggingface")
        
        # Check if already cached
        status = self.get_download_status(model_id)
        if status.get("cached"):
            return {
                "ok": True,
                "model_id": model_id,
                "already_cached": True,
                "cache_path": status.get("cache_path"),
                "ready_to_use": True,
                "message": f"Model {model_id} is already available locally"
            }
        
        # Download the model
        print(f"Jessica autonomously downloading: {model_id}")
        download_result = self.download_model(model_id, source)
        
        # Log download
        if download_result.get("ok"):
            self.download_history.append({
                "model_id": model_id,
                "requirement": requirement,
                "success": True
            })
        
        return download_result
