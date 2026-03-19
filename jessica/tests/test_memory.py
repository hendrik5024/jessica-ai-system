from jessica.memory.sqlite_store import EpisodicMemoryStore

def test_insert_and_latest():
    store = EpisodicMemoryStore()
    store.insert_event('test', 'hello', {'x':1})
    latest = store.latest(1)
    assert len(latest) == 1
    assert latest[0]['type'] == 'test'
