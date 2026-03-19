"""
Phase 98.6: Model Isolation Layer - SIMPLIFIED

Model output sanitizer that removes direct identity claims and model self-references.
Model becomes a RAW KNOWLEDGE SOURCE, not a character speaking to the user.

Jessica interprets model knowledge, never lets model speak directly.
"""

import re
from typing import Optional


class ModelOutputSanitizer:
    """
    Sanitizes model output by removing direct model self-references.
    
    Focus: Remove "I am", "I believe", "As an AI" type statements.
    Keep: Factual knowledge ("Paris is...", "The capital is...")
    """

    def __init__(self):
        pass

    def should_discard(self, text: str) -> bool:
        """
        Check if model output is fundamentally about wrong identity.
        
        Discard cases where model:
        - Claims to BE someone ("Your name is Alice")
        - Claims to be Phi specifically
        - Explicitly says "I am an AI assistant" (at start)
        
        Args:
            text: Model output to check
            
        Returns:
            True if should discard, False if safe to process
        """
        if not text:
            return False
        
        lowered = text.lower()
        
        # Hard block: Attempting to assign wrong name to user
        if "your name is alice" in lowered:
            return True
        
        # Hard block: Claiming to be Phi (opening)
        if lowered.startswith("i am phi") or lowered.startswith("i'm phi"):
            return True
        
        # Hard block: Explicit AI assistant claim at start
        if lowered.startswith("i'm an ai assistant") or lowered.startswith("i am an ai assistant"):
            return True
        
        # Hard block: Phi's creation claim
        if "phi's creation" in lowered or "phi's personal" in lowered:
            return True
        
        return False

    def sanitize(self, text: str) -> str:
        """
        Remove model self-references and make output pure knowledge.
        
        Removes:
        - "As an AI, ..."
        - "I'm a helpful assistant..."
        - "According to my training..."
        - "My knowledge cutoff is..."
        - "Based on my knowledge..."
        
        Keeps:
        - Factual statements
        - Information content
        
        Example:
            Input: "As an AI, Paris is the capital of France."
            Output: "Paris is the capital of France."
        
        Args:
            text: Raw model output
            
        Returns:
            Sanitized text (model self-references removed)
        """
        if not text or not isinstance(text, str):
            return ""
        
        result = text
        
        # Remove opening self-references (match start of text)
        opening_patterns = [
            r"^as an ai,?\s+",
            r"^as a language model,?\s+",
            r"^i'm a helpful assistant.*?:\s*",
            r"^i'm an ai assistant.*?:\s*",
            r"^as an ai assistant,?\s+",
            r"^as a helpful assistant:?\s*",
        ]
        
        lowered_test = result.lower()
        for pattern in opening_patterns:
            if re.match(pattern, lowered_test):
                result = re.sub(pattern, "", result, flags=re.IGNORECASE)
                break
        
        # Remove training/knowledge references mid-text (full phrases including ending)
        mid_patterns = [
            r"\s+according to my training,?\s+",
            r"\s+based on my training,?\s+",
            r"\s+my knowledge cutoff is [^.]*?\.",  # Capture to period
            r"\s+i was trained on [^.]*?\.",  # Capture to period
            r"\s+according to my knowledge,?\s+",
        ]
        
        for pattern in mid_patterns:
            result = re.sub(pattern, " ", result, flags=re.IGNORECASE)
        
        # Remove "I don't have access..." disclaimers
        result = re.sub(
            r"\s+i don't have access to [^.]*?\.",
            "",
            result,
            flags=re.IGNORECASE
        )
        
        # Clean up multiple spaces
        result = re.sub(r"\s+", " ", result).strip()
        
        # Remove leading/trailing punctuation
        result = result.strip(".,;:!?-")
        
        return result

    def is_knowledge_empty(self, sanitized: str) -> bool:
        """
        Check if sanitized output contains meaningful knowledge.
        
        Args:
            sanitized: Cleaned model output
            
        Returns:
            True if too short or empty, False if contains knowledge
        """
        if not sanitized:
            return True
        
        # Less than 10 characters is probably not useful knowledge
        if len(sanitized) < 10:
            return True
        
        # Check if it's just punctuation/whitespace
        if not re.search(r"[a-z0-9]", sanitized, re.IGNORECASE):
            return True
        
        return False

    def extract_knowledge(self, text: str) -> Optional[str]:
        """
        Full extraction pipeline:
        1. Check if should discard (identity claims)
        2. Sanitize (remove self-references)
        3. Check if meaningful knowledge remains
        
        Args:
            text: Model output
            
        Returns:
            Extracted knowledge or None if discarded
        """
        # Step 1: Hard block check
        if self.should_discard(text):
            return None
        
        # Step 2: Sanitize
        cleaned = self.sanitize(text)
        
        # Step 3: Check if empty/too short
        if self.is_knowledge_empty(cleaned):
            return None
        
        return cleaned
