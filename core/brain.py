import logging
from core.perception import Perception
from core.decision import DecisionEngine
from core.execution import ExecutionEngine
from core.reflection import Reflection
from memory.memory_manager import MemoryManager
from memory.learning_manager import LearningManager
from memory.feedback_manager import FeedbackManager
from memory.improvement_manager import ImprovementManager
from core.model_router import ModelRouter


logging.basicConfig(level=logging.INFO)


def handle_special_cases(user_input):
    text = user_input.lower()

    if "your name" in text or "who are you" in text:
        return "I am Jessica, your personal AI assistant created by Hendrik."

    if "who created you" in text:
        return "I was created by Hendrik."

    return None


class Brain:
    def __init__(self):
        self.perception = Perception()
        self.decision = DecisionEngine()
        self.execution = ExecutionEngine()
        self.reflection = Reflection()
        self.model_router = ModelRouter()
        self.learning = LearningManager()
        self.feedback = FeedbackManager()
        self.improvement = ImprovementManager()
        try:
            self.memory = MemoryManager()
        except Exception as e:
            logging.error(f"Memory initialization failed in Brain: {e}")
            self.memory = None

    def process(self, input_text: str) -> dict:
        raw_input = input_text
        context = {"intent": "unknown"}
        try:
            special_response = handle_special_cases(raw_input)

            if special_response:
                return {
                    "handled": True,
                    "response": special_response,
                    "intent": "identity"
                }

            learned = self.learning.get_learned_response(raw_input)

            if learned:
                return {
                    "handled": True,
                    "response": learned,
                    "intent": "learned"
                }

            recent = []
            try:
                if self.memory is not None:
                    recent = self.memory.get_recent(limit=5)
            except Exception as e:
                logging.error(f"Memory load failed in Brain: {e}")

            context = self.perception.process(raw_input)
            context["memory"] = recent
            intent = context["intent"]
            text = context["raw_input"]

            if context.get("confidence", 0.5) < 0.6:
                return {
                    "handled": True,
                    "response": "I'm not sure I understood. Can you rephrase?",
                    "intent": context.get("intent", "unknown")
                }

            action = self.decision.decide(context)
            result = self.execution.execute(action)

            if result == "I don't understand yet.":
                model_response = self.model_router.generate(intent, text)
                if model_response:
                    result = model_response

            self.reflection.process(context, action, result)

            success = result != "I don't understand yet."
            try:
                self.feedback.save_feedback(
                    context["raw_input"],
                    result,
                    success
                )
            except Exception as e:
                logging.error(f"Feedback save failed in Brain: {e}")

            try:
                suggestions = self.improvement.analyze_failures()
                self.improvement.auto_learn(self.learning)
                if suggestions:
                    print("[AUTO-LEARNING APPLIED]")
            except Exception as e:
                logging.error(f"Improvement analysis failed in Brain: {e}")

            if result is not None and result != "I don't understand yet.":
                try:
                    self.learning.save_pattern(raw_input, result)
                except Exception as e:
                    logging.error(f"Learning save failed in Brain: {e}")

            if not success:
                final_result = {
                    "handled": True,
                    "response": "I'm still learning. Can you rephrase that?",
                    "intent": context["intent"]
                }
            else:
                final_result = {
                    "handled": True,
                    "response": result,
                    "intent": context["intent"]
                }

            try:
                if self.memory is not None:
                    self.memory.save_interaction(
                        context["raw_input"],
                        context["intent"],
                        final_result.get("response")
                    )
            except Exception as e:
                logging.error(f"Memory save failed in Brain: {e}")

            return final_result

        except Exception as e:
            logging.error(f"Brain processing error: {e}")
            return {
                "handled": False,
                "response": None,
                "intent": context["intent"]
            }
