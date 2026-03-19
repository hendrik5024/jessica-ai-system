# RAG 2.0 - Long-Term Memory System for Jessica

A fully **offline, privacy-first** recursive memory system using ChromaDB and local embeddings. Jessica can now remember past conversations and provide contextually-aware responses.

## 🎯 Features

- **100% Local**: All data stays on your machine - no API calls, no cloud services
- **Vector-Based Memory**: Uses ChromaDB for fast semantic search
- **Local Embeddings**: sentence-transformers models run entirely offline
- **Persistent Storage**: Memories survive across restarts
- **Easy Integration**: Simple API to add to any LLM chatbot
- **Metadata Support**: Tag memories with custom metadata (topics, emotions, dates)
- **LLM-Ready**: Automatic context formatting for Llama, Mistral, etc.

## 📦 Installation

### Install ChromaDB and Dependencies

```bash
cd jessica/memory
pip install -r rag_requirements.txt
```

Or install individually:
```bash
pip install chromadb sentence-transformers
```

### Verify Installation

```bash
python rag_memory.py
```

You should see the demo output showing memory storage and retrieval.

## 🚀 Quick Start

### Basic Usage

```python
from jessica.memory.rag_memory import RAGMemorySystem

# Initialize memory system
memory = RAGMemorySystem(
    persist_directory="./my_memories",
    embedding_model="all-MiniLM-L6-v2"  # Fast local model
)

# Store a conversation
memory.store_conversation(
    user_input="I love hiking in the mountains",
    assistant_response="That's wonderful! Mountain hiking is great exercise.",
    metadata={"topic": "hobbies", "emotion": "positive"}
)

# Query relevant memories
user_query = "What outdoor activities do I enjoy?"
relevant_memories = memory.query_memory(user_query, n_results=3)

for mem in relevant_memories:
    print(f"Memory: {mem['text']}")
    print(f"Similarity: {mem['distance']}")
```

### Integration with LLM

```python
from jessica.memory.rag_memory import RAGMemorySystem, create_llm_prompt_with_memory

memory = RAGMemorySystem()

# Get user input
user_input = "What do you remember about me?"

# Retrieve relevant context
context = memory.get_context_for_llm(user_input, n_results=3)

# Create complete prompt for your LLM
system_prompt = "You are Jessica, a helpful AI with long-term memory."
full_prompt = create_llm_prompt_with_memory(
    system_prompt=system_prompt,
    user_input=user_input,
    relevant_memories=context
)

# Send to your local Llama model
response = your_llm_model.generate(full_prompt)
```

### Full Integration Example

See `rag_integration_example.py` for a complete chatbot implementation with:
- Conversation storage
- Memory retrieval
- LLM integration
- Metadata tagging

Run it:
```bash
python rag_integration_example.py
```

## 🧠 Embedding Models

Choose based on your needs:

| Model | Speed | Quality | Size |
|-------|-------|---------|------|
| `all-MiniLM-L6-v2` | ⚡ Fast | ✓ Good | 80MB |
| `all-mpnet-base-v2` | 🐢 Slower | ⭐ Best | 420MB |
| `paraphrase-multilingual-MiniLM-L12-v2` | ⚡ Fast | ✓ Good | 470MB |

**Default**: `all-MiniLM-L6-v2` (good balance)

Change model:
```python
memory = RAGMemorySystem(embedding_model="all-mpnet-base-v2")
```

## 📊 API Reference

### RAGMemorySystem

#### `__init__(persist_directory, collection_name, embedding_model)`
Initialize the memory system.

#### `store_memory(text, metadata, memory_id) -> str`
Store a single memory with optional metadata.

#### `store_conversation(user_input, assistant_response, metadata) -> str`
Store a complete conversation exchange.

#### `query_memory(user_input, n_results, filter_metadata) -> List[Dict]`
Search for relevant memories semantically.

Returns:
```python
[
    {
        "text": "conversation text",
        "metadata": {"topic": "hobbies"},
        "distance": 0.234,  # Lower = more similar
        "id": "mem_20260113_123456"
    }
]
```

#### `get_context_for_llm(user_input, n_results) -> str`
Get formatted memory context ready to inject into LLM prompt.

#### `delete_memory(memory_id) -> bool`
Delete a specific memory.

#### `clear_all_memories() -> bool`
⚠️ Delete ALL memories (use with caution!).

#### `get_memory_stats() -> Dict`
Get statistics about stored memories.

## 🔧 Advanced Usage

### Metadata Filtering

Store with metadata:
```python
memory.store_conversation(
    user_input="I work as a software engineer",
    assistant_response="That's interesting! What languages do you use?",
    metadata={
        "topic": "work",
        "subtopic": "career",
        "emotion": "neutral",
        "date": "2026-01-13"
    }
)
```

Query with metadata filter:
```python
# Only retrieve work-related memories
memories = memory.query_memory(
    "What do you know about my job?",
    n_results=5,
    filter_metadata={"topic": "work"}
)
```

### Search by Metadata Only

```python
# Find all conversations about hobbies
hobby_memories = memory.search_by_metadata(
    metadata_filter={"topic": "hobbies"},
    n_results=10
)
```

### Custom Memory IDs

```python
memory.store_memory(
    text="Important user preference: prefers dark mode",
    metadata={"type": "preference"},
    memory_id="pref_dark_mode"
)
```

## 🔗 Integration with Jessica's LLM

### Using with Llama.cpp

```python
from llama_cpp import Llama
from jessica.memory.rag_memory import RAGMemorySystem, create_llm_prompt_with_memory

# Load Llama model
llm = Llama(model_path="./models/Phi-3.5-mini-instruct-Q4_K_M.gguf")

# Initialize memory
memory = RAGMemorySystem()

# Process user input
user_input = "What did we talk about yesterday?"
context = memory.get_context_for_llm(user_input, n_results=3)

# Create prompt
prompt = create_llm_prompt_with_memory(
    system_prompt="You are Jessica, an AI with perfect memory.",
    user_input=user_input,
    relevant_memories=context
)

# Generate response
output = llm(prompt, max_tokens=256, stop=["User:"])
response = output["choices"][0]["text"]

# Store this conversation
memory.store_conversation(user_input, response)
```

### Using with Jessica's Existing Router

```python
# In jessica_core.py or agent_loop.py

from jessica.memory.rag_memory import RAGMemorySystem

class JessicaCore:
    def __init__(self):
        self.memory = RAGMemorySystem(
            persist_directory="./jessica_data/rag_memory"
        )
        # ... rest of init
    
    def process_input(self, user_input):
        # Retrieve relevant context
        context = self.memory.get_context_for_llm(user_input, n_results=3)
        
        # Inject into system prompt or context
        if context:
            enhanced_prompt = f"{self.base_prompt}\n\n{context}\n\nUser: {user_input}"
        else:
            enhanced_prompt = f"{self.base_prompt}\n\nUser: {user_input}"
        
        # Generate response
        response = self.model_router.route_and_generate(enhanced_prompt)
        
        # Store conversation
        self.memory.store_conversation(user_input, response)
        
        return response
```

## 🗂️ Data Storage

All data is stored locally in the specified directory:

```
jessica_rag_memory/
├── chroma.sqlite3          # Vector database
└── [collection_name]/      # Collection data
    ├── data_level0.bin
    ├── header.bin
    ├── index_metadata.pickle
    └── ...
```

**Privacy**: No data ever leaves your machine!

## 🧪 Testing

Run the demo:
```bash
python rag_memory.py
```

Run integration example:
```bash
python rag_integration_example.py
```

## 🔄 Migration from Old Memory System

If you're using the old `long_term_memory.py`:

```python
from jessica.memory.long_term_memory import LongTermMemory
from jessica.memory.rag_memory import RAGMemorySystem

# Initialize both
old_memory = LongTermMemory()
new_memory = RAGMemorySystem()

# Migrate memorable facts
facts = old_memory.retrieve_facts(limit=100)
for fact in facts:
    new_memory.store_memory(
        text=fact["fact"],
        metadata={
            "category": fact["category"],
            "migrated": True
        }
    )
```

## ⚙️ Performance Tips

1. **Choose the right embedding model**:
   - For speed: `all-MiniLM-L6-v2`
   - For quality: `all-mpnet-base-v2`

2. **Limit n_results**: Don't retrieve more memories than needed (3-5 is usually enough)

3. **Use metadata filters**: Narrow down searches to specific topics

4. **Batch storage**: Store memories in batches if processing many at once

5. **Persistence**: ChromaDB automatically persists to disk - no manual saves needed

## 🛠️ Troubleshooting

### "chromadb not installed"
```bash
pip install chromadb
```

### "sentence-transformers not installed"
```bash
pip install sentence-transformers
```

### "No module named 'torch'"
```bash
pip install torch
```

### Slow first run
First time loading embedding model downloads it (~80-400MB). Subsequent runs are fast.

### Memory not persisting
Check that `persist_directory` path is valid and writable.

## 📚 Resources

- **ChromaDB Docs**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **Embedding Model Rankings**: https://huggingface.co/spaces/mteb/leaderboard

## 🎓 How It Works

1. **Embedding**: User input is converted to a 384-dimensional vector using sentence-transformers
2. **Storage**: Vector + text + metadata stored in ChromaDB (local SQLite + Parquet)
3. **Retrieval**: Query embedded, ChromaDB finds most similar vectors using cosine similarity
4. **Context Injection**: Top-k relevant memories formatted and added to LLM prompt
5. **Response**: LLM generates contextually-aware response
6. **Storage**: New conversation stored for future recall

## 📝 License

Part of the Jessica AI project. See main LICENSE file.

## 🤝 Contributing

Improvements welcome! Consider:
- Additional embedding model support
- Memory compression strategies
- Automatic memory summarization
- Time-weighted relevance scoring

---

**Built with ❤️ for fully offline AI**
