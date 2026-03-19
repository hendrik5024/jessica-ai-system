from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelInterface:
    _shared_model = None
    _shared_tokenizer = None
    _load_attempted = False

    def __init__(self):
        if ModelInterface._shared_model is not None and ModelInterface._shared_tokenizer is not None:
            self.model = ModelInterface._shared_model
            self.tokenizer = ModelInterface._shared_tokenizer
            return

        if ModelInterface._load_attempted:
            self.model = None
            self.tokenizer = None
            return

        ModelInterface._load_attempted = True
        print("[MODEL] Loading local model...")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            self.model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            ModelInterface._shared_model = self.model
            ModelInterface._shared_tokenizer = self.tokenizer
            print("[MODEL] Loaded successfully")
        except Exception as e:
            print("[MODEL ERROR]", e)
            self.model = None
            self.tokenizer = None

    def generate(self, user_input):
        if not self.model or not self.tokenizer:
            return "Model not available."

        try:
            system_prompt = """You are Jessica, a personal AI assistant created by Hendrik.

Rules:
- Always answer as Jessica
- Be helpful, clear, and concise
- Do NOT invent commands or features
- If unsure, say "I'm still learning"
- Never create fake conversations
- Never include 'User:' or 'Jessica:' in your answer
- Keep answers short unless asked for detail

Identity:
- Creator: Hendrik
- Name: Jessica
- Purpose: Assist with information, coding, and reasoning
"""

            prompt = f"{system_prompt}\nUser: {user_input}\nJessica:"

            inputs = self.tokenizer(prompt, return_tensors="pt")

            outputs = self.model.generate(
                inputs["input_ids"],
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove prompt part
            if "Jessica:" in response:
                response = response.split("Jessica:")[-1]

            # Stop model continuing conversation
            if "User:" in response:
                response = response.split("User:")[0]

            response = response.replace("for I in range(", "for i in range(")

            response = response.strip()

            if not response:
                response = "I'm still learning."

            print(f"[MODEL OUTPUT] {response}")

            return response

        except Exception as e:
            return f"[MODEL ERROR] {e}"


class ModelTool(ModelInterface):
    pass
