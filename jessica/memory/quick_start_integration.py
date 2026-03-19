"""
Quick Start: Integrating RAG Memory into Jessica's Main Agent Loop
Add long-term memory to your existing Jessica AI assistant in 3 simple steps.
"""
import sys
import os

# Step 1: Import the RAG memory system
from jessica.memory.rag_memory import RAGMemorySystem

# Step 2: Initialize memory in your Jessica class
class JessicaWithRAGMemory:
    """Example integration into your existing Jessica system."""
    
    def __init__(self):
        # Initialize your existing components
        # self.model_router = ModelRouter(...)
        # self.nlp = NLPEngine(...)
        # etc.
        
        # Add RAG memory system
        self.memory = RAGMemorySystem(
            persist_directory="./jessica_data/rag_memory",
            collection_name="jessica_conversations",
            embedding_model="all-MiniLM-L6-v2"
        )
        print("✓ RAG Memory System enabled")
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input with memory-enhanced context."""
        
        # Step 3a: Retrieve relevant memories
        memory_context = self.memory.get_context_for_llm(
            user_input,
            n_results=3  # Top 3 most relevant memories
        )
        
        # Step 3b: Construct prompt with memory context
        if memory_context:
            # Inject memories into your system prompt
            enhanced_prompt = f"""You are Jessica, an AI assistant with long-term memory.

{memory_context}

Current conversation:
User: {user_input}
Jessica:"""
        else:
            # No relevant memories found
            enhanced_prompt = f"""You are Jessica, an AI assistant.

User: {user_input}
Jessica:"""
        
        # Step 3c: Generate response using your LLM
        # response = self.model_router.route_and_generate(enhanced_prompt)
        response = "[Your LLM response here]"
        
        # Step 3d: Store this conversation for future recall
        self.memory.store_conversation(
            user_input=user_input,
            assistant_response=response,
            metadata={
                "timestamp": "2026-01-13",
                # Add any other metadata you track
            }
        )
        
        return response


# Quick integration example for your existing agent_loop.py
def integrate_into_agent_loop():
    """
    Example of integrating into your existing agent_loop.py:
    
    1. Import at the top:
       from jessica.memory.rag_memory import RAGMemorySystem
    
    2. In your AgentLoop.__init__():
       self.memory = RAGMemorySystem(
           persist_directory="./jessica_data/rag_memory"
       )
    
    3. In your main loop (before LLM call):
       memory_context = self.memory.get_context_for_llm(user_input, n_results=3)
       # Inject memory_context into your prompt
    
    4. After generating response:
       self.memory.store_conversation(user_input, response)
    """
    pass


# Example: Adding memory to existing jessica_core.py
def integrate_into_jessica_core():
    """
    Minimal changes to jessica_core.py:
    
    ```python
    # Add to imports
    from jessica.memory.rag_memory import RAGMemorySystem
    
    # In JessicaCore.__init__:
    self.rag_memory = RAGMemorySystem(
        persist_directory="./jessica_data/rag_memory"
    )
    
    # In your chat/process method:
    def chat(self, user_input):
        # Get relevant memories
        context = self.rag_memory.get_context_for_llm(user_input, n_results=3)
        
        # Build prompt with context
        if context:
            full_prompt = f"{self.system_prompt}\n\n{context}\n\nUser: {user_input}"
        else:
            full_prompt = f"{self.system_prompt}\n\nUser: {user_input}"
        
        # Generate response
        response = self.generate_response(full_prompt)
        
        # Store for future
        self.rag_memory.store_conversation(user_input, response)
        
        return response
    ```
    """
    pass


# Example: Using with your existing model router
def example_with_model_router():
    """
    Using RAG memory with your dual-model system:
    """
    from jessica.memory.rag_memory import RAGMemorySystem
    
    # Initialize
    memory = RAGMemorySystem()
    
    # When routing to chat model
    def route_chat_query(user_input):
        # Get memories first
        context = memory.get_context_for_llm(user_input, n_results=3)
        
        # Route to appropriate model (chat vs code)
        if is_coding_query(user_input):
            model_type = "code"
        else:
            model_type = "chat"
        
        # Generate with memory context
        prompt_with_memory = f"{context}\n\nUser: {user_input}" if context else user_input
        response = generate_with_model(model_type, prompt_with_memory)
        
        # Store
        memory.store_conversation(
            user_input=user_input,
            assistant_response=response,
            metadata={"model_type": model_type}
        )
        
        return response
    
    def is_coding_query(text):
        return any(kw in text.lower() for kw in ["code", "program", "function", "debug"])
    
    def generate_with_model(model_type, prompt):
        return f"[{model_type} model response]"


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Memory Integration - Quick Start Guide")
    print("=" * 60)
    print()
    print("To integrate RAG memory into Jessica:")
    print()
    print("1. Initialize in your main class:")
    print("   from jessica.memory.rag_memory import RAGMemorySystem")
    print("   self.memory = RAGMemorySystem()")
    print()
    print("2. Before LLM call, get context:")
    print("   context = self.memory.get_context_for_llm(user_input)")
    print()
    print("3. Inject context into your prompt:")
    print("   prompt = f'{system_prompt}\\n{context}\\nUser: {user_input}'")
    print()
    print("4. After response, store conversation:")
    print("   self.memory.store_conversation(user_input, response)")
    print()
    print("=" * 60)
    print()
    print("For detailed examples, see:")
    print("- rag_integration_example.py (full implementation)")
    print("- RAG_MEMORY_README.md (complete documentation)")
    print()
    print("Test it:")
    demo = JessicaWithRAGMemory()
    print("\nProcessing: 'Hello, what's my name?'")
    response = demo.process_user_input("Hello, what's my name?")
    print(f"Response: {response}")
