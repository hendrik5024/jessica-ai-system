from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.knowledge_entry import KnowledgeEntry
from jessica.knowledge_store import KnowledgeStore
from jessica.knowledge_retriever import KnowledgeRetriever
from jessica.knowledge_orchestrator import KnowledgeOrchestrator


def _entry(entry_id: str, topic: str, content: str, tags: list[str], version: int) -> KnowledgeEntry:
    return KnowledgeEntry(
        entry_id=entry_id,
        topic=topic,
        content=content,
        tags=tags,
        version=version,
        created_at=datetime(2026, 2, 9, 12, 0, 0),
    )


def test_entry_immutable():
    entry = _entry("e1", "topic", "content", ["tag"], 1)
    with pytest.raises(FrozenInstanceError):
        entry.topic = "new"


def test_store_append_only():
    store = KnowledgeStore()
    entry = _entry("e1", "topic", "content", ["tag"], 1)
    store.add_entry(entry)
    with pytest.raises(ValueError):
        store.add_entry(entry)


def test_get_entry():
    store = KnowledgeStore()
    entry = _entry("e1", "topic", "content", ["tag"], 1)
    store.add_entry(entry)
    assert store.get_entry("e1") == entry


def test_search_by_topic_exact_case_insensitive():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "Topic", "content", ["tag"], 1))
    results = store.search_by_topic("topic")
    assert results[0].entry_id == "e1"


def test_search_by_topic_deterministic_order():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "c1", ["tag"], 1))
    store.add_entry(_entry("e2", "topic", "c2", ["tag"], 2))
    results = store.search_by_topic("topic")
    assert [r.entry_id for r in results] == ["e2", "e1"]


def test_search_by_tag():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "t1", "c1", ["tag"], 1))
    store.add_entry(_entry("e2", "t2", "c2", ["tag"], 2))
    results = store.search_by_tag("tag")
    assert [r.entry_id for r in results] == ["e2", "e1"]


def test_list_topics_sorted():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "b", "c1", ["tag"], 1))
    store.add_entry(_entry("e2", "a", "c2", ["tag"], 1))
    assert store.list_topics() == ["a", "b"]


def test_retrieve_by_topic():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    retriever = KnowledgeRetriever(store)
    results = retriever.retrieve("topic")
    assert results[0].entry_id == "e1"


def test_retrieve_best_match_exact():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    store.add_entry(_entry("e2", "topic", "content2", ["tag"], 2))
    retriever = KnowledgeRetriever(store)
    best = retriever.retrieve_best_match("topic")
    assert best.entry_id == "e2"


def test_retrieve_best_match_substring():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    retriever = KnowledgeRetriever(store)
    best = retriever.retrieve_best_match("top")
    assert best.entry_id == "e1"


def test_retrieve_best_match_none():
    store = KnowledgeStore()
    retriever = KnowledgeRetriever(store)
    assert retriever.retrieve_best_match("unknown") is None


def test_retrieve_by_tags_any_match():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag1"], 1))
    store.add_entry(_entry("e2", "topic", "content", ["tag2"], 1))
    retriever = KnowledgeRetriever(store)
    results = retriever.retrieve_by_tags(["tag2"]) 
    assert [r.entry_id for r in results] == ["e2"]


def test_orchestrator_answer_query():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    orchestrator = KnowledgeOrchestrator(KnowledgeRetriever(store))
    result = orchestrator.answer_query("topic")
    assert result["content"] == "content"
    assert result["entry_id"] == "e1"


def test_orchestrator_answer_topic():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    orchestrator = KnowledgeOrchestrator(KnowledgeRetriever(store))
    result = orchestrator.answer_topic("topic")
    assert result["content"] == "content"


def test_versioning_correctness():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "c1", ["tag"], 1))
    store.add_entry(_entry("e2", "topic", "c2", ["tag"], 3))
    retriever = KnowledgeRetriever(store)
    best = retriever.retrieve_best_match("topic")
    assert best.entry_id == "e2"


def test_no_execution_side_effects():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    retriever = KnowledgeRetriever(store)
    retriever.retrieve_best_match("topic")
    assert store.count() == 1


def test_deterministic_output_across_runs():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    retriever = KnowledgeRetriever(store)
    result1 = retriever.retrieve_best_match("topic")
    result2 = retriever.retrieve_best_match("topic")
    assert result1.entry_id == result2.entry_id


def test_query_resolution_prefers_topic():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    store.add_entry(_entry("e2", "other", "topic content", ["tag"], 2))
    retriever = KnowledgeRetriever(store)
    best = retriever.retrieve_best_match("topic")
    assert best.entry_id == "e1"


def test_orchestrator_confidence_exact():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    orchestrator = KnowledgeOrchestrator(KnowledgeRetriever(store))
    result = orchestrator.answer_query("topic")
    assert result["confidence"] == 0.9


def test_orchestrator_confidence_substring():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    orchestrator = KnowledgeOrchestrator(KnowledgeRetriever(store))
    result = orchestrator.answer_query("top")
    assert result["confidence"] == 0.7


def test_append_only_integrity():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    _ = store.search_by_topic("topic")
    assert store.count() == 1


def test_tag_search_case_insensitive():
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["Tag"], 1))
    results = store.search_by_tag("tag")
    assert results[0].entry_id == "e1"


def test_logging_on_access(caplog):
    store = KnowledgeStore()
    store.add_entry(_entry("e1", "topic", "content", ["tag"], 1))
    caplog.set_level("INFO")
    _ = store.get_entry("e1")
    assert any("knowledge.get_entry" in record.message for record in caplog.records)
