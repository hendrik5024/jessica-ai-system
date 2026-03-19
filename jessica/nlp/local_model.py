# Placeholder local model wrapper (e.g., small conversational model)
class LocalChatModel:
    def __init__(self, model_name: str = 'dialo-gpt-small'):
        self.model_name = model_name

    def chat(self, history):
        # TODO: integrate huggingface local inference offline
        last = history[-1] if history else {'text': ''}
        return f"(local placeholder reply to: {last.get('text','')[:60]})"
