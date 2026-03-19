"""Test the multi-brain router system."""
from jessica.nlp.model_router import ModelRouter
import time

def test_router():
    """Test intent categorization and routing."""
    print("=== Testing Multi-Brain Router ===\n")
    
    router = ModelRouter()
    
    # Test cases for different intent categories
    test_inputs = [
        ("Hello! How are you today?", "SMALL_TALK"),
        ("Write a Python function to calculate fibonacci", "CODING"),
        ("What's a good recipe for chocolate cake?", "GENERAL_KNOWLEDGE"),
        ("How do I debug a JavaScript error?", "CODING"),
        ("Tell me about the weather", "SMALL_TALK"),
        ("Explain the theory of relativity", "GENERAL_KNOWLEDGE"),
        ("Good morning Jessica!", "SMALL_TALK"),
        ("Help me write a SQL query", "CODING"),
    ]
    
    print("--- Intent Categorization Test ---\n")
    for user_input, expected in test_inputs:
        category = router.categorize_intent(user_input)
        status = "✓" if category == expected else "✗"
        print(f"{status} '{user_input[:50]}'")
        print(f"   Expected: {expected}, Got: {category}\n")
    
    print("\n--- Full Response Test ---\n")
    
    # Test small talk (should use fast_brain)
    print("1. Testing SMALL_TALK routing:")
    print("   Input: 'Hi Jessica!'")
    response = router.jessica_think("Hi Jessica!", max_tokens=50)
    print(f"   Response: {response[:100]}...\n")
    
    # Test coding (should use code_brain)
    print("2. Testing CODING routing:")
    print("   Input: 'Write hello world in Python'")
    response = router.jessica_think("Write hello world in Python", max_tokens=50)
    print(f"   Response: {response[:100]}...\n")
    
    print("✓ Multi-brain router test complete!")

def test_streaming():
    """Test streaming with router."""
    print("\n\n=== Testing Streaming with Router ===\n")
    
    router = ModelRouter()
    
    print("Streaming response for: 'What is 2+2?'")
    print("Response: ", end="", flush=True)
    
    for chunk in router.jessica_think_stream("What is 2+2?", max_tokens=50):
        print(chunk, end="", flush=True)
    
    print("\n\n✓ Streaming test complete!")

if __name__ == "__main__":
    try:
        test_router()
        test_streaming()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
