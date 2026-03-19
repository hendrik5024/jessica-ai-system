"""
RAG 2.0 - Recursive Memory System for Jessica AI Assistant
Uses ChromaDB for local persistent vector storage with sentence-transformers embeddings.
All processing happens locally - no data leaves the machine.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except ImportError:
    raise ImportError(
        "chromadb not installed. Install with: pip install chromadb"
    )

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "sentence-transformers not installed. Install with: pip install sentence-transformers"
    )


class RAGMemorySystem:
    """
    Long-term recursive memory system using ChromaDB and local embeddings.
    Stores conversation history and retrieves relevant context for AI responses.
    """

    def __init__(
        self,
        persist_directory: str = "./jessica_rag_memory",
        collection_name: str = "conversation_memory",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize the RAG memory system.

        Args:
            persist_directory: Path to store ChromaDB data locally
            collection_name: Name of the memory collection
            embedding_model: Sentence-transformers model name
                - all-MiniLM-L6-v2: Fast, good quality (default)
                - all-mpnet-base-v2: Slower but higher quality
                - paraphrase-multilingual-MiniLM-L12-v2: For multilingual support
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with local persistence (new API)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,  # Privacy: no telemetry
            )
        )
        
        # Initialize local embedding function using sentence-transformers
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Long-term conversation memory for Jessica AI"}
        )
        
        print(f"✓ RAG Memory System initialized")
        print(f"  - Storage: {persist_directory}")
        print(f"  - Collection: {collection_name}")
        print(f"  - Memories stored: {self.collection.count()}")

    def store_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> str:
        """
        Store a conversation snippet or memory in the vector database.

        Args:
            text: The conversation text or memory to store
            metadata: Optional metadata (user_name, timestamp, emotion, topic, etc.)
            memory_id: Optional custom ID, otherwise auto-generated

        Returns:
            The ID of the stored memory
        """
        if not text or not text.strip():
            raise ValueError("Cannot store empty memory text")

        # Generate ID if not provided
        if memory_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            memory_id = f"mem_{timestamp}"

        # Prepare metadata with timestamp
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = metadata.get("timestamp", datetime.now().isoformat())
        metadata["stored_at"] = datetime.now().isoformat()
        
        # Store in ChromaDB
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        print(f"✓ Stored memory: {memory_id}")
        return memory_id

    def store_conversation(
        self,
        user_input: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a complete conversation exchange (user + assistant).

        Args:
            user_input: What the user said
            assistant_response: Jessica's response
            metadata: Additional context (emotion, skill_used, etc.)

        Returns:
            The ID of the stored conversation
        """
        # Format as conversation
        conversation_text = f"User: {user_input}\nJessica: {assistant_response}"
        
        # Add conversation metadata
        if metadata is None:
            metadata = {}
        
        metadata["type"] = "conversation"
        metadata["user_input"] = user_input[:200]  # Store snippet for quick reference
        metadata["assistant_response"] = assistant_response[:200]
        
        return self.store_memory(conversation_text, metadata)

    def query_memory(
        self,
        user_input: str,
        n_results: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the memory database for relevant past interactions.

        Args:
            user_input: Current user query to find relevant memories for
            n_results: Number of top memories to retrieve (default: 3)
            filter_metadata: Optional metadata filter (e.g., {"type": "conversation"})

        Returns:
            List of relevant memories with text, metadata, and similarity distance
        """
        if not user_input or not user_input.strip():
            return []
        
        # Check if collection is empty
        collection_count = self.collection.count()
        if collection_count == 0:
            return []  # No memories to retrieve
        
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[user_input],
            n_results=min(n_results, collection_count),
            where=filter_metadata if filter_metadata else None,
        )
        
        # Format results
        memories = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                memory = {
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "id": results["ids"][0][i] if results["ids"] else None,
                }
                memories.append(memory)
        
        return memories

    def get_context_for_llm(
        self,
        user_input: str,
        n_results: int = 3,
        include_in_prompt: bool = True,
    ) -> str:
        """
        Retrieve relevant memories and format them for LLM context injection.

        Args:
            user_input: Current user query
            n_results: Number of memories to retrieve
            include_in_prompt: Whether to format as prompt-ready text

        Returns:
            Formatted context string ready to inject into LLM prompt
        """
        memories = self.query_memory(user_input, n_results=n_results)
        
        if not memories:
            return ""
        
        if include_in_prompt:
            context_parts = ["=== RELEVANT PAST MEMORIES ==="]
            for i, mem in enumerate(memories, 1):
                timestamp = mem["metadata"].get("timestamp", "unknown time")
                text = mem["text"]
                context_parts.append(f"\n[Memory {i}] ({timestamp}):")
                context_parts.append(text)
            context_parts.append("\n=== END MEMORIES ===\n")
            return "\n".join(context_parts)
        else:
            return "\n\n".join([mem["text"] for mem in memories])

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory by ID."""
        try:
            self.collection.delete(ids=[memory_id])
            print(f"✓ Deleted memory: {memory_id}")
            return True
        except Exception as e:
            print(f"✗ Error deleting memory {memory_id}: {e}")
            return False

    def clear_all_memories(self) -> bool:
        """Clear all memories from the collection. Use with caution!"""
        try:
            count = self.collection.count()
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
            print(f"✓ Cleared {count} memories")
            return True
        except Exception as e:
            print(f"✗ Error clearing memories: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        return {
            "total_memories": self.collection.count(),
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
        }

    def search_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search memories by metadata only (no semantic search).

        Args:
            metadata_filter: Metadata to filter by (e.g., {"type": "conversation"})
            n_results: Max number of results

        Returns:
            List of matching memories
        """
        results = self.collection.get(
            where=metadata_filter,
            limit=n_results,
        )
        
        memories = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                memory = {
                    "text": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    "id": results["ids"][i] if results["ids"] else None,
                }
                memories.append(memory)
        
        return memories


def create_llm_prompt_with_memory(
    system_prompt: str,
    user_input: str,
    relevant_memories: str,
    personality: Optional[str] = None,
) -> str:
    """
    Helper function to construct a complete LLM prompt with memory context.

    Args:
        system_prompt: Base system instructions for the LLM
        user_input: Current user query
        relevant_memories: Retrieved memory context from query_memory()
        personality: Optional personality/role description

    Returns:
        Complete prompt ready for local LLM (Llama, Mistral, etc.)
    """
    prompt_parts = [system_prompt]
    
    if personality:
        prompt_parts.append(f"\nYour personality: {personality}")
    
    if relevant_memories:
        prompt_parts.append(f"\n{relevant_memories}")
    
    prompt_parts.append(f"\nUser: {user_input}")
    prompt_parts.append("Jessica:")
    
    return "\n".join(prompt_parts)


# Example usage and testing
if __name__ == "__main__":
    print("=== RAG 2.0 Memory System Demo ===\n")
    
    # Initialize the memory system
    memory = RAGMemorySystem(
        persist_directory="./demo_rag_memory",
        collection_name="jessica_demo",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    # Example 1: Store some conversation memories
    print("\n--- Example 1: Storing Conversations ---")
    
    memory.store_conversation(
        user_input="I love hiking in the mountains on weekends",
        assistant_response="That's wonderful! Hiking is great exercise and the mountain air must be refreshing.",
        metadata={"topic": "hobbies", "emotion": "positive"}
    )
    
    memory.store_conversation(
        user_input="My favorite food is Italian pasta",
        assistant_response="Italian cuisine is delicious! Do you have a favorite pasta dish?",
        metadata={"topic": "food", "emotion": "positive"}
    )
    
    memory.store_conversation(
        user_input="I'm learning Python programming",
        assistant_response="Python is an excellent choice! It's versatile and beginner-friendly. What are you building?",
        metadata={"topic": "programming", "emotion": "curious"}
    )
    
    print(f"\n✓ Stored 3 conversations")
    
    # Example 2: Query relevant memories
    print("\n--- Example 2: Querying Relevant Memories ---")
    
    query = "What outdoor activities do I enjoy?"
    print(f"Query: '{query}'")
    
    memories = memory.query_memory(query, n_results=2)
    print(f"\nFound {len(memories)} relevant memories:")
    for i, mem in enumerate(memories, 1):
        print(f"\nMemory {i} (distance: {mem['distance']:.3f}):")
        print(f"  Text: {mem['text'][:100]}...")
        print(f"  Metadata: {mem['metadata']}")
    
    # Example 3: Get formatted context for LLM
    print("\n--- Example 3: LLM Context Integration ---")
    
    user_query = "Tell me about my hobbies"
    context = memory.get_context_for_llm(user_query, n_results=2)
    
    # Create complete prompt for local LLM
    system_prompt = "You are Jessica, a helpful AI assistant with long-term memory."
    personality = "friendly, empathetic, and remembers past conversations"
    
    full_prompt = create_llm_prompt_with_memory(
        system_prompt=system_prompt,
        user_input=user_query,
        relevant_memories=context,
        personality=personality
    )
    
    print("\nComplete LLM Prompt:")
    print("-" * 60)
    print(full_prompt)
    print("-" * 60)
    
    # Example 4: Memory statistics
    print("\n--- Example 4: Memory Statistics ---")
    stats = memory.get_memory_stats()
    print(f"Total memories: {stats['total_memories']}")
    print(f"Collection: {stats['collection_name']}")
    print(f"Storage: {stats['persist_directory']}")
    
    print("\n=== Demo Complete ===")
    print("Memory persists in './demo_rag_memory' directory")
    print("Run this script again to see memories are retained!")
