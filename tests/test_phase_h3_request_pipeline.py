import asyncio

from config import load_settings
from jessica.core.jessica_core import JessicaCore
from logger import get_internal_logger


def _core():
    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    return JessicaCore(settings=settings, logger=logger)


def test_h3_pipeline_components_exist():
    core = _core()

    assert core.request_pipeline is not None
    assert core.response_router is not None


def test_h3_identity_layer_response():
    core = _core()

    response = asyncio.run(core.handle_input("Who created you?"))

    assert "Hendrik Venter" in response


def test_h3_internal_intent_layer_response():
    core = _core()

    response = asyncio.run(core.handle_input("system status"))

    assert "System status:" in response
