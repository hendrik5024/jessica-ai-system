"""
Phase 98.5: Personal Question Detection

Identifies personal/identity questions that should use memory/beliefs first,
NOT model fallback.
"""


class PersonalQuestionDetector:
    """
    Detects personal and identity questions that require belief store access.
    
    These questions must ALWAYS use memory/beliefs, never be answered by model.
    """

    # Keywords indicating personal questions
    PERSONAL_KEYWORDS = [
        # Name questions
        "my name",
        "who am i",
        "my full name",
        "call me",
        
        # Creator/origin questions
        "who created you",
        "who made you",
        "who built you",
        "who coded you",
        "who developed you",
        "who created jessica",
        "creator",
        
        # Age/birth questions
        "my age",
        "how old am i",
        "when was i born",
        "birth year",
        
        # Knowledge about user
        "do you know me",
        "about me",
        "tell me about myself",
        "what do you know about me",
        "remember me",
        
        # Location
        "where do i live",
        "my location",
        "my home",
        
        # Identity affirmations
        "i am",
        "you are",
        "i'm your",
        "i created you",
        "i made you",
        "i built you",
        "i coded you",
        "i developed you",
    ]

    # Keywords indicating external knowledge questions (NOT personal)
    EXTERNAL_KEYWORDS = [
        "what is",
        "who was",
        "when did",
        "how does",
        "explain",
        "calculate",
        "math",
        "define",
        "example",
        "capital of",
        "president of",
        "formula for",
        "distance between",
    ]

    @staticmethod
    def is_personal_question(text: str) -> bool:
        """
        Determine if question is personal/identity-related.
        
        Personal questions should ALWAYS use belief store first,
        never be answered directly by model.
        
        Args:
            text: User input text
            
        Returns:
            True if personal question, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        lowered = text.lower().strip()
        
        # Check if it's a personal question
        is_personal = any(keyword in lowered for keyword in PersonalQuestionDetector.PERSONAL_KEYWORDS)
        
        # Even if it matches personal keywords, check if it's really external knowledge
        # e.g., "What is my name?" contains "my name" but asks for external knowledge
        is_external = any(keyword in lowered for keyword in PersonalQuestionDetector.EXTERNAL_KEYWORDS)
        
        # If it contains both, be conservative - treat as personal
        # (because personal questions are sensitive)
        if is_personal and is_external:
            return True
        
        return is_personal

    @staticmethod
    def is_identity_update(text: str) -> bool:
        """
        Determine if user is providing identity information.
        
        Examples:
        - "My name is Hendrik"
        - "I created you"
        - "I was born in 1995"
        
        Args:
            text: User input text
            
        Returns:
            True if providing identity info, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        lowered = text.lower().strip()
        
        identity_patterns = [
            "my name is",
            "i am",
            "i created",
            "i made",
            "i built",
            "i coded",
            "i was born",
            "born in",
            "i live in",
            "i'm your",
            "i'm the one",
        ]
        
        return any(pattern in lowered for pattern in identity_patterns)

    @staticmethod
    def classify_question(text: str) -> str:
        """
        Classify the type of question.
        
        Returns: "personal", "identity_update", "math", "external_knowledge", "other"
        """
        if PersonalQuestionDetector.is_identity_update(text):
            return "identity_update"
        elif PersonalQuestionDetector.is_personal_question(text):
            return "personal"
        elif any(kw in text.lower() for kw in ["what is", "calculate", "solve", "+", "-", "*", "/"]):
            return "math"
        elif any(kw in text.lower() for kw in PersonalQuestionDetector.EXTERNAL_KEYWORDS):
            return "external_knowledge"
        else:
            return "other"
