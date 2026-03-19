"""
Phase 87/90: Reasoning Engine

Structured reasoning methods for Jessica's cognitive core.
Phase 90: Model fallback gated through permission checks.
"""

import re
from datetime import datetime


class ReasoningEngine:
    """
    Provides structured reasoning capabilities.
    Phase 90: Permission-aware model fallback.
    """

    def __init__(self, permission_manager=None):
        self.permission_manager = permission_manager

    def calculate_age(self, birth_year, birth_month=None):
        """
        Calculate accurate age considering birth month.
        Returns integer age.
        """
        from datetime import datetime

        now = datetime.now()
        age = now.year - birth_year

        if birth_month:
            if now.month < birth_month:
                age -= 1

        return age

    def resolve_personal_question(self, text: str, knowledge_store):
        """
        Resolve personal questions using stored knowledge.
        Returns answer or None.
        """
        text_lower = text.lower()

        # Name recall
        if "what is my name" in text_lower or "my name" in text_lower:
            name = knowledge_store.get_fact("user.name")
            if name:
                return f"Your name is {name}."
            return "I do not know your name yet."

        # Age calculation
        if "how old am i" in text_lower or "how old" in text_lower:
            birth_year = knowledge_store.get_fact("user.birth_year")
            if birth_year:
                birth_month = knowledge_store.get_fact("user.birth_month")
                age = self.calculate_age(birth_year, birth_month)
                return f"You are {age} years old."
            return "I do not know your age yet."

        # Location
        if "where do i live" in text_lower:
            location = knowledge_store.get_fact("user.location")
            if location:
                return f"You live in {location}."
            return "I do not know where you live."

        return None

    def resolve_math(self, text: str):
        """
        Safely evaluate basic math expressions.
        Returns result or None.
        """
        # Extract mathematical expressions
        # Pattern must contain at least one digit and operator
        candidates = []
        
        # Pattern 1: expressions with parentheses like (10+5)*2
        match = re.search(r"\([0-9+\-*/. ]+\)[*+\-/][0-9.]+", text)
        if match:
            candidates.append(match.group().strip())
        
        # Pattern 2: simple numeric expressions (at least digit+operator+digit)
        match = re.search(r"[0-9]+(?:[. ]*[+\-*/][. ]*[0-9()]+)+", text)
        if match:
            candidates.append(match.group().strip())
        
        # Use the longest candidate (most complete expression)
        if not candidates:
            return None
        
        expression = max(candidates, key=len)

        # Sanitize: only allow safe characters
        if not re.match(r"^[0-9+\-*/(). ]+$", expression):
            return None

        try:
            # Safe evaluation
            result = eval(expression, {"__builtins__": None}, {})
            return f"The answer is {result}."
        except Exception:
            return None

    def resolve_age(self, knowledge_store):
        """
        Resolve user's age from birth year and month.
        Returns answer or None.
        """
        birth_year = knowledge_store.get_birth_year()
        if not birth_year:
            return None

        birth_month = knowledge_store.get_fact("user.birth_month")
        age = self.calculate_age(birth_year, birth_month)

        return f"You are {age} years old."

    def resolve_name(self, knowledge_store):
        """
        Resolve user's name from memory.
        Returns answer or None.
        """
        name = knowledge_store.get_user_name()
        if name:
            return f"Your name is {name}."
        return None

    def resolve_birth_year(self, knowledge_store):
        """
        Resolve user's birth year from memory.
        Returns answer or None.
        """
        year = knowledge_store.get_birth_year()
        if year:
            return f"You were born in {year}."
        return None

    def resolve_identity(self, text: str, knowledge_store=None):
        """
        Resolve Jessica's identity questions.
        Returns structured answer.
        """
        text_lower = text.lower()

        # What are you
        if "what are you" in text_lower:
            return "I am Jessica, a cognitive AI system that reasons, remembers, and assists."

        # Who created you
        if "who created you" in text_lower:
            if knowledge_store:
                name = knowledge_store.get_user_name()
                if name:
                    return f"You created me, {name}."
            return "I was created by my developer."

        # What is your name
        if "what is your name" in text_lower:
            return "My name is Jessica."

        return None

    def resolve_identity_question(self, text: str, knowledge_store=None):
        """
        Handle identity-related questions.
        Returns structured answer.
        """
        text_lower = text.lower()

        # Creator
        if "who created you" in text_lower:
            if knowledge_store:
                creator = knowledge_store.get_fact("jessica.creator")
                if creator:
                    return f"You created me, {creator}."
            return "You created me."

        # Jessica's name
        if "your name" in text_lower or "what are you called" in text_lower:
            return "My name is Jessica."

        # What are you
        if "what are you" in text_lower:
            return "I am Jessica, a cognitive AI system designed to reason, remember, and assist."

        return None

    def fallback_with_model(self, text: str, model):
        """
        Query the model as a knowledge tool.
        Phase 90: Requires code_execution permission.
        Returns model response as structured data (not directly to user).
        """
        if not model:
            return None

        if self.permission_manager:
            self.permission_manager.require("code_execution")

        model_answer = self._ask_model(text)
        
        # Return structured response - Jessica controls presentation
        if model_answer:
            return {
                "type": "model_assisted",
                "model_answer": model_answer,
            }
        return None

    def _ask_model(self, text: str) -> str:
        """
        Get model's answer to a question.
        Phase 96: Used for fallback knowledge when Jessica's structured reasoning fails.
        
        Args:
            text: User question
            
        Returns:
            Model's answer or generic fallback
        """
        if not self.model:
            return "I could not retrieve external knowledge."
        
        try:
            return self.model.generate(text)
        except Exception:
            return "I could not retrieve external knowledge."
    
    @property
    def model(self):
        """Get model instance if available."""
        # This will be set by CognitiveKernel during initialization
        return getattr(self, "_model", None)
    
    @model.setter
    def model(self, value):
        """Set model instance."""
        self._model = value
