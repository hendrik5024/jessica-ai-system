from jessica.llm.llm_interface import LLMInterface


class LLMRouter:
    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def should_use_llm(self, user_input: str) -> bool:
        """
        Determine if the LLM should be used.
        Use LLM if:
        - general knowledge question
        - math question
        - explanation request
        """
        keywords = ["what", "why", "how", "explain", "who", "when", "where"]
        return any(k in user_input.lower() for k in keywords)

    def generate(self, user_input: str) -> str:
        return self.llm.generate(user_input)
