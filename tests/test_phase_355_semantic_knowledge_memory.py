import asyncio
from datetime import datetime

from config import load_settings
from jessica.cognition.fact_extractor import FactExtractor
from jessica.core.jessica_core import JessicaCore
from jessica.memory import episodic_memory as episodic_module
from jessica.memory import knowledge_memory as knowledge_module
from logger import get_internal_logger


def test_fact_extractor_extracts_birthplace_and_birth_year():
    extractor = FactExtractor()

    assert extractor.extract("I was born in South Africa") == ("birthplace", "South Africa")
    assert extractor.extract("I was born in 1990") == ("birth_year", "1990")


def test_pipeline_learns_birthplace_and_recalls_directly(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    asyncio.run(core.handle_input("I was born in South Africa"))
    response = asyncio.run(core.handle_input("Where was I born?"))

    assert core.knowledge_memory.get_fact("birthplace") == "South Africa"
    assert response == "You told me earlier that you were born in South Africa."


def test_pipeline_age_query_uses_knowledge_memory(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    asyncio.run(core.handle_input("I was born in 1990"))
    response = asyncio.run(core.handle_input("how old am i"))

    expected_age = datetime.now().year - 1990
    assert core.knowledge_memory.get_fact("birth_year") == "1990"
    assert response == f"You were born in 1990, which makes you {expected_age} years old."


def test_pipeline_semantic_facts_are_isolated_per_user(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    asyncio.run(core.handle_input("I was born in South Africa", user_id="alice"))
    asyncio.run(core.handle_input("I was born in Brazil", user_id="bob"))

    alice_response = asyncio.run(core.handle_input("Where was I born?", user_id="alice"))
    bob_response = asyncio.run(core.handle_input("Where was I born?", user_id="bob"))

    assert alice_response == "You told me earlier that you were born in South Africa."
    assert bob_response == "You told me earlier that you were born in Brazil."
    assert core.knowledge_memory.get_fact("birthplace", user_id="alice") == "South Africa"
    assert core.knowledge_memory.get_fact("birthplace", user_id="bob") == "Brazil"


def test_creator_identity_is_global_across_users(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    creator = core.identity.get_creator()
    alice_response = asyncio.run(core.handle_input("who created you", user_id="alice"))
    bob_response = asyncio.run(core.handle_input("who created you", user_id="bob"))

    assert creator in alice_response
    assert creator in bob_response
