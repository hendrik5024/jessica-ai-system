from collections import deque
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ConversationTurn:
    user: str
    jessica: str


class ConversationMemory:
    """
    Short-term conversation memory (working memory)

    Stores last N turns of conversation
    """

    def __init__(self, max_turns: int = 10):
        self._history = deque(maxlen=max_turns)

    def add_turn(self, user_input: str, jessica_response: str):
        self._history.append(
            ConversationTurn(user=user_input, jessica=jessica_response)
        )

    def get_recent(self) -> List[ConversationTurn]:
        return list(self._history)

    def get_last_user_input(self) -> str:
        if not self._history:
            return ""
        return self._history[-1].user

    def get_last_response(self) -> str:
        if not self._history:
            return ""
        return self._history[-1].jessica

    def clear(self):
        self._history.clear()
