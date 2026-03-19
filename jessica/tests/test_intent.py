from jessica.jessica_core import parse_intent

def test_reminder_intent():
    intent = parse_intent("Remind me to drink water at 15:00")
    assert intent['intent'] == 'set_reminder'

def test_open_app_intent():
    intent = parse_intent("open excel")
    assert intent['intent'] == 'open_app'

def test_chat_fallback():
    intent = parse_intent("How are you today?")
    assert intent['intent'] == 'chat'
