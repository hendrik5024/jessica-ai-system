"""
Knowledge Store: Persists external knowledge (facts, documents, web content).
Separates teachable knowledge from episodic memory for better retrieval.
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

KNOWLEDGE_DB = Path(__file__).resolve().parent.parent / "data" / "knowledge.json"


class KnowledgeStore:
    def __init__(self):
        self.path = KNOWLEDGE_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.load(open(self.path, "r", encoding="utf-8"))
            except Exception:
                return self._default()
        return self._default()

    def _default(self) -> dict:
        return {
            "documents": {},      # doc_id -> {title, source, content_chunk, timestamp, tags}
            "facts": {},          # topic -> [fact1, fact2, ...]
            "sources": {},        # source_url -> metadata
            "categories": {},     # category -> [doc_ids]
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_document(self, title: str, content: str, source: str = "user", tags: List[str] = None) -> str:
        """Add a document chunk to knowledge base."""
        doc_id = hashlib.md5(f"{title}{content}".encode()).hexdigest()[:12]
        
        self.data["documents"][doc_id] = {
            "title": title,
            "content": content[:5000],  # Limit size
            "source": source,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "chunk_count": 1
        }
        
        # Index by category/tags
        for tag in (tags or ["general"]):
            if tag not in self.data["categories"]:
                self.data["categories"][tag] = []
            if doc_id not in self.data["categories"][tag]:
                self.data["categories"][tag].append(doc_id)
        
        self.save()
        return doc_id

    def add_fact(self, topic: str, fact: str, source: str = "user"):
        """Add a discrete fact under a topic."""
        if topic not in self.data["facts"]:
            self.data["facts"][topic] = []
        
        self.data["facts"][topic].append({
            "text": fact,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def add_source(self, url: str, metadata: Dict[str, Any] = None):
        """Track an external source (website, API)."""
        self.data["sources"][url] = {
            "metadata": metadata or {},
            "last_fetched": datetime.now().isoformat(),
            "doc_count": 0
        }
        self.save()

    def get_knowledge_context(self, query: str, top_k: int = 5) -> str:
        """Return formatted knowledge snippets for a query topic."""
        lines = []
        
        # Search facts by topic keywords
        for topic, facts_list in self.data["facts"].items():
            if any(word in query.lower() for word in topic.lower().split()):
                for fact in facts_list[:3]:
                    lines.append(f"- {fact['text']}")
        
        # Search documents by title/tags
        for doc_id, doc in list(self.data["documents"].items())[:top_k]:
            for tag in doc.get("tags", []):
                if any(word in query.lower() for word in tag.lower().split()):
                    lines.append(f"[{doc['title']}]: {doc['content'][:200]}...")
                    break
        
        if lines:
            return "Knowledge base:\n" + "\n".join(lines[:10])
        return ""

    def list_categories(self) -> List[str]:
        return list(self.data["categories"].keys())

    def list_topics(self) -> List[str]:
        return list(self.data["facts"].keys())

    def describe(self) -> dict:
        return {
            "documents": len(self.data["documents"]),
            "facts": sum(len(f) for f in self.data["facts"].values()),
            "categories": list(self.data["categories"].keys()),
            "topics": list(self.data["facts"].keys())
        }
