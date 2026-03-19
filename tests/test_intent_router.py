from intent_router import route_intent


def test_time_query_with_punctuation_routes_to_time():
    assert route_intent("What is the time?") == "TIME"


def test_system_time_query_routes_to_time():
    assert route_intent("Can you check system time?") == "TIME"


def test_system_status_still_routes_correctly():
    assert route_intent("Can you check system status?") == "SYSTEM_STATUS"
