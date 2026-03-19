"""
Background curiosity worker for idle time.
Scans recent activity and docs folder to surface follow-up when user returns.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, List, Dict


class BackgroundCuriosity:
    def __init__(self, min_idle_seconds: int = 900, cooldown_seconds: int = 3600):
        self.min_idle_seconds = min_idle_seconds
        self.cooldown_seconds = cooldown_seconds
        self.last_run = 0.0

    def maybe_research(self, system_state, context_manager) -> Optional[Dict]:
        now = time.time()
        if (now - self.last_run) < self.cooldown_seconds:
            return None

        idle_seconds = max(system_state.keyboard_idle_seconds, system_state.mouse_idle_seconds)
        if idle_seconds < self.min_idle_seconds:
            return None

        topics = self._extract_topics(context_manager)
        # fallback to focus apps / likely next apps
        if not topics:
            suggestion = context_manager.profile.get_context_suggestion() if context_manager else {}
            topics = suggestion.get("likely_next_apps") or []

        self.last_run = now
        if not topics:
            return None

        # Keep lightweight: just return the topics as a queued thought
        return {
            "message": "While you were away, I queued a few things to revisit.",
            "topics": topics[:3],
            "idle_seconds": idle_seconds,
        }

    def _extract_topics(self, context_manager) -> List[str]:
        if not context_manager:
            return []
        suggestion = context_manager.profile.get_context_suggestion()
        topics = []
        if suggestion.get("current_app"):
            topics.append(suggestion.get("current_app"))
        topics.extend(suggestion.get("likely_next_apps") or [])
        
        # Also scan docs folder for recent files
        doc_topics = self._scan_docs_folder()
        topics.extend(doc_topics)
        
        return [t for t in topics if t]
    
    def _scan_docs_folder(self, max_files: int = 3) -> List[str]:
        """Scan docs folder for recently modified files as potential topics."""
        # Scan project root docs folder (not jessica/docs)
        docs_path = Path(__file__).parent.parent.parent / "docs"
        if not docs_path.exists():
            return []
        
        try:
            # Get .md files, sorted by modification time (most recent first)
            md_files = list(docs_path.glob("*.md"))
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Extract topics from file names (remove extension, convert underscores)
            topics = []
            for f in md_files[:max_files]:
                topic = f.stem.replace("_", " ").lower()
                # Only suggest if file was modified in last 7 days
                age_days = (time.time() - f.stat().st_mtime) / 86400
                if age_days < 7:
                    topics.append(topic)
            
            return topics
        except Exception:
            return []

