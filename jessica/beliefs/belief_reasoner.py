"""
Phase 91: Belief Reasoner

Uses stored beliefs to answer questions and maintain consistency.
"""


class BeliefReasoner:
    """
    Reasons with Jessica's beliefs.
    All answers grounded in stored beliefs from memory.
    """

    def __init__(self, belief_store):
        """
        Initialize belief reasoner.
        
        Args:
            belief_store: BeliefStore instance to query
        """
        self.belief_store = belief_store

    def resolve(self, question_type, subject=None):
        """
        Resolve a question using stored beliefs.
        
        Args:
            question_type: Type of question (e.g., "user_name", "creator")
            subject: Optional subject filter
        
        Returns:
            Answer string or None if no belief found
        """
        if question_type == "user_name":
            belief = self.belief_store.get_belief("user", "name")
            if belief:
                return belief["value"]

        elif question_type == "creator":
            belief = self.belief_store.get_belief("system", "creator")
            if belief:
                return belief["value"]

        elif question_type == "user_location":
            belief = self.belief_store.get_belief("user", "location")
            if belief:
                return belief["value"]

        elif question_type == "user_birth_year":
            belief = self.belief_store.get_belief("user", "birth_year")
            if belief:
                return belief["value"]

        elif question_type == "user_birth_month":
            belief = self.belief_store.get_belief("user", "birth_month")
            if belief:
                return belief["value"]

        return None

    def get_confidence(self, subject, predicate):
        """
        Get confidence level of a belief.
        
        Args:
            subject: Subject of belief
            predicate: Predicate of belief
        
        Returns:
            Confidence (0.0-1.0) or None if no belief
        """
        belief = self.belief_store.get_belief(subject, predicate)
        return belief["confidence"] if belief else None

    def has_belief(self, subject, predicate):
        """
        Check if a belief exists.
        
        Args:
            subject: Subject of belief
            predicate: Predicate of belief
        
        Returns:
            True if belief exists
        """
        return self.belief_store.get_belief(subject, predicate) is not None

    def get_all_about(self, subject):
        """
        Get all beliefs about a subject.
        
        Args:
            subject: Subject to query
        
        Returns:
            List of beliefs about subject
        """
        return self.belief_store.query(subject=subject)

    def get_conflicts(self):
        """
        Detect conflicting beliefs (same subject/predicate, different values).
        
        Returns:
            List of (subject, predicate) pairs with conflicting values
        """
        conflicts = []
        seen_keys = {}

        for belief in self.belief_store.get_all():
            key = (belief["subject"], belief["predicate"])
            if key in seen_keys:
                if seen_keys[key] != belief["value"]:
                    conflicts.append(key)
            else:
                seen_keys[key] = belief["value"]

        return conflicts

    def format_belief(self, belief):
        """
        Format a belief for display.
        
        Args:
            belief: Belief record to format
        
        Returns:
            Human-readable string
        """
        return (
            f"{belief['subject']}[{belief['predicate']}] = {belief['value']} "
            f"(confidence: {belief['confidence']}, source: {belief['source']})"
        )
