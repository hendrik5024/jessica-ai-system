"""
Image Generation Skill - Offline Image Generation with Stable Diffusion XL Turbo

Provides:
- Offline image generation using local Stable Diffusion XL Turbo model
- GPU/CPU device detection and optimization
- Fast inference (4 steps for speed)
- Persistent caching of model pipeline
- Automatic image saving with timestamps
"""

import logging
import torch
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Check if diffusers is available
try:
    from diffusers import AutoPipelineForText2Image
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    logger.warning("diffusers library not found. Install with: pip install diffusers")


class ImageGenerator:
    """Handles offline image generation with caching."""
    
    def __init__(self):
        """Initialize the image generator with lazy loading."""
        self.pipeline = None
        self.device = None
        self.output_dir = Path.home() / "Jessica_Images" / "generated_images"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image output directory: {self.output_dir}")
    
    def _init_device(self) -> str:
        """Detect and return available device."""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("CUDA not available, using CPU (slower)")
        
        return device
    
    def _init_pipeline(self) -> None:
        """Initialize the diffusion pipeline (lazy loading)."""
        if self.pipeline is not None:
            return
        
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("diffusers library is required. Install with: pip install diffusers")
        
        logger.info("Loading Stable Diffusion XL Turbo model...")
        
        # Detect device
        self.device = self._init_device()
        
        try:
            # Load the optimized SDXL Turbo pipeline
            # This model is smaller and faster than regular SDXL
            self.pipeline = AutoPipelineForText2Image.from_pretrained(
                "stabilityai/sdxl-turbo",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable attention slicing for memory efficiency
            self.pipeline.enable_attention_slicing()
            
            logger.info("✅ Stable Diffusion XL Turbo model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        steps: int = 4,
        width: int = 512,
        height: int = 512,
        guidance_scale: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            steps: Number of inference steps (4 for speed, up to 50 for quality)
            width: Image width in pixels (must be multiple of 8)
            height: Image height in pixels (must be multiple of 8)
            guidance_scale: Guidance scale (0 = no guidance for speed)
        
        Returns:
            Dictionary with image path, prompt, and generation time
        """
        # Initialize pipeline on first use
        if self.pipeline is None:
            self._init_pipeline()
        
        try:
            logger.info(f"Generating image: '{prompt}' ({width}x{height}, {steps} steps)")
            
            # Generate image
            with torch.no_grad():
                result = self.pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=steps,
                    guidance_scale=guidance_scale
                )
            
            image = result.images[0]
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            # Sanitize prompt for filename (remove special chars)
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
            if not safe_prompt:
                safe_prompt = "image"
            
            filename = f"{timestamp}_{safe_prompt}.png"
            image_path = self.output_dir / filename
            
            # Save image
            image.save(image_path)
            logger.info(f"✅ Image saved: {image_path}")
            
            return {
                'status': 'success',
                'image_path': str(image_path),
                'prompt': prompt,
                'size': f"{width}x{height}",
                'steps': steps,
                'device': self.device,
                'message': f"Generated {width}x{height} image in {steps} steps"
            }
        
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                'status': 'error',
                'message': f"Failed to generate image: {str(e)}",
                'prompt': prompt
            }
    
    def clear_cache(self) -> None:
        """Unload model from memory to free resources."""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Model cache cleared")


# Singleton instance
_image_generator: Optional[ImageGenerator] = None


def get_image_generator() -> ImageGenerator:
    """Get or create singleton image generator instance."""
    global _image_generator
    if _image_generator is None:
        _image_generator = ImageGenerator()
    return _image_generator


# ============================================================================
# JESSICA SKILL INTEGRATION
# ============================================================================

def can_handle(intent: Dict) -> bool:
    """
    Check if this is an image generation request.
    
    Examples:
    - "Generate an image of a sunset over mountains"
    - "Create a picture of a cat playing with yarn"
    - "Make an image: futuristic city skyline"
    """
    text = intent.get("text", "").lower()
    
    # Keywords that indicate image generation request
    keywords = [
        "generate image",
        "generate a image",
        "create image",
        "create a image",
        "make image",
        "make a image",
        "draw image",
        "draw a image",
        "picture of",
        "image of",
        "visualize",
        "imagine",
        "create a picture",
        "draw me",
        "generate me",
        "generate an image"
    ]
    
    return any(keyword in text for keyword in keywords)


def run(
    intent: Dict,
    context: Optional[Dict] = None,
    relevant=None,
    manager=None
) -> Dict[str, Any]:
    """
    Handle image generation request.
    
    Parses the prompt from the query and generates an offline image.
    """
    try:
        query = intent.get("text", "").lower()
        
        # Extract prompt by removing command keywords
        prompt = query
        remove_phrases = [
            "generate image of ",
            "generate a image of ",
            "create image of ",
            "create a image of ",
            "make image of ",
            "make a image of ",
            "draw image of ",
            "draw a image of ",
            "generate an image of ",
            "picture of ",
            "image of ",
            "visualize ",
            "imagine ",
            "create a picture of ",
            "draw me a ",
            "generate me an? ",
            "generate an? image of "
        ]
        
        for phrase in remove_phrases:
            if phrase in prompt:
                prompt = prompt.replace(phrase, "").strip()
                break
        
        # If still too generic, use entire query as prompt
        if not prompt or len(prompt) < 3:
            prompt = query.replace("generate", "").replace("image", "").replace("create", "").strip()
        
        if not prompt:
            return {
                "reply": "🎨 Please describe what you'd like me to generate. For example: 'Generate an image of a sunset over mountains'"
            }
        
        logger.info(f"Generating image for prompt: {prompt}")
        
        # Generate image
        generator = get_image_generator()
        result = generator.generate_image(
            prompt=prompt,
            steps=4,  # Fast inference
            width=512,
            height=512,
            guidance_scale=0.0  # No guidance for speed
        )
        
        if result['status'] == 'success':
            return {
                "reply": f"✅ Generated 512x512 image!\n\n"
                        f"📸 Saved to: {result['image_path']}\n"
                        f"📝 Prompt: {result['prompt']}\n"
                        f"⚡ Generated in 4 steps using Stable Diffusion XL Turbo\n"
                        f"🖥️ Device: {result['device'].upper()}",
                "image_path": result['image_path']
            }
        else:
            return {
                "reply": f"❌ Image generation failed: {result['message']}"
            }
    
    except Exception as e:
        logger.error(f"Image generation skill error: {e}")
        return {
            "reply": f"Error generating image: {str(e)}\n\n"
                    f"Make sure you have the required libraries installed:\n"
                    f"`pip install diffusers torch`"
        }
