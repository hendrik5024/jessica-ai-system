"""
Integration Example: Using RAG Memory System with Jessica's Llama LLM
Demonstrates end-to-end usage with local Llama models
"""
from __future__ import annotations

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from jessica.memory.rag_memory import RAGMemorySystem, create_llm_prompt_with_memory


class JessicaWithMemory:
    """
    Enhanced Jessica with RAG 2.0 long-term memory integration.
    Combines conversation context with vector-based memory retrieval.
    """

    def __init__(
        self,
        llm_model=None,
        memory_dir: str = "./jessica_rag_memory",
        enable_memory: bool = True,
    ):
        """
        Initialize Jessica with memory capabilities.

        Args:
            llm_model: Your existing LLM model instance (Llama, etc.)
            memory_dir: Directory for persistent memory storage
            enable_memory: Whether to use memory system
        """
        self.llm_model = llm_model
        self.enable_memory = enable_memory
        
        # Initialize RAG memory system
        if self.enable_memory:
            self.memory = RAGMemorySystem(
                persist_directory=memory_dir,
                collection_name="jessica_conversations",
                embedding_model="all-MiniLM-L6-v2"  # Fast and efficient
            )
        else:
            self.memory = None
        
        # Jessica's personality
        self.system_prompt = """You are Jessica, an intelligent and caring AI assistant.
You have long-term memory and can recall past conversations with the user.
You are helpful, empathetic, and always strive to provide accurate information.
Use the provided memories to give contextual and personalized responses."""

    def chat(
        self,
        user_input: str,
        store_conversation: bool = True,
        retrieve_memories: int = 3,
        metadata: dict = None,
    ) -> str:
        """
        Process user input with memory-enhanced context.

        Args:
            user_input: What the user said
            store_conversation: Whether to save this exchange to memory
            retrieve_memories: Number of relevant past memories to retrieve
            metadata: Optional metadata for this conversation

        Returns:
            Jessica's response
        """
        # Step 1: Retrieve relevant memories (if enabled)
        memory_context = ""
        if self.enable_memory and self.memory:
            memory_context = self.memory.get_context_for_llm(
                user_input,
                n_results=retrieve_memories
            )
            if memory_context:
                print(f"[Memory] Retrieved {retrieve_memories} relevant memories")

        # Step 2: Construct prompt with memory context
        full_prompt = create_llm_prompt_with_memory(
            system_prompt=self.system_prompt,
            user_input=user_input,
            relevant_memories=memory_context,
            personality="friendly and remembers our past conversations"
        )

        # Step 3: Generate response using local LLM
        response = self._generate_llm_response(full_prompt)

        # Step 4: Store this conversation in memory (if enabled)
        if self.enable_memory and self.memory and store_conversation:
            conversation_metadata = metadata or {}
            conversation_metadata["user_input_length"] = len(user_input)
            conversation_metadata["response_length"] = len(response)
            
            memory_id = self.memory.store_conversation(
                user_input=user_input,
                assistant_response=response,
                metadata=conversation_metadata
            )
            print(f"[Memory] Stored as {memory_id}")

        return response

    def _generate_llm_response(self, prompt: str) -> str:
        """
        Generate response using local LLM (Llama, Mistral, etc.)
        
        This is where you integrate your existing LLM model.
        """
        if self.llm_model is not None:
            # Use your actual LLM model
            # Example for llama-cpp-python:
            # response = self.llm_model(prompt, max_tokens=256, stop=["User:", "\n\n"])
            # return response["choices"][0]["text"].strip()
            
            # Example for transformers:
            # inputs = self.tokenizer(prompt, return_tensors="pt")
            # outputs = self.model.generate(**inputs, max_length=512)
            # return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return "[LLM response would go here - integrate your model]"
        else:
            # Fallback for demo purposes
            return f"I understand you're asking about: '{prompt[-100:]}...' (Mock response - integrate your LLM)"

    def search_past_conversations(self, query: str, n_results: int = 5):
        """Search through past conversations."""
        if not self.enable_memory or not self.memory:
            print("Memory is not enabled")
            return []
        
        memories = self.memory.query_memory(query, n_results=n_results)
        return memories

    def get_memory_summary(self):
        """Get summary of stored memories."""
        if not self.enable_memory or not self.memory:
            return {"enabled": False}
        
        stats = self.memory.get_memory_stats()
        stats["enabled"] = True
        return stats


def demo_integration():
    """Demonstrate RAG memory integration with Jessica."""
    print("=== Jessica with RAG Memory - Integration Demo ===\n")
    
    # Initialize Jessica with memory
    jessica = JessicaWithMemory(
        llm_model=None,  # Replace with your actual LLM model
        memory_dir="./jessica_integration_memory",
        enable_memory=True
    )
    
    # Simulate a conversation over time
    print("--- Day 1: Initial Conversations ---")
    
    response1 = jessica.chat(
        "Hi Jessica! My name is Alex and I'm a software engineer.",
        metadata={"topic": "introduction", "day": "1"}
    )
    print(f"User: Hi Jessica! My name is Alex and I'm a software engineer.")
    print(f"Jessica: {response1}\n")
    
    response2 = jessica.chat(
        "I'm working on a machine learning project using Python and TensorFlow.",
        metadata={"topic": "work", "day": "1"}
    )
    print(f"User: I'm working on a machine learning project using Python and TensorFlow.")
    print(f"Jessica: {response2}\n")
    
    response3 = jessica.chat(
        "In my free time, I enjoy rock climbing and reading sci-fi novels.",
        metadata={"topic": "hobbies", "day": "1"}
    )
    print(f"User: In my free time, I enjoy rock climbing and reading sci-fi novels.")
    print(f"Jessica: {response3}\n")
    
    print("\n--- Day 2: Memory Recall Test ---")
    print("(Jessica should remember previous conversations)\n")
    
    response4 = jessica.chat(
        "What do you remember about my hobbies?",
        metadata={"topic": "memory_test", "day": "2"}
    )
    print(f"User: What do you remember about my hobbies?")
    print(f"Jessica: {response4}\n")
    
    response5 = jessica.chat(
        "Can you recommend a book based on what you know about me?",
        metadata={"topic": "recommendation", "day": "2"}
    )
    print(f"User: Can you recommend a book based on what you know about me?")
    print(f"Jessica: {response5}\n")
    
    # Search past conversations
    print("\n--- Searching Past Conversations ---")
    search_query = "programming and technology"
    print(f"Searching for: '{search_query}'")
    
    past_memories = jessica.search_past_conversations(search_query, n_results=3)
    print(f"Found {len(past_memories)} relevant memories:\n")
    for i, mem in enumerate(past_memories, 1):
        print(f"Memory {i}:")
        print(f"  Distance: {mem['distance']:.3f}")
        print(f"  Text: {mem['text'][:150]}...")
        print()
    
    # Memory statistics
    print("--- Memory Statistics ---")
    stats = jessica.get_memory_summary()
    print(f"Memory enabled: {stats['enabled']}")
    print(f"Total conversations stored: {stats['total_memories']}")
    print(f"Storage location: {stats['persist_directory']}")
    
    print("\n=== Integration Demo Complete ===")


def example_llama_integration():
    """
    Example of integrating with llama-cpp-python.
    Install with: pip install llama-cpp-python
    """
    print("\n=== Example: Llama.cpp Integration ===\n")
    
    try:
        from llama_cpp import Llama
        
        # Load your local Llama model
        llm = Llama(
            model_path="../../models/Phi-3.5-mini-instruct-Q4_K_M.gguf",
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        
        # Create Jessica with Llama model
        class JessicaWithLlama(JessicaWithMemory):
            def _generate_llm_response(self, prompt: str) -> str:
                """Override with actual Llama generation."""
                output = self.llm_model(
                    prompt,
                    max_tokens=256,
                    temperature=0.7,
                    top_p=0.9,
                    stop=["User:", "\n\n\n"],
                    echo=False
                )
                return output["choices"][0]["text"].strip()
        
        jessica = JessicaWithLlama(
            llm_model=llm,
            memory_dir="./jessica_llama_memory",
            enable_memory=True
        )
        
        # Test conversation
        print("User: Tell me about Python programming")
        response = jessica.chat("Tell me about Python programming")
        print(f"Jessica: {response}")
        
        print("\n✓ Successfully integrated with Llama model!")
        
    except ImportError:
        print("llama-cpp-python not installed")
        print("Install with: pip install llama-cpp-python")
    except Exception as e:
        print(f"Note: {e}")
        print("Update model path to your local Llama model")


if __name__ == "__main__":
    # Run the integration demo
    demo_integration()
    
    # Uncomment to test with actual Llama model:
    # example_llama_integration()
