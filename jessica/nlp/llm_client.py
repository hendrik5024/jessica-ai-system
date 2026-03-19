# Placeholder remote LLM client adapter
from typing import List

class RemoteLLMClient:
    def __init__(self, provider: str = 'openai', api_key: str = None):
        self.provider = provider
        self.api_key = api_key

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        # TODO: integrate actual API call (opt-in)
        return f"(remote placeholder response to: {prompt[:50]})"
