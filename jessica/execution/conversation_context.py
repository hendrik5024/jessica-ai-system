from dataclasses import dataclass
from typing import Tuple

from .reflection_record import ReflectionRecord


@dataclass(frozen=True)
class ConversationContext:
    """
    Immutable, read-only conversation context for Phase 8.2.
    """

    current_reflection: ReflectionRecord
    prior_reflections: Tuple[ReflectionRecord, ...]
    max_history: int = 3

    def __post_init__(self) -> None:
        if self.current_reflection is None:
            raise ValueError("current_reflection cannot be None")
        if self.max_history < 0:
            raise ValueError("max_history cannot be negative")

        prior = tuple(self.prior_reflections)
        if self.max_history == 0:
            prior = ()
        elif len(prior) > self.max_history:
            prior = prior[: self.max_history]

        object.__setattr__(self, "prior_reflections", prior)

    def has_prior_context(self) -> bool:
        return len(self.prior_reflections) > 0

