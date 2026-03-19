from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable

from config import load_settings
from jessica.nlp.intent_parser import parse_intent
from jessica.core.jessica_core import JessicaCore
from logger import get_internal_logger


@dataclass
class _AgencyAdapter:
    manager: "CognitiveManager"

    def respond(self, text: str, user: str = "default", stream: bool = False, use_router: bool = True):
        response = self.manager._run_core(text, user=user)

        if stream:
            return self._stream_once(response)

        return response

    def _stream_once(self, response: str) -> Iterable[str]:
        yield response


class CognitiveManager:
    """Compatibility wrapper for legacy package entrypoints.

    Routes all handling through the canonical Phase stack `JessicaCore`.
    """

    def __init__(self):
        settings = load_settings()
        logger = get_internal_logger(settings.log_file)
        self._core = JessicaCore(settings=settings, logger=logger)
        self.agency = _AgencyAdapter(self)

    def _run_core(self, text: str, user: str = "default") -> str:
        loop = asyncio.new_event_loop()

        try:
            return loop.run_until_complete(self._core.handle_input(text, user_id=user))
        finally:
            loop.close()

    def handle_input(self, text: str, user: str = "default") -> Dict[str, Any]:
        result = self._run_core(text, user=user)

        return {
            "source": "core_adapter",
            "result": {"reply": result},
            "semantic_context": [],
        }


__all__ = ["CognitiveManager", "parse_intent"]
