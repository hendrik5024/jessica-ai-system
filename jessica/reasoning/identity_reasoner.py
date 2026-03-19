"""
Phase 98.9: Identity Reasoning Engine

Moves from simple memory retrieval to intelligent identity reasoning.
Jessica now links facts together, answers consistently, speaks naturally,
and resolves conflicts about who she is and who you are.
"""

from typing import Optional


class IdentityReasoner:
    """
    Reasons about identity using stored beliefs.
    
    Transforms simple facts into coherent, natural responses that show
    understanding of the relationships between beliefs.
    
    Examples:
    - Belief: "user_name" = "Alice"
    - Question: "Who am I?"
    - Answer: "You are Alice" (not just retrieval, but reasoning)
    """
    
    def __init__(self, belief_store):
        """
        Initialize with reference to the belief store.
        
        Args:
            belief_store: BeliefStore instance containing identity facts
        """
        self.beliefs = belief_store
    
    def answer(self, question: str) -> Optional[str]:
        """
        Reason about identity based on stored beliefs.
        
        Args:
            question: User's question about identity
            
        Returns:
            Natural language answer if able to reason, None otherwise
        """
        if not question:
            return None
        
        q = question.lower().strip()
        
        # Get key beliefs
        user_name = self.beliefs.get("user_name")
        creator = self.beliefs.get("creator")
        birth_year = self.beliefs.get("birth_year")
        profession = self.beliefs.get("profession")
        interest = self.beliefs.get("interest")
        
        # ===== WHO CREATED YOU =====
        if any(phrase in q for phrase in ["who created you", "who made you", "who coded you", 
                                          "who built you", "who developed you"]):
            if creator:
                return f"You created me, {creator}."
            return "I am not sure who created me yet."
        
        # ===== WHO ARE YOU / WHAT IS YOUR NAME =====
        if any(phrase in q for phrase in ["who are you", "what is your name", "your name"]):
            return "I am Jessica."
        
        # ===== WHO AM I / WHAT IS MY NAME =====
        if any(phrase in q for phrase in ["who am i", "what is my name", "my name", "identify me"]):
            if user_name:
                return f"You are {user_name}."
            return "I do not know who you are yet."
        
        # ===== DO YOU KNOW ME =====
        if any(phrase in q for phrase in ["do you know me", "do you remember me", "know who i am"]):
            if user_name:
                return f"Yes, I know you. You are {user_name}."
            return "I do not know you yet."
        
        # ===== TELL ME ABOUT MYSELF =====
        if any(phrase in q for phrase in ["tell me about me", "describe me", "what do you know about me"]):
            facts = []
            if user_name:
                facts.append(f"Your name is {user_name}")
            if birth_year:
                from datetime import datetime
                age = datetime.now().year - birth_year
                facts.append(f"You were born in {birth_year} (you are {age} years old)")
            if profession:
                facts.append(f"You are a {profession.lower()}")
            if interest:
                facts.append(f"You enjoy {interest.lower()}")
            if creator and user_name and creator == user_name:
                facts.append("You created me")
            
            if facts:
                return "Here is what I know about you: " + ", and ".join(facts) + "."
            return "I do not know much about you yet."
        
        # ===== HOW OLD AM I / WHEN WAS I BORN =====
        if any(phrase in q for phrase in ["how old am i", "my age", "when was i born", "when do i turn"]):
            if birth_year:
                from datetime import datetime
                age = datetime.now().year - birth_year
                return f"You are {age} years old, born in {birth_year}."
            return "I do not know your birth year yet."
        
        # ===== WHAT DO I DO / MY JOB =====
        if any(phrase in q for phrase in ["what do i do", "my job", "my profession", "my career", "what is my job"]):
            if profession:
                return f"You are a {profession}."
            return "I do not know your profession yet."
        
        # ===== WHAT DO I LIKE / MY INTERESTS =====
        if any(phrase in q for phrase in ["what do i like", "my interest", "what am i interested in", "what do i enjoy"]):
            if interest:
                return f"You enjoy {interest}."
            return "I do not know your interests yet."
        
        # ===== SUMMARIZE OUR RELATIONSHIP =====
        if any(phrase in q for phrase in ["our relationship", "tell me about us", "what's our connection"]):
            if user_name and creator and creator == user_name:
                return f"You are {user_name}, and you created me. We have a creator-assistant relationship."
            elif user_name:
                return f"You are {user_name}. I am your assistant, Jessica."
            elif creator:
                return f"You created me, {creator}. I am your assistant, Jessica."
            return "I am Jessica, your assistant."
        
        # ===== NOT AN IDENTITY QUESTION =====
        return None
    
    def has_identity_question(self, question: str) -> bool:
        """
        Check if a question is about identity.
        
        More specific than just checking for keywords to avoid false positives.
        
        Args:
            question: User's question
            
        Returns:
            True if this is an identity question
        """
        if not question:
            return False
        
        q = question.lower().strip()
        
        # Explicit identity question patterns
        identity_patterns = [
            # Who created you questions
            "who created you", "who made you", "who coded you", "who built you", "who developed you",
            "who created jessica", "who made jessica",
            # Who are you questions
            "who are you", "who am i", "what is my name", "what's my name",
            "tell me who i am", "tell me about me", "describe me",
            # Age/birth questions
            "how old am i", "what's my age", "when was i born", "when was i born", "my birth year",
            # Profession questions
            "what do i do", "what's my job", "what is my profession", "what do i do for work",
            # Interest questions
            "what do i like", "what are my interests", "what do you know about me",
            # Relationship questions
            "what's our relationship", "tell me about our relationship", "how do you know me",
            # Existence questions
            "do you know me", "have we met before", "do i know you"
        ]
        
        return any(pattern in q for pattern in identity_patterns)
    
    def explain_reasoning(self, question: str) -> Optional[str]:
        """
        Explain how the reasoner arrived at an answer.
        Useful for debugging and transparency.
        
        Args:
            question: User's question
            
        Returns:
            Explanation of reasoning process
        """
        if not question:
            return None
        
        q = question.lower()
        
        user_name = self.beliefs.get("user_name")
        creator = self.beliefs.get("creator")
        
        if "who am i" in q or "what is my name" in q:
            if user_name:
                return f"I know your name is {user_name}, so I answer: 'You are {user_name}'"
            else:
                return "I do not have your name in my beliefs, so I say I don't know"
        
        if "who created you" in q:
            if creator:
                return f"I know from beliefs that {creator} created me"
            else:
                return "I have no creator information stored"
        
        return None
