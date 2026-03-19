"""Long-Term Memory (LTM) system for Jessica.

Extracts memorable facts from conversation history every N interactions
and persists them to user_profile.db for future recall.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Dict, List, Optional


class LongTermMemory:
    """Manages extraction and retrieval of memorable facts from conversations."""

    def __init__(self, db_path: str = "user_profile.db", extraction_interval: int = 5):
        self.db_path = db_path
        self.extraction_interval = extraction_interval
        self.interaction_count = 0
        self._init_db()

    def _init_db(self):
        """Initialize the LTM database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memorable_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL,
                    category TEXT,
                    confidence REAL DEFAULT 1.0,
                    source_episode_id TEXT,
                    extracted_at INTEGER,
                    last_accessed INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interaction_tracker (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_interactions INTEGER DEFAULT 0,
                    last_extraction_at INTEGER
                )
            """)
            # Ensure tracker row exists
            conn.execute("""
                INSERT OR IGNORE INTO interaction_tracker (id, total_interactions, last_extraction_at)
                VALUES (1, 0, 0)
            """)
            conn.commit()

    def increment_interaction(self) -> int:
        """Increment interaction count and return current count."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE interaction_tracker 
                SET total_interactions = total_interactions + 1
                WHERE id = 1
            """)
            result = conn.execute("SELECT total_interactions FROM interaction_tracker WHERE id = 1").fetchone()
            self.interaction_count = result[0] if result else 0
            conn.commit()
        return self.interaction_count

    def should_extract(self) -> bool:
        """Check if it's time to extract memorable facts."""
        return self.interaction_count > 0 and self.interaction_count % self.extraction_interval == 0

    def extract_facts(self, recent_episodes: List[Dict], model_router) -> List[str]:
        """Use LLM to extract memorable facts from recent conversation history.
        
        Returns a list of extracted facts.
        """
        if not recent_episodes:
            return []

        # Build context from recent episodes
        context_lines = []
        for ep in recent_episodes[-10:]:  # Last 10 interactions
            user_input = ep.get("input_text", "").strip()
            output = ep.get("output", {})
            reply = ""
            if isinstance(output, dict):
                reply = output.get("reply", str(output))
            else:
                reply = str(output)
            
            if user_input:
                context_lines.append(f"User: {user_input}")
            if reply:
                context_lines.append(f"Jessica: {reply}")

        conversation = "\n".join(context_lines)

        prompt = f"""Analyze this conversation and extract memorable facts about the user that should be remembered long-term.

Conversation:
{conversation}

Extract facts about:
- User preferences (likes, dislikes, habits)
- Personal information (name, location, occupation, relationships)
- Goals and aspirations
- Important events or context
- Recurring topics or interests

Return ONLY a JSON array of facts, each as a string. Format:
["fact 1", "fact 2", "fact 3"]

If no memorable facts are found, return an empty array: []

Memorable Facts:"""

        try:
            response = model_router.generate(prompt, mode="chat")
            # Extract JSON from response
            response = response.strip()
            
            # Try to find JSON array in response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                facts = json.loads(json_str)
                if isinstance(facts, list):
                    return [str(f).strip() for f in facts if f]
        except Exception as e:
            print(f"[LTM] Fact extraction failed: {e}")
        
        return []

    def save_facts(self, facts: List[str], category: str = "general", source_episode_id: Optional[str] = None):
        """Save extracted facts to the database."""
        if not facts:
            return

        timestamp = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            for fact in facts:
                # Check for duplicates
                existing = conn.execute(
                    "SELECT id FROM memorable_facts WHERE fact = ? LIMIT 1", 
                    (fact,)
                ).fetchone()
                
                if not existing:
                    conn.execute("""
                        INSERT INTO memorable_facts 
                        (fact, category, confidence, source_episode_id, extracted_at, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (fact, category, 1.0, source_episode_id, timestamp, timestamp))
            
            conn.execute("""
                UPDATE interaction_tracker 
                SET last_extraction_at = ?
                WHERE id = 1
            """, (timestamp,))
            conn.commit()

        print(f"[LTM] Saved {len(facts)} memorable facts")

    def retrieve_facts(self, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Retrieve memorable facts, optionally filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute("""
                    SELECT id, fact, category, confidence, extracted_at
                    FROM memorable_facts
                    WHERE category = ?
                    ORDER BY confidence DESC, last_accessed DESC
                    LIMIT ?
                """, (category, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT id, fact, category, confidence, extracted_at
                    FROM memorable_facts
                    ORDER BY confidence DESC, last_accessed DESC
                    LIMIT ?
                """, (limit,)).fetchall()

            facts = []
            for row in rows:
                facts.append({
                    "id": row[0],
                    "fact": row[1],
                    "category": row[2],
                    "confidence": row[3],
                    "extracted_at": row[4],
                })
                # Update last_accessed
                conn.execute(
                    "UPDATE memorable_facts SET last_accessed = ? WHERE id = ?",
                    (int(time.time()), row[0])
                )
            
            conn.commit()
            return facts

    def get_context_summary(self, limit: int = 5) -> str:
        """Get a formatted summary of memorable facts for prompt injection."""
        facts = self.retrieve_facts(limit=limit)
        if not facts:
            return ""

        lines = ["Long-term memory (memorable facts):"]
        for fact in facts:
            lines.append(f"- {fact['fact']}")
        
        return "\n".join(lines)

    def get_statistics(self) -> Dict:
        """Get statistics about the LTM system."""
        with sqlite3.connect(self.db_path) as conn:
            total_facts = conn.execute("SELECT COUNT(*) FROM memorable_facts").fetchone()[0]
            total_interactions = conn.execute(
                "SELECT total_interactions FROM interaction_tracker WHERE id = 1"
            ).fetchone()[0]
            last_extraction = conn.execute(
                "SELECT last_extraction_at FROM interaction_tracker WHERE id = 1"
            ).fetchone()[0]
            
            return {
                "total_facts": total_facts,
                "total_interactions": total_interactions,
                "last_extraction_at": last_extraction,
                "next_extraction_in": self.extraction_interval - (total_interactions % self.extraction_interval),
            }
