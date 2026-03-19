"""
Episodic Milestone System - Tracks achievements and shared milestones.

Integrates with ChromaDB (RAG 2.0) to store and retrieve milestones:
- Project starts
- Major bug fixes
- Goal completions
- Shared achievements

Milestones are embedded as vectors for semantic retrieval and can be
injected into conversations to create continuity and celebrate progress.
"""
from __future__ import annotations

import sqlite3
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger("jessica.milestones")


class MilestoneStore:
    """
    SQLite-based storage for milestone metadata.
    
    Milestones include:
    - id: Unique identifier
    - ts: Timestamp of milestone
    - title: Human-readable milestone name
    - type: 'project_start', 'bug_fix', 'goal_complete', 'feature_ship', 'achievement'
    - description: Detailed description
    - context: Associated project/file/task
    - embedding_id: Reference to ChromaDB embedding
    - meta_json: Additional metadata
    """
    
    def __init__(self, db_path: str = "jessica_data.db"):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        """Initialize milestone table if not exists"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    context TEXT,
                    embedding_id TEXT,
                    meta_json TEXT,
                    created_at INTEGER DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_milestones_ts ON milestones(ts DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_milestones_type ON milestones(type)
            """)
            conn.commit()
    
    def add_milestone(
        self,
        title: str,
        milestone_type: str,
        description: str = "",
        context: str = "",
        embedding_id: Optional[str] = None,
        meta: Optional[Dict] = None
    ) -> int:
        """
        Add a new milestone to storage.
        
        Args:
            title: Short milestone name (e.g., "Completed Authentication Module")
            milestone_type: 'project_start', 'bug_fix', 'goal_complete', 'feature_ship', 'achievement'
            description: Longer description of the milestone
            context: Associated project/file/task
            embedding_id: ChromaDB embedding ID (added after embedding)
            meta: Additional metadata dict
        
        Returns:
            Milestone ID
        """
        ts = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO milestones 
                (ts, title, type, description, context, embedding_id, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ts,
                title,
                milestone_type,
                description,
                context,
                embedding_id,
                json.dumps(meta or {})
            ))
            conn.commit()
            cursor = conn.execute("SELECT last_insert_rowid()")
            return cursor.fetchone()[0]
    
    def get_milestone(self, milestone_id: int) -> Optional[Dict]:
        """Get a specific milestone by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, ts, title, type, description, context, embedding_id, meta_json
                FROM milestones WHERE id = ?
            """, (milestone_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_dict(row)
    
    def get_milestones(
        self,
        limit: int = 10,
        milestone_type: Optional[str] = None,
        context: Optional[str] = None
    ) -> List[Dict]:
        """Get recent milestones, optionally filtered by type or context"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT id, ts, title, type, description, context, embedding_id, meta_json FROM milestones WHERE 1=1"
            params = []
            
            if milestone_type:
                query += " AND type = ?"
                params.append(milestone_type)
            
            if context:
                query += " AND context = ?"
                params.append(context)
            
            query += " ORDER BY ts DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_old_milestones(self, days_ago: int = 30, limit: int = 50) -> List[Dict]:
        """Get milestones from exactly N days ago (for anniversary mentions)"""
        cutoff_ts = int(time.time()) - (days_ago * 86400)
        cutoff_ts_end = cutoff_ts + 86400  # Within a 24-hour window
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, ts, title, type, description, context, embedding_id, meta_json
                FROM milestones
                WHERE ts BETWEEN ? AND ?
                ORDER BY ts DESC
                LIMIT ?
            """, (cutoff_ts, cutoff_ts_end, limit))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_milestones_in_range(
        self,
        days_ago_min: int,
        days_ago_max: int,
        limit: int = 50
    ) -> List[Dict]:
        """Get milestones from a time range (e.g., 20-30 days ago)"""
        now_ts = int(time.time())
        min_ts = now_ts - (days_ago_max * 86400)
        max_ts = now_ts - (days_ago_min * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, ts, title, type, description, context, embedding_id, meta_json
                FROM milestones
                WHERE ts BETWEEN ? AND ?
                ORDER BY ts DESC
                LIMIT ?
            """, (min_ts, max_ts, limit))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def count_milestones(self) -> int:
        """Count total milestones"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM milestones")
            return cursor.fetchone()[0]
    
    def _row_to_dict(self, row: tuple) -> Dict:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'ts': row[1],
            'title': row[2],
            'type': row[3],
            'description': row[4],
            'context': row[5],
            'embedding_id': row[6],
            'meta': json.loads(row[7] or '{}'),
            'date': datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d'),
            'formatted_date': datetime.fromtimestamp(row[1]).strftime('%B %d, %Y')
        }


class MilestoneEmbedder:
    """
    Embeds milestones into ChromaDB for semantic retrieval.
    
    Converts milestone objects into vectors for similarity search
    and stores them for later recall in conversations.
    """
    
    def __init__(self, rag_memory_system=None):
        """
        Initialize embedder.
        
        Args:
            rag_memory_system: RAGMemorySystem instance (optional, for ChromaDB access)
        """
        self.rag = rag_memory_system
        self.milestone_collection = None
        
        if self.rag:
            # Create separate collection for milestones
            self.milestone_collection = self.rag.client.get_or_create_collection(
                name="milestones",
                embedding_function=self.rag.embedding_function,
                metadata={"description": "Achievement milestones and shared accomplishments"}
            )
    
    def embed_milestone(
        self,
        milestone_id: int,
        title: str,
        description: str = "",
        context: str = "",
        milestone_type: str = "achievement"
    ) -> Optional[str]:
        """
        Embed a milestone into ChromaDB vector store.
        
        Args:
            milestone_id: ID from MilestoneStore
            title: Milestone title
            description: Full description
            context: Associated project/context
            milestone_type: Type of milestone
        
        Returns:
            Document ID in ChromaDB
        """
        if not self.milestone_collection:
            logger.warning("RAG memory system not available, skipping embedding")
            return None
        
        # Create rich document for embedding
        doc_id = f"milestone_{milestone_id}"
        document = self._create_milestone_document(
            title, description, context, milestone_type
        )
        
        # Add to ChromaDB
        try:
            self.milestone_collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[{
                    'milestone_id': str(milestone_id),
                    'title': title,
                    'type': milestone_type,
                    'context': context,
                    'timestamp': str(int(time.time()))
                }]
            )
            logger.info(f"Embedded milestone {milestone_id}: {title}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to embed milestone: {e}")
            return None
    
    def _create_milestone_document(
        self,
        title: str,
        description: str,
        context: str,
        milestone_type: str
    ) -> str:
        """Create embedding document from milestone data"""
        parts = [f"Milestone: {title}"]
        
        if description:
            parts.append(f"Details: {description}")
        
        if context:
            parts.append(f"Project: {context}")
        
        # Add type-specific context
        type_hints = {
            'project_start': "Started a new project or initiative",
            'bug_fix': "Fixed a significant bug or issue",
            'goal_complete': "Completed an important goal or objective",
            'feature_ship': "Shipped a new feature or functionality",
            'achievement': "Notable achievement or accomplishment"
        }
        
        if milestone_type in type_hints:
            parts.append(f"Type: {type_hints[milestone_type]}")
        
        return " | ".join(parts)
    
    def retrieve_similar_milestones(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Retrieve milestones similar to a query.
        
        Args:
            query: Search query (can be natural language)
            n_results: Number of results to return
        
        Returns:
            List of milestone dicts with similarity scores
        """
        if not self.milestone_collection:
            return []
        
        try:
            results = self.milestone_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            milestones = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i] if results['metadatas'] else {}
                    milestones.append({
                        'document': doc,
                        'metadata': meta,
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return milestones
        except Exception as e:
            logger.error(f"Failed to retrieve milestones: {e}")
            return []


class MilestoneRecaller:
    """
    Recalls milestones for mention in conversations.
    
    Implements logic to occasionally pull old milestones and
    inject them into prompts for continuity and celebration.
    """
    
    def __init__(self, milestone_store: MilestoneStore, embedder: MilestoneEmbedder = None):
        self.store = milestone_store
        self.embedder = embedder
        self.last_recall_ts = 0
        self.recall_cooldown = 600  # 10 minutes between recalls
    
    def maybe_recall_milestone(self, min_days_old: int = 30) -> Optional[Dict]:
        """
        Randomly decide to recall a milestone if conditions are met.
        
        Respects cooldown to avoid spam.
        
        Args:
            min_days_old: Only recall milestones at least this old
        
        Returns:
            Milestone dict or None
        """
        now = time.time()
        
        # Check cooldown
        if (now - self.last_recall_ts) < self.recall_cooldown:
            return None
        
        # Random chance to recall (20%)
        if random.random() > 0.2:
            return None
        
        # Get old milestones
        milestones = self.store.get_milestones_in_range(
            days_ago_min=min_days_old,
            days_ago_max=365,  # Up to a year old
            limit=50
        )
        
        if not milestones:
            return None
        
        # Select random milestone
        milestone = random.choice(milestones)
        self.last_recall_ts = now
        
        logger.info(f"Recalled milestone: {milestone['title']}")
        return milestone
    
    def format_milestone_mention(self, milestone: Dict) -> str:
        """
        Format a milestone for natural conversation insertion.
        
        Returns a sentence that can be added to conversations.
        """
        days_ago = (int(time.time()) - milestone['ts']) // 86400
        title = milestone['title']
        context = milestone.get('context', '')
        
        # Create natural phrasing
        templates = [
            f"It's been {days_ago} days since {title.lower()}—look how far we've come!",
            f"Remember when we {title.lower()}? That was {days_ago} days ago.",
            f"Looking back, {days_ago} days ago we accomplished: {title}",
            f"Fun fact: {days_ago} days ago we {title.lower()}!",
            f"Time flies! {days_ago} days have passed since we {title.lower()}.",
        ]
        
        if context:
            templates.extend([
                f"It's been {days_ago} days since we finished {context}—remember {title.lower()}?",
                f"On this day {days_ago} days ago, we {title.lower()} in {context}.",
            ])
        
        return random.choice(templates)
    
    def get_random_achievement_summary(self, limit: int = 3) -> str:
        """
        Get a quick summary of recent achievements for conversation.
        
        Returns a paragraph suitable for insertion into responses.
        """
        milestones = self.store.get_milestones(limit=limit)
        
        if not milestones:
            return "We're just getting started on this journey."
        
        achievements = [m['title'] for m in milestones]
        
        if len(achievements) == 1:
            return f"Recently, we accomplished: {achievements[0]}."
        elif len(achievements) == 2:
            return f"Recently, we've made progress on: {achievements[0]} and {achievements[1]}."
        else:
            last = achievements[-1]
            rest = ", ".join(achievements[:-1])
            return f"We've been productive lately! We've worked on: {rest}, and most recently {last}."


# Singleton instances
_milestone_store = None
_milestone_embedder = None
_milestone_recaller = None


def get_milestone_store() -> MilestoneStore:
    """Get or create milestone store singleton"""
    global _milestone_store
    if _milestone_store is None:
        _milestone_store = MilestoneStore()
    return _milestone_store


def get_milestone_embedder(rag_memory=None) -> MilestoneEmbedder:
    """Get or create milestone embedder singleton"""
    global _milestone_embedder
    if _milestone_embedder is None:
        _milestone_embedder = MilestoneEmbedder(rag_memory)
    return _milestone_embedder


def get_milestone_recaller() -> MilestoneRecaller:
    """Get or create milestone recaller singleton"""
    global _milestone_recaller
    if _milestone_recaller is None:
        store = get_milestone_store()
        embedder = get_milestone_embedder()
        _milestone_recaller = MilestoneRecaller(store, embedder)
    return _milestone_recaller
