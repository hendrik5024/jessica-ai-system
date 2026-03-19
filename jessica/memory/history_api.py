"""
Conversation history API: Browser-friendly endpoint to view past chats.
"""
from jessica.memory.sqlite_store import EpisodicStore
from jessica.memory.embeddings_index import EmbeddingsIndex
from jessica.memory.user_profile import UserProfile

def get_recent_history(limit: int = 20):
    """Fetch recent conversations."""
    db = EpisodicStore("jessica_data.db")
    return db.recent(limit)


def search_history(query: str, top_k: int = 10):
    """Search past conversations by semantic similarity."""
    emb = EmbeddingsIndex("jessica_data_embeddings")
    results = []
    for id_, score in emb.search(query, top_k=top_k):
        meta = emb.get_meta(id_)
        results.append({
            "id": id_,
            "score": score,
            "meta": meta
        })
    return results


def get_user_profile():
    """Get user profile with known names and places."""
    profile = UserProfile()
    return {
        "user_name": profile.data.get("user_name"),
        "names_mentioned": profile.data.get("names_mentioned", {}),
        "places": profile.data.get("places", {}),
        "relationships": profile.data.get("relationships", {}),
        "preferences": profile.data.get("preferences", {})
    }


def set_user_name(name: str):
    """Explicitly set the user's name."""
    profile = UserProfile()
    profile.set_user_name(name)
    profile.save()


def add_relationship(name: str, relation: str):
    """Add a known relationship (e.g., 'Alice is my sister')."""
    profile = UserProfile()
    profile.set_relationship(name, relation)
    profile.save()
