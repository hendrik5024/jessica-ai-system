"""
Phase 88/89: Self-Correction Engine

Enables Jessica to detect and correct mistakes.
Phase 89: Now tracks corrections in persistent memory.
"""


class SelfCorrectionEngine:
    """
    Monitors for correction signals and inconsistencies.
    Phase 89: Stores corrections for learning.
    """

    def __init__(self, knowledge_store=None):
        self.knowledge_store = knowledge_store
        self.last_response = None  # Track last response for feedback

    def check(self, user_input, response=None):
        """
        Check if user is indicating a mistake or correction needed.
        Returns correction message or None.
        """
        user_lower = user_input.lower()

        # Direct correction signals
        if "incorrect" in user_lower or "that's incorrect" in user_lower:
            self.learn_from_feedback(user_input, self.last_response)
            return "Let me review that."

        if "wrong" in user_lower or "that's wrong" in user_lower:
            self.learn_from_feedback(user_input, self.last_response)
            return "I may have made a mistake. Let me correct that."

        if "no that's not right" in user_lower or "not right" in user_lower:
            self.learn_from_feedback(user_input, self.last_response)
            return "I apologize. Let me reconsider."

        return None

    def learn_from_feedback(self, user_input, last_response):
        """
        Store correction feedback for learning.
        Phase 89: Persists corrections to JSON.
        """
        if not self.knowledge_store:
            return

        if not last_response:
            return

        corrections = self.knowledge_store.get_fact("corrections") or []
        
        corrections.append({
            "user_feedback": user_input,
            "last_response": last_response
        })
        
        # Safety limit: max 100 corrections
        corrections = corrections[-100:]
        
        self.knowledge_store.set_fact("corrections", corrections)

    def update_last_response(self, response):
        """Track the last response for feedback correlation."""
        self.last_response = response

    def check_consistency(self, key, new_value, user_input):
        """
        Check if new information conflicts with stored memory.
        Returns warning message or None.
        """
        if not self.knowledge_store:
            return None

        existing = self.knowledge_store.get_fact(key)
        
        # No conflict if nothing stored
        if existing is None:
            return None

        # Check for conflict
        if existing != new_value:
            # Age consistency check
            if key == "user.birth_year":
                from datetime import datetime
                current_year = datetime.now().year
                
                # If user says age, calculate what birth year should be
                if "years old" in user_input.lower() or "i am" in user_input.lower():
                    # Extract potential age number
                    import re
                    age_match = re.search(r"\b(\d{1,3})\b", user_input)
                    if age_match:
                        claimed_age = int(age_match.group(0))
                        expected_year = current_year - claimed_age
                        
                        # Allow 1 year variance for birthday timing
                        if abs(existing - expected_year) > 1:
                            return f"That seems inconsistent with what I know (born {existing}). Can you confirm?"

            # General conflict
            return f"That conflicts with what I remember ({existing}). Should I update this?"

        return None
