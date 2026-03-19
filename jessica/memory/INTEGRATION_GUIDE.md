# Integration Guide: Adding RAG Memory to Your Existing Jessica System

This guide shows exactly where to add the RAG memory code to your current Jessica implementation.

## Files to Modify

1. **`jessica/agent_loop.py`** - Main conversation loop
2. **`jessica/jessica_core.py`** - Core processing (if separate)
3. **`jessica/requirements.txt`** - Add new dependencies

---

## Step 1: Update Requirements

### File: `jessica/requirements.txt`

**ADD these lines:**
```txt
# RAG Memory System (add to end of file)
chromadb>=0.4.22
sentence-transformers>=2.2.2
```

**Then install:**
```bash
cd jessica
pip install chromadb sentence-transformers
```

---

## Step 2: Modify Agent Loop

### File: `jessica/agent_loop.py`

#### A. Add Import (at top of file)

**Find the imports section and ADD:**
```python
from jessica.memory.rag_memory import RAGMemorySystem
```

**Example - your imports might look like:**
```python
# Existing imports
from jessica.nlp.intent_parser import IntentParser
from jessica.skills.skill_router import SkillRouter
from jessica.memory.context_manager import ContextManager
# ... other imports ...

# ADD THIS:
from jessica.memory.rag_memory import RAGMemorySystem
```

#### B. Initialize in `__init__` method

**Find your `__init__` method and ADD memory initialization:**

```python
class AgentLoop:
    def __init__(self):
        # Existing initialization
        self.intent_parser = IntentParser()
        self.skill_router = SkillRouter()
        self.context = ContextManager()
        # ... other components ...
        
        # ADD THIS - RAG Memory System:
        self.rag_memory = RAGMemorySystem(
            persist_directory="./jessica_data/rag_memory",
            collection_name="jessica_conversations",
            embedding_model="all-MiniLM-L6-v2"
        )
        print("✓ RAG long-term memory enabled")
```

#### C. Modify Main Processing Loop

**Find your main conversation processing method and MODIFY it:**

**Before (typical structure):**
```python
def process_input(self, user_input: str) -> str:
    # Parse intent
    intent = self.intent_parser.parse(user_input)
    
    # Route to skill
    skill_output = self.skill_router.route(intent, user_input)
    
    # Generate response
    response = self.generate_response(skill_output, user_input)
    
    # Store context
    self.context.add_exchange(user_input, response)
    
    return response
```

**After (with RAG memory):**
```python
def process_input(self, user_input: str) -> str:
    # 1. RETRIEVE relevant memories (ADD THIS)
    memory_context = self.rag_memory.get_context_for_llm(
        user_input, 
        n_results=3
    )
    
    # Parse intent
    intent = self.intent_parser.parse(user_input)
    
    # Route to skill
    skill_output = self.skill_router.route(intent, user_input)
    
    # 2. INJECT memory into prompt (MODIFY THIS)
    response = self.generate_response(
        skill_output, 
        user_input,
        memory_context=memory_context  # Pass memory context
    )
    
    # Store context
    self.context.add_exchange(user_input, response)
    
    # 3. STORE conversation in RAG memory (ADD THIS)
    self.rag_memory.store_conversation(
        user_input=user_input,
        assistant_response=response,
        metadata={
            "intent": intent.get("type", "unknown"),
            "skill": skill_output.get("skill_used", "unknown")
        }
    )
    
    return response
```

#### D. Modify Response Generation

**Find your `generate_response` method and MODIFY to accept memory:**

**Before:**
```python
def generate_response(self, skill_output, user_input):
    prompt = f"{self.system_prompt}\n\nUser: {user_input}\nJessica:"
    response = self.model_router.route_and_generate(prompt)
    return response
```

**After:**
```python
def generate_response(self, skill_output, user_input, memory_context=""):
    # Build prompt with memory context
    prompt_parts = [self.system_prompt]
    
    # Add memory context if available
    if memory_context:
        prompt_parts.append(memory_context)
    
    # Add current input
    prompt_parts.append(f"\nUser: {user_input}\nJessica:")
    
    prompt = "\n".join(prompt_parts)
    response = self.model_router.route_and_generate(prompt)
    return response
```

---

## Step 3: Alternative - Modify Jessica Core

If you have a separate `jessica_core.py` file:

### File: `jessica/jessica_core.py`

#### Add to Imports:
```python
from jessica.memory.rag_memory import RAGMemorySystem
```

#### In `__init__`:
```python
class JessicaCore:
    def __init__(self, model_router, ...):
        self.model_router = model_router
        # ... other init ...
        
        # Add RAG memory
        self.memory = RAGMemorySystem(
            persist_directory="./jessica_data/rag_memory"
        )
```

#### In Main Processing Method:
```python
def chat(self, user_input):
    # Get memories
    context = self.memory.get_context_for_llm(user_input, n_results=3)
    
    # Build prompt
    if context:
        full_prompt = f"{self.system_prompt}\n{context}\n\nUser: {user_input}"
    else:
        full_prompt = f"{self.system_prompt}\n\nUser: {user_input}"
    
    # Generate
    response = self.model_router.route_and_generate(full_prompt)
    
    # Store
    self.memory.store_conversation(user_input, response)
    
    return response
```

---

## Complete Example: Minimal Integration

Here's the **absolute minimum** code you need to add:

```python
# 1. Import (top of file)
from jessica.memory.rag_memory import RAGMemorySystem

# 2. Initialize (in __init__)
self.memory = RAGMemorySystem()

# 3. Use (in your main loop)
def process(self, user_input):
    # Get memories
    context = self.memory.get_context_for_llm(user_input, n_results=3)
    
    # Generate with memory
    prompt = f"{self.system_prompt}\n{context}\n\nUser: {user_input}"
    response = your_llm_generate(prompt)
    
    # Store for next time
    self.memory.store_conversation(user_input, response)
    
    return response
```

That's it! Just **3 additions** to your code.

---

## Testing Your Integration

### 1. Basic Test

Add this test function to verify it works:

```python
def test_rag_memory():
    """Test RAG memory integration."""
    print("Testing RAG memory...")
    
    # Initialize your Jessica
    jessica = AgentLoop()  # or JessicaCore()
    
    # Test 1: Store a fact
    response1 = jessica.process_input("I love Python programming")
    print(f"Response 1: {response1[:100]}...")
    
    # Test 2: See if it remembers
    response2 = jessica.process_input("What programming language do I like?")
    print(f"Response 2: {response2[:100]}...")
    
    # Check memory stats
    stats = jessica.rag_memory.get_memory_stats()
    print(f"Memories stored: {stats['total_memories']}")
    
    print("✓ RAG memory working!")
```

### 2. Run Your System

```bash
python run_jessica.py
```

**Test conversation:**
```
You: My name is Alex and I work as a software engineer
Jessica: Nice to meet you, Alex! ...

You: What do you know about me?
Jessica: You're Alex, and you work as a software engineer! ...
```

---

## Configuration Options

### Adjust Number of Memories Retrieved

```python
# In your process_input method, change n_results:
context = self.rag_memory.get_context_for_llm(
    user_input,
    n_results=5  # Get top 5 instead of 3
)
```

### Add Metadata Tagging

```python
# When storing, add useful metadata:
self.rag_memory.store_conversation(
    user_input=user_input,
    assistant_response=response,
    metadata={
        "intent": intent_type,
        "emotion": detected_emotion,
        "topic": conversation_topic,
        "skill_used": skill_name,
        "timestamp": datetime.now().isoformat()
    }
)
```

### Filter by Metadata

```python
# Only retrieve work-related memories:
context = self.rag_memory.query_memory(
    user_input,
    n_results=3,
    filter_metadata={"topic": "work"}
)
```

---

## Troubleshooting

### Issue: "chromadb not installed"
**Fix:**
```bash
pip install chromadb sentence-transformers
```

### Issue: Slow first run
**Reason:** Downloading embedding model (80MB) on first use
**Fix:** Wait for download, then it's fast

### Issue: Out of memory
**Fix:** Use a smaller embedding model:
```python
self.memory = RAGMemorySystem(
    embedding_model="all-MiniLM-L6-v2"  # Smallest, fastest
)
```

### Issue: Not finding relevant memories
**Fix:** Lower similarity threshold or increase n_results:
```python
context = self.memory.get_context_for_llm(user_input, n_results=5)
```

---

## Performance Tips

1. **Cache embedding model** - It's loaded once and stays in memory
2. **Limit n_results** - 3-5 is optimal, more is slower
3. **Use metadata filters** - Narrows search space
4. **Batch storage** - If processing many at once
5. **Regular cleanup** - Delete very old memories if needed

---

## What Happens Under the Hood

```
User Input
    ↓
Embed user input → Vector (384 dimensions)
    ↓
Search ChromaDB → Find top 3 most similar vectors
    ↓
Retrieve associated text → Past conversations
    ↓
Format as context → "=== RELEVANT MEMORIES ==="
    ↓
Inject into LLM prompt → "You are Jessica... [memories] ... User: ..."
    ↓
LLM generates response → Uses memory for context
    ↓
Store new conversation → Embed and save to ChromaDB
    ↓
Return response to user
```

---

## Summary Checklist

- [ ] Install: `pip install chromadb sentence-transformers`
- [ ] Import: `from jessica.memory.rag_memory import RAGMemorySystem`
- [ ] Initialize: `self.memory = RAGMemorySystem()`
- [ ] Retrieve: `context = self.memory.get_context_for_llm(user_input)`
- [ ] Use: Inject `context` into your prompt
- [ ] Store: `self.memory.store_conversation(user_input, response)`
- [ ] Test: Run Jessica and verify memory recall

**That's it!** Your Jessica AI now has long-term memory! 🎉

---

## Need Help?

- See `rag_integration_example.py` for complete working example
- Read `RAG_MEMORY_README.md` for detailed API reference
- Check `RAG_IMPLEMENTATION_SUMMARY.md` for overview

---

**Integration Time: ~15 minutes**  
**Lines of Code to Add: ~10-20**  
**Benefit: Infinite memory! 🧠**
