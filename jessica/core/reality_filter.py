"""
Reality Filter

Ensures responses match actual system capabilities.
Prevents hallucinations.
"""

from jessica.core.capabilities import CapabilityRegistry


class RealityFilter:

    def __init__(self):
        self.cap = CapabilityRegistry()

    def filter(self, user_input: str, response: str) -> str:
        text = response.lower()

        # Web access
        if "web" in text or "internet" in text:
            if not self.cap.has("has_web_access"):
                return "I do not have direct access to the internet. I rely on my internal knowledge and tools."

        # Camera
        if "camera" in text or "webcam" in text:
            if not self.cap.has("has_camera_access"):
                return "I cannot access your camera. I operate within controlled permissions."

        # Files
        if "files" in text or "laptop" in text:
            if not self.cap.has("has_file_access"):
                return "I do not access your files directly unless explicitly integrated to do so."

        # Model awareness
        if "model" in text:
            if self.cap.has("uses_llm"):
                return "I use language models as tools, but I am governed by my own cognitive architecture."

        # Platform hallucination
        if "platform" in text:
            return "I run locally on your system."

        # Experience hallucination
        if "i have experience" in text or "i have done this before" in text:
            return "I do not have personal experience. I operate based on programmed capabilities."

        # Assistant hallucination
        if "assistant" in text:
            return "I am Jessica, a cognitive AI system designed to assist you."

        return response
