import asyncio

from config import load_settings
from jessica.core.jessica_core import JessicaCore as CanonicalJessicaCore
from jessica.jessica_core import CognitiveManager
from jessica_core import JessicaCore as RootJessicaCore
from logger import get_internal_logger


def test_root_core_is_canonical_alias():
    assert RootJessicaCore is CanonicalJessicaCore


def test_legacy_cognitive_manager_routes_to_canonical_core():
    manager = CognitiveManager()
    result = manager.handle_input("Who created you?")

    assert isinstance(result, dict)
    assert "result" in result
    assert "reply" in result["result"]
    assert "Hendrik Venter" in result["result"]["reply"]


def test_canonical_core_identity_response():
    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = CanonicalJessicaCore(settings=settings, logger=logger)

    response = asyncio.run(core.handle_input("Who owns this system?"))

    assert "This installation of Jessica belongs to" in response
