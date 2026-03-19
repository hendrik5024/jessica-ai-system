"""
Quick test script to verify RAG memory system installation and functionality.
Run this after installing dependencies to ensure everything works.
"""
import sys


def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    
    try:
        import chromadb
        print("✓ chromadb installed")
    except ImportError as e:
        print("✗ chromadb NOT installed - run: pip install chromadb")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers installed")
    except ImportError:
        print("✗ sentence-transformers NOT installed - run: pip install sentence-transformers")
        return False
    
    try:
        import numpy
        print("✓ numpy installed")
    except ImportError:
        print("✗ numpy NOT installed - run: pip install numpy")
        return False
    
    try:
        import torch
        print("✓ torch installed")
    except ImportError:
        print("✗ torch NOT installed - run: pip install torch")
        return False
    
    return True


def test_basic_functionality():
    """Test basic RAG memory operations."""
    print("\nTesting RAG memory functionality...")
    
    try:
        from rag_memory import RAGMemorySystem
        
        # Initialize
        memory = RAGMemorySystem(
            persist_directory="./test_rag_memory",
            collection_name="test_collection"
        )
        print("✓ RAGMemorySystem initialized")
        
        # Store a memory
        memory_id = memory.store_memory(
            text="Test memory for verification",
            metadata={"test": True}
        )
        print(f"✓ Memory stored: {memory_id}")
        
        # Query memory
        results = memory.query_memory("verification test", n_results=1)
        if results and len(results) > 0:
            print(f"✓ Memory retrieval working (found {len(results)} results)")
        else:
            print("✗ Memory retrieval failed")
            return False
        
        # Get stats
        stats = memory.get_memory_stats()
        print(f"✓ Memory stats: {stats['total_memories']} memories stored")
        
        # Cleanup test data
        memory.clear_all_memories()
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing RAG memory: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_storage():
    """Test conversation storage and retrieval."""
    print("\nTesting conversation storage...")
    
    try:
        from rag_memory import RAGMemorySystem
        
        memory = RAGMemorySystem(
            persist_directory="./test_rag_memory",
            collection_name="test_conversations"
        )
        
        # Store a conversation
        conv_id = memory.store_conversation(
            user_input="I love programming in Python",
            assistant_response="Python is a great language!",
            metadata={"topic": "programming"}
        )
        print(f"✓ Conversation stored: {conv_id}")
        
        # Query for relevant conversation
        results = memory.query_memory("Python programming", n_results=1)
        if results and "Python" in results[0]["text"]:
            print("✓ Conversation retrieval successful")
        else:
            print("✗ Conversation retrieval failed")
            return False
        
        # Get LLM context
        context = memory.get_context_for_llm("Tell me about Python", n_results=1)
        if context and "RELEVANT PAST MEMORIES" in context:
            print("✓ LLM context formatting successful")
        else:
            print("✗ LLM context formatting failed")
            return False
        
        # Cleanup
        memory.clear_all_memories()
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing conversations: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG Memory System - Installation Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        print("\n⚠️ Some dependencies are missing. Install them with:")
        print("   pip install -r rag_requirements.txt")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    # Test conversation storage
    if not test_conversation_storage():
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("RAG memory system is ready to use.")
        print("\nNext steps:")
        print("1. Run the demo: python rag_memory.py")
        print("2. See integration example: python rag_integration_example.py")
        print("3. Read the docs: RAG_MEMORY_README.md")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check error messages above for details.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
