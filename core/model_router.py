class ModelRouter:
    def __init__(self):
        from models.model_interface import ModelInterface

        print("[ROUTER] Initializing models...")

        # FAST model (always available)
        self.fast_model = ModelInterface()

        # LOGIC model (Mistral)
        self.logic_model = None

        # CODE model (CodeLlama)
        self.code_model = None

        print("[ROUTER] Fast model ready")

    def route(self, intent, text):
        """
        Decide which model to use
        """

        # No model needed
        if intent in ["get_time", "get_date", "identity"]:
            return None

        # Coding tasks
        if any(word in text.lower() for word in ["code", "python", "program"]):
            print("[ROUTER] Using CODE model")
            return self.code_model or self.fast_model

        # Reasoning tasks
        if any(word in text.lower() for word in ["why", "how", "explain"]):
            print("[ROUTER] Using LOGIC model")
            return self.logic_model or self.fast_model

        # Default
        print("[ROUTER] Using FAST model")
        return self.fast_model

    def generate(self, intent, text):
        model = self.route(intent, text)

        if model is None:
            return None

        return model.generate(text)