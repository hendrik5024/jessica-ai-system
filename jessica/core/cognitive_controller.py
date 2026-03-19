"""
Phase 87/89/91: Cognitive Controller

Central controller where Jessica makes all decisions.
The model is only an advisory tool.
Phase 89: Now stores all interactions for persistent learning.
Phase 91: Uses internal belief system for identity consistency.
"""

import re
from jessica.core.self_correction import SelfCorrectionEngine


class CognitiveController:
    """
    Jessica's cognitive control layer.
    All responses originate from Jessica.
    Phase 89: Tracks interactions for learning.
    Phase 91: Uses beliefs for consistent identity.
    """

    def __init__(self, knowledge_store, reasoning_engine, model=None, belief_store=None, belief_reasoner=None):
        self.knowledge_store = knowledge_store
        self.reasoning_engine = reasoning_engine
        self.model = model
        self.belief_store = belief_store
        self.belief_reasoner = belief_reasoner
        self.self_correction_engine = SelfCorrectionEngine(knowledge_store)
        
        # Pass model to reasoning engine for fallback
        if model:
            self.reasoning_engine.model = model

    def process(self, text: str) -> str:
        """
        Main processing flow.
        Jessica controls all responses.
        
        Order: correction check → memory store → personal queries → identity → math → model fallback (STRICT)
        Phase 89: Stores all interactions after response generation.
        """
        text_lower = text.lower()

        # STEP 0: Self-correction check (before all processing)
        correction = self.self_correction_engine.check(text)
        if correction:
            self.store_interaction(text, correction)
            self.self_correction_engine.update_last_response(correction)
            return correction

        # STEP 0.5: "What do you know about me" query (Phase 89)
        if "what do you know about me" in text_lower:
            response = self._summarize_knowledge()
            self.store_interaction(text, response)
            self.self_correction_engine.update_last_response(response)
            return response

        # STEP 1: Birth year storage with response and consistency check
        if "born" in text_lower:
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
            month_match = re.search(
                r"(january|february|march|april|may|june|july|august|september|october|november|december)",
                text_lower
            )

            if year_match:
                year = int(year_match.group(0))
                
                # Consistency check before storing
                consistency_warning = self.self_correction_engine.check_consistency(
                    "user.birth_year", year, text
                )
                if consistency_warning:
                    self.store_interaction(text, consistency_warning)
                    self.self_correction_engine.update_last_response(consistency_warning)
                    return consistency_warning

                self.knowledge_store.set_fact("user.birth_year", year)

                if month_match:
                    month_map = {
                        "january": 1, "february": 2, "march": 3, "april": 4,
                        "may": 5, "june": 6, "july": 7, "august": 8,
                        "september": 9, "october": 10, "november": 11, "december": 12
                    }
                    month = month_map[month_match.group(0)]
                    self.knowledge_store.set_fact("user.birth_month", month)

                response = "I will remember your birth information."
                self.store_interaction(text, response)
                self.self_correction_engine.update_last_response(response)
                return response

        # STEP 2: Memory extraction (for other patterns)
        self._extract_memory(text)

        # STEP 3: Birth year query
        if "when was i born" in text_lower or "what year was i born" in text_lower:
            result = self.reasoning_engine.resolve_birth_year(self.knowledge_store)
            if result:
                self.store_interaction(text, result)
                self.self_correction_engine.update_last_response(result)
                return result
            response = "I do not know your birth year yet."
            self.store_interaction(text, response)
            self.self_correction_engine.update_last_response(response)
            return response

        # STEP 4: Jessica's age question (before personal questions to avoid confusion)
        if "how old are you" in text_lower:
            response = "I do not have an age like a human. I am a cognitive system."
            self.store_interaction(text, response)
            self.self_correction_engine.update_last_response(response)
            return response

        # STEP 5: Personal questions (name recall, user age, location, etc.)
        # Phase 91: Check beliefs first, then fall back to reasoning engine
        personal_answer = None
        
        if self.belief_reasoner:
            # Try to answer from beliefs
            if "what is my name" in text_lower or "my name" in text_lower:
                name = self.belief_reasoner.resolve("user_name")
                if name:
                    personal_answer = f"Your name is {name}."
            
            elif "how old am i" in text_lower:
                birth_year = self.belief_reasoner.resolve("user_birth_year")
                if birth_year:
                    from datetime import datetime
                    age = datetime.now().year - int(birth_year)
                    birth_month = self.belief_reasoner.resolve("user_birth_month")
                    if birth_month:
                        if datetime.now().month < int(birth_month):
                            age -= 1
                    personal_answer = f"You are {age} years old."
            
            elif "where do i live" in text_lower or "where do you live" in text_lower:
                location = self.belief_reasoner.resolve("user_location")
                if location:
                    personal_answer = f"You live in {location}."
        
        # Fall back to reasoning engine if belief didn't answer
        if not personal_answer:
            personal_answer = self.reasoning_engine.resolve_personal_question(
                text, self.knowledge_store
            )
        
        if personal_answer:
            self.store_interaction(text, personal_answer)
            self.self_correction_engine.update_last_response(personal_answer)
            return personal_answer

        # STEP 6: Identity questions
        # Phase 91: Check beliefs for creator information
        identity_answer = None
        
        if self.belief_reasoner:
            if "who created you" in text_lower:
                creator = self.belief_reasoner.resolve("creator")
                if creator:
                    identity_answer = f"You created me, {creator}."
        
        # Fall back to reasoning engine
        if not identity_answer:
            identity_answer = self.reasoning_engine.resolve_identity(
                text, self.knowledge_store
            )
        
        if identity_answer:
            self.store_interaction(text, identity_answer)
            self.self_correction_engine.update_last_response(identity_answer)
            return identity_answer

        # STEP 7: Math reasoning
        math_answer = self.reasoning_engine.resolve_math(text)
        if math_answer:
            self.store_interaction(text, math_answer)
            self.self_correction_engine.update_last_response(math_answer)
            return math_answer

        # STEP 8: Age reasoning (user age)
        if "how old am i" in text_lower:
            age_answer = self.reasoning_engine.resolve_age(self.knowledge_store)
            if age_answer:
                self.store_interaction(text, age_answer)
                self.self_correction_engine.update_last_response(age_answer)
                return age_answer
            response = "I do not know your age yet."
            self.store_interaction(text, response)
            self.self_correction_engine.update_last_response(response)
            return response

        # STEP 9: STRICT MODEL GATE - only for knowledge questions
        # Do NOT use model for name, age, birth, identity
        model_blocked_keywords = ["my name", "your name", "how old", "born", "who created", "what are you"]
        if any(keyword in text_lower for keyword in model_blocked_keywords):
            response = "I am not sure yet, but I can try to learn or find out."
            self.store_interaction(text, response)
            self.self_correction_engine.update_last_response(response)
            return response

        # STEP 10: Model fallback (only for knowledge questions)
        if self.model:
            print("⚠️ Model fallback used")
            result = self.reasoning_engine.fallback_with_model(
                text, self.model
            )
            if result and result.get("type") == "model_assisted":
                # Jessica uses external knowledge but maintains control
                response = {
                    "response": f"I used external knowledge to answer: {result['model_answer']}",
                    "model_assisted": True,
                    "model_knowledge": result["model_answer"]
                }
                self.store_interaction(text, response.get("response"))
                self.self_correction_engine.update_last_response(response.get("response"))
                return response

        # STEP 11: Final fallback
        response = "I am not sure yet, but I can try to learn or find out."
        self.store_interaction(text, response)
        self.self_correction_engine.update_last_response(response)
        return response
        return response

    def _extract_memory(self, text: str):
        """Extract and store user information from input."""
        text_lower = text.lower()

        # Name extraction (case-insensitive search)
        if "my name is" in text_lower:
            # Find the position and extract from original text
            idx = text_lower.find("my name is")
            if idx >= 0:
                name = text[idx + len("my name is"):].strip().title()
                if name:
                    self.knowledge_store.set_fact("user.name", name)

        # Birth year extraction
        if "born" in text_lower:
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
            if year_match:
                year = int(year_match.group(0))
                self.knowledge_store.set_fact("user.birth_year", year)

    def _wrap_model_knowledge(self, model_response: str) -> str:
        """
        Process model response.
        Return clean response without wrapper (natural output).
        """
        # Clean the response
        cleaned = model_response.strip()

        # Check for identity leaks
        forbidden = ["i am phi", "language model", "assistant:", "openai", "microsoft"]
        lower = cleaned.lower()

        for phrase in forbidden:
            if phrase in lower:
                return "I am Jessica."

        # Return clean model response (no wrapper)
        return cleaned

    def store_interaction(self, user_input, response):
        """
        Store interaction history for learning.
        Phase 89: Persisted to JSON with safety limits.
        """
        history = self.knowledge_store.get_fact("history") or []
        
        history.append({
            "input": user_input,
            "response": response
        })
        
        # Safety limit: max 50 interactions
        history = history[-50:]
        
        self.knowledge_store.set_fact("history", history)

    def _summarize_knowledge(self):
        """
        Summarize what Jessica knows about the user.
        Phase 89: New feature for memory recall.
        """
        name = self.knowledge_store.get_fact("user.name")
        birth_year = self.knowledge_store.get_fact("user.birth_year")
        birth_month = self.knowledge_store.get_fact("user.birth_month")
        location = self.knowledge_store.get_fact("user.location")
        
        facts = []
        
        if name:
            facts.append(f"your name is {name}")
        
        if birth_year:
            if birth_month:
                month_names = ["", "January", "February", "March", "April", "May", 
                              "June", "July", "August", "September", "October", 
                              "November", "December"]
                month_name = month_names[birth_month]
                facts.append(f"you were born in {month_name} {birth_year}")
            else:
                facts.append(f"you were born in {birth_year}")
        
        if location:
            facts.append(f"you live in {location}")
        
        if not facts:
            return "I do not know much about you yet. Tell me about yourself!"
        
        if len(facts) == 1:
            return f"I know that {facts[0]}."
        
        if len(facts) == 2:
            return f"I know that {facts[0]} and {facts[1]}."
        
        return f"I know that {', '.join(facts[:-1])}, and {facts[-1]}."
