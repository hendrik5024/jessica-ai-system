def can_handle(intent):
    return intent.get("intent") == "chat"


def run(intent, context, relevant, manager):
    text = intent["text"]
    
    # Build memory context from recent episodes and semantic hits
    context_lines = []
    
    # Recent conversation history
    if context:
        context_lines.append("Recent conversation:")
        for ep in context[:3]:
            user_input = (ep.get("input_text") or "").strip()
            if user_input:
                context_lines.append(f"- {user_input}")
    
    # Semantically similar past interactions
    if relevant:
        context_lines.append("\nRelevant past context:")
        for hit in relevant[:2]:
            meta = hit.get("meta", {})
            score = hit.get("score", 0)
            if score > 0.5:  # Only include high-confidence matches
                context_lines.append(f"- {meta}")
    
    # User profile / known entities
    try:
        from jessica.memory.user_profile import UserProfile
        profile = UserProfile()
        profile.extract_entities(text)
        profile.save()
        
        entities = profile.get_known_entities()
        if entities and "No entities" not in entities:
            context_lines.append(f"\nKnown entities:\n{entities}")
    except Exception as e:
        print(f"[chat_skill] profile error: {e}")

    # Knowledge base context
    try:
        from jessica.memory.knowledge_store import KnowledgeStore
        ks = KnowledgeStore()
        knowledge_ctx = ks.get_knowledge_context(text, top_k=3)
        if knowledge_ctx:
            context_lines.append(f"\n{knowledge_ctx}")
    except Exception as e:
        print(f"[chat_skill] knowledge error: {e}")

    memory_block = "\n".join(context_lines) if context_lines else ""
    
    prompt = f"""You are Jessica, an offline AI assistant with memory of past conversations and a knowledge base.
Your name is Jessica (never Phi). Always speak as Jessica and avoid referring to the model name.

{f"Context from memory:{chr(10)}{memory_block}{chr(10)}" if memory_block else ""}
Rules:
- Reply ONLY to the user's last message.
- Use context from memory to reference past conversations and relationships.
- If the user mentions a name you've heard before, acknowledge that you remember.
- Use knowledge base facts when relevant to the user's question.
- Do NOT invent additional user messages or a multi-turn transcript.
- Do NOT include prefixes like 'User:' or 'Assistant:' in your reply.
- Keep the reply concise unless the user asks for detail.

User: {text}
"""

    return manager.model_router.chat_model.generate(prompt, max_tokens=100, temperature=0.7)  # Reduced from 160
