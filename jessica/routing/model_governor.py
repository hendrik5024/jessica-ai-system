"""
Phase 98.5/98.6: Model Governor

Ensures model is only used appropriately:
- NEVER overrides beliefs
- NEVER answers personal questions
- ALWAYS outputs are wrapped
- Conflicts are logged
- Phase 98.6: Model output sanitized (removes identity claims)
"""

from typing import Dict, Optional, Any
from jessica.security.audit_log import AuditLog
from jessica.routing.model_output_sanitizer import ModelOutputSanitizer


class ModelGovernor:
    """
    Governs model behavior to prevent it from overriding Jessica's beliefs
    or answering questions it shouldn't.
    
    Rules:
    1. Model CANNOT answer personal/identity questions
    2. Model answers are ALWAYS wrapped
    3. Model answers conflicting with beliefs are REJECTED
    4. All conflicts logged for audit trail
    """

    def __init__(self, audit_log: Optional[AuditLog] = None):
        self.audit_log = audit_log or AuditLog()
        self.sanitizer = ModelOutputSanitizer()
        self.forbidden_topics = [
            "who is jessica",
            "i am phi",
            "jessica is phi",
            "who created jessica",
            "who made jessica",
            "who built jessica",
        ]

    def can_answer_this_question(self, question: str) -> bool:
        """
        Check if model is allowed to answer this question.
        
        Model is NOT allowed to answer:
        - Identity questions (who created you, who are you)
        - Personal memory (my name, my age)
        - Questions directly about Jessica's creation
        
        Args:
            question: User question
            
        Returns:
            True if model allowed, False if blocked
        """
        lowered = question.lower()
        
        # Forbidden topics - model never answers these
        for topic in self.forbidden_topics:
            if topic in lowered:
                return False
        
        forbidden_patterns = [
            "who created you",
            "who made you",
            "who built you",
            "who coded you",
            "who developed you",
            "who created jessica",
            "who are you",
            "what are you",
            "who is jessica",
            "my name",
            "who am i",
            "my age",
            "when was i born",
            "i created you",
            "i made you",
            "i built you",
        ]
        
        return not any(pattern in lowered for pattern in forbidden_patterns)

    def check_conflict(self, model_answer: str, belief_answer: str, question: str) -> bool:
        """
        Check if model answer conflicts with stored belief.
        
        Args:
            model_answer: Answer from model
            belief_answer: Answer from belief store
            question: Original question
            
        Returns:
            True if conflict detected, False if consistent
        """
        if not belief_answer or not model_answer:
            return False
        
        # Normalize for comparison
        model_norm = model_answer.lower().strip()
        belief_norm = belief_answer.lower().strip()
        
        # Direct conflict: belief not in model answer
        if belief_norm not in model_norm:
            # Log conflict
            self.audit_log.record("belief_model_conflict", "conflict_detected", {
                "question": question,
                "belief": belief_answer,
                "model": model_answer,
                "action": "belief_preferred"
            })
            return True
        
        return False

    def wrap_model_output(self, model_answer: str, question: str) -> str:
        """
        Wrap model output to indicate it's external knowledge, not Jessica's authorship.
        Phase 98.6: Sanitize to remove identity claims first.
        
        Args:
            model_answer: Raw model output
            question: Question asked
            
        Returns:
            Wrapped output indicating external knowledge source, or None if discarded
        """
        if not model_answer:
            return ""
        
        # Phase 98.6: Sanitize model output to remove identity claims
        sanitized = self.sanitizer.extract_knowledge(model_answer)
        
        if not sanitized:
            # Model output was too contaminated with identity claims
            self.audit_log.record("model_output_discarded", "blocked", {
                "question": question,
                "reason": "output contained identity claims",
                "raw": model_answer
            })
            return None
        
        # Wrap with attribution to external knowledge
        wrapped = f"I understand it as follows: {sanitized}"
        
        # Log model usage
        self.audit_log.record("model_used_for_knowledge", "allowed", {
            "question": question,
            "raw": model_answer,
            "sanitized": sanitized,
            "wrapped": wrapped
        })
        
        return wrapped

    def govern_model_response(
        self,
        question: str,
        model_answer: str,
        belief_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check and govern model response before it's returned to user.
        Phase 98.6: Sanitize output, remove identity claims, never let model speak directly.
        
        Args:
            question: Original user question
            model_answer: Raw model output
            belief_answer: Answer from belief store (if any)
            
        Returns:
            Dict with:
            - allowed: bool (whether to use model response)
            - answer: str (final answer to return)
            - reason: str (explanation if blocked)
            - conflict: bool (whether conflict detected)
        """
        # Check 1: Is model allowed to answer this question?
        if not self.can_answer_this_question(question):
            return {
                "allowed": False,
                "answer": None,
                "reason": "Model not authorized to answer this question",
                "conflict": False
            }
        
        # Check 2: Is there a conflict with belief?
        conflict = False
        if belief_answer:
            conflict = self.check_conflict(model_answer, belief_answer, question)
            if conflict:
                return {
                    "allowed": False,
                    "answer": belief_answer,
                    "reason": f"Model answer conflicts with stored belief. Using belief instead.",
                    "conflict": True
                }
        
        # Check 3: Phase 98.6 - Wrap model output (with sanitization)
        wrapped = self.wrap_model_output(model_answer, question)
        
        if not wrapped:
            # Model output was entirely discarded due to identity claims
            return {
                "allowed": False,
                "answer": None,
                "reason": "Model output contained identity claims. Discarded.",
                "conflict": False
            }
        
        return {
            "allowed": True,
            "answer": wrapped,
            "reason": "Model response allowed and wrapped",
            "conflict": False
        }
