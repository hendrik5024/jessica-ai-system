"""Test the Long-Term Memory and Chain-of-Thought systems."""
from jessica.memory.long_term_memory import LongTermMemory
from jessica.nlp.model_router import ModelRouter
import time

def test_ltm():
    """Test LTM extraction and retrieval."""
    print("=== Testing Long-Term Memory System ===\n")
    
    ltm = LongTermMemory(db_path="test_user_profile.db", extraction_interval=3)
    model_router = ModelRouter()
    
    # Simulate conversations
    mock_episodes = [
        {"input_text": "My name is Alex", "output": {"reply": "Nice to meet you, Alex!"}},
        {"input_text": "I love playing guitar", "output": {"reply": "That's great! Music is wonderful."}},
        {"input_text": "I work as a software engineer", "output": {"reply": "Interesting career choice!"}},
        {"input_text": "I'm planning a trip to Japan", "output": {"reply": "That sounds exciting!"}},
        {"input_text": "I prefer tea over coffee", "output": {"reply": "Noted! I'll remember that."}},
    ]
    
    # Test interaction counting
    for i in range(5):
        count = ltm.increment_interaction()
        print(f"Interaction {count}")
        
        if ltm.should_extract():
            print(f"  -> Extraction triggered at interaction {count}")
            facts = ltm.extract_facts(mock_episodes[:count], model_router)
            print(f"  -> Extracted {len(facts)} facts:")
            for fact in facts:
                print(f"     - {fact}")
            ltm.save_facts(facts, category="test")
    
    # Test retrieval
    print("\n=== Retrieved Memorable Facts ===")
    stored_facts = ltm.retrieve_facts(limit=10)
    for fact in stored_facts:
        print(f"- {fact['fact']} (confidence: {fact['confidence']})")
    
    # Test context summary
    print("\n=== Context Summary for Prompts ===")
    summary = ltm.get_context_summary(limit=5)
    print(summary)
    
    # Statistics
    print("\n=== LTM Statistics ===")
    stats = ltm.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

def test_cot_parsing():
    """Test Chain-of-Thought parsing."""
    print("\n\n=== Testing Chain-of-Thought Parsing ===\n")
    
    from jessica.agent_loop import AgencyLoop
    from jessica.personality import Personality
    from jessica.memory.sqlite_store import EpisodicStore
    from jessica.memory.embeddings_index import EmbeddingsIndex
    
    personality = Personality()
    memory = EpisodicStore("test_jessica_data.db")
    embeddings = EmbeddingsIndex("test_jessica_embeddings")
    model_router = ModelRouter()
    
    agency = AgencyLoop(memory, embeddings, model_router, personality)
    
    # Test CoT parsing with properly formatted response
    test_responses = [
        """[REASONING]
The user is asking about my capabilities. I should list my main features clearly.
First, I'll mention the BDI architecture, then tools, then streaming.
[/REASONING]

[ANSWER]
I'm Jessica, an offline AI with BDI architecture, safe tool execution, and streaming responses.
[/ANSWER]""",
        
        "This is a response without CoT tags.",
        
        """Some text before
[REASONING]
Thinking about the weather...
[/REASONING]
Some middle text
[ANSWER]
It's sunny today!
[/ANSWER]
Some text after"""
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"Test {i}:")
        parsed = agency._parse_cot(response)
        print(f"  Reasoning: {parsed['reasoning'][:50]}..." if len(parsed['reasoning']) > 50 else f"  Reasoning: {parsed['reasoning']}")
        print(f"  Answer: {parsed['answer'][:50]}..." if len(parsed['answer']) > 50 else f"  Answer: {parsed['answer']}")
        print()

if __name__ == "__main__":
    try:
        test_ltm()
        test_cot_parsing()
        print("\n✓ All tests completed!")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
