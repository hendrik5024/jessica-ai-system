"""
Phase 78 — Cognitive Engine

Executes thinking based on routing decision.
"""

import re

from jessica.core.cognitive_router import CognitiveRouter, CognitiveMode
from jessica.core.self_model import SelfModel
from jessica.core.introspection_engine import IntrospectionEngine
from jessica.core.explanation_engine import ExplanationEngine
from jessica.memory.memory_manager import MemoryManager
from jessica.tools.analysis.math_engine import evaluate
from jessica.tools.tool_registry import ToolRegistry

class CognitiveEngine:

    def __init__(self):
        self.router = CognitiveRouter()
        self.memory = MemoryManager()
        self.introspection = IntrospectionEngine()
        self.explainer = ExplanationEngine()
        self.tools = ToolRegistry()

    def think(self, user_input: str, llm_callable=None) -> str:

        user = user_input.lower()

        self_model = SelfModel()

        # Self-awareness interception — answer from ground truth, not LLM
        if "what are you" in user:
            return self._respond(self_model.identity)

        if "who are you" in user:
            return self._respond(self_model.identity)

        if "how do you work" in user:
            return self._respond(self_model.architecture)

        if "do you use a model" in user:
            return self._respond(self_model.model_usage)

        if "where do you run" in user or "where are you" in user:
            return self._respond(self_model.environment)

        if "what can you do" in user:
            return self._respond(
                "I can assist with reasoning, answering questions, and helping with tasks "
                "within my integrated capabilities."
            )

        if "limitations" in user:
            return self._respond(self_model.limitations)

        if "platform" in user:
            return self._respond("I run locally on your system.")

        # Introspection trigger
        if "why did you" in user or "explain yourself" in user:
            return self._respond(self.introspection.explain_last())

        # Feedback-driven correction
        if self.is_feedback(user_input):
            last = self.introspection.get_last_record()
            if last and last.get("intent") in {"calculation", "math"}:
                expression = self._extract_expression(last.get("input", ""))
                if not expression:
                    return self._respond("I could not correct the answer.")
                try:
                    result = evaluate(expression)
                    self.memory.store_fact(expression, result)
                    return self._respond(
                        f"You're right. Let me correct that. The answer is {result}."
                    )
                except Exception:
                    return self._respond("I could not correct the answer.")

        intent = self.classify_intent(user_input)
        if intent == "set_preference":
            self.memory.store("address_by_name", True)
            return self._respond("I will address you by your name.")

        if intent in {"store_name", "recall_name"}:
            return self._respond(self._handle_memory(user_input))

        # Tool check EARLY (before mode routing) so tools take priority
        tool = self.tools.find_tool(user_input)
        if tool:
            result = tool.execute(user_input)
            reasoning = "I used a calculation tool to evaluate the expression."
            self.introspection.record(
                input_text=user_input,
                intent="calculation",
                decision="tool_used",
                response=result,
                reasoning=reasoning,
            )
            return self._respond(result)

        # Standard routing after self-questions
        mode = self.router.classify(user_input)

        # MEMORY
        if mode == CognitiveMode.MEMORY:
            return self._respond(self._handle_memory(user_input))

        # IDENTITY
        if mode == CognitiveMode.IDENTITY:
            from jessica.identity.identity_core import IdentityCore
            return self._respond(IdentityCore().get_identity())

        # LOGIC
        if mode == CognitiveMode.LOGIC:
            return self._respond(self._handle_logic(user_input))

        # WORLD
        if mode == CognitiveMode.WORLD:
            return self._respond(self._handle_world(user_input))

        # Explanation request
        if "why" in user_input.lower() or "how" in user_input.lower():
            last = self.introspection.get_last_record()
            return self._respond(self.explainer.generate(last))

        # Model override for memory/calculation intents
        if self.is_memory_query(user_input):
            return self._respond(self._handle_memory(user_input))

        if self.is_calculation_query(user_input):
            return self._respond(self._handle_logic(user_input))

        # LLM fallback
        if mode == CognitiveMode.LLM and llm_callable:
            raw = llm_callable(user_input)

            from jessica.core.response_guard import ResponseGuard
            from jessica.core.reality_filter import RealityFilter

            guard = ResponseGuard()
            filtered = guard.enforce_identity(raw)

            reality = RealityFilter()
            final = reality.filter(user_input, filtered)

            reasoning = "The request was informational and safe to answer."
            self.introspection.record(
                input_text=user_input,
                intent="information_request",
                decision="answered",
                response=final,
                reasoning=reasoning,
            )

            return self._respond(final)

        reasoning = "The request could not be classified or understood."
        response = (
            "I do not have enough understanding to answer that directly. "
            "Could you rephrase your question or ask something clearer?"
        )
        self.introspection.record(
            input_text=user_input,
            intent="unknown",
            decision="insufficient_understanding",
            response=response,
            reasoning=reasoning,
        )
        return self._respond(response)

    # ---------------------
    # INTERNAL SYSTEMS
    # ---------------------

    def is_feedback(self, text: str) -> bool:
        triggers = ["wrong", "incorrect", "mistake", "try again"]
        return any(trigger in text.lower() for trigger in triggers)

    def is_memory_query(self, text: str) -> bool:
        lowered = text.lower()
        return "name" in lowered and "my" in lowered

    def is_calculation_query(self, text: str) -> bool:
        lowered = text.lower()
        if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", lowered):
            return True
        return any(token in lowered for token in ["calculate", "compute", "plus", "minus", "times", "divide"])

    def is_math_expression(self, text: str) -> bool:
        allowed = "0123456789+-*/(). "
        stripped = text.strip()
        if not stripped:
            return False
        return all(char in allowed for char in stripped)

    def classify_intent(self, text: str) -> str:
        lowered = text.lower()

        if "my name is" in lowered:
            return "store_name"

        if "address me by my name" in lowered:
            return "set_preference"

        if "my name" in lowered or "recall my name" in lowered:
            return "recall_name"

        if self.is_math_expression(lowered):
            return "math"

        return "general"

    def _respond(self, message: str) -> str:
        if self.memory.get("address_by_name"):
            name = self.memory.get("user_name")
            if name:
                return f"{name}, {message}"
        return message

    def _handle_memory(self, user_input: str) -> str:
        text = user_input.lower()

        if "my name is" in text:
            parts = text.split("my name is", 1)
            if len(parts) > 1:
                name = parts[1].strip()
                self.memory.store("user_name", name)
                return f"I will remember that your name is {name}."

        if "name" in text and "my" in text:
            name = self.memory.get("user_name")
            if name:
                return f"Your name is {name}."
            return "I do not know your name yet."

        return "I am not sure what to remember."

    def _handle_logic(self, user_input: str) -> str:
        try:
            expression = self._extract_expression(user_input)
            if not expression:
                return "I could not evaluate that expression. Please try a simpler calculation."
            result = evaluate(expression)
            return f"The answer is {result}."
        except Exception:
            reasoning = "The mathematical expression could not be evaluated."
            response = "I could not evaluate that expression. Please try a simpler calculation."
            self.introspection.record(
                input_text=user_input,
                intent="math",
                decision="failed_evaluation",
                response=response,
                reasoning=reasoning,
            )
            return response

    def _extract_expression(self, text: str) -> str:
        match = re.search(r"(\d[\d\s\+\-\*\/\(\)\.]*\d)", text)
        if not match:
            return ""
        return match.group(1)

    def _handle_world(self, user_input: str) -> str:
        text = user_input.lower()

        if "capital of france" in text:
            return "The capital of France is Paris."

        if "capital of germany" in text:
            return "The capital of Germany is Berlin."

        return "I do not have that knowledge yet."
