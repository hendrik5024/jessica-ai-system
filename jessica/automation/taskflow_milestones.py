"""
TaskFlow Milestone Integration - Tracks task completion as shared achievements.

Monitors task completion and automatically creates milestone entries
when tasks are marked complete in TaskFlow.
"""
from __future__ import annotations

import logging
import json
from typing import Dict, Optional, Any
from pathlib import Path

from jessica.memory.milestone_system import (
    get_milestone_store,
    get_milestone_embedder,
    MilestoneStore,
    MilestoneEmbedder
)

logger = logging.getLogger("jessica.taskflow_milestones")


class TaskFlowMilestoneTracker:
    """
    Monitors TaskFlow for task completion and creates milestones.
    
    Watches the .jessica_tasks.json queue for completion events and
    automatically records them as "Shared Achievements" in the milestone system.
    """
    
    def __init__(self, rag_memory=None):
        self.store = get_milestone_store()
        self.embedder = get_milestone_embedder(rag_memory)
        self.rag = rag_memory
        self.last_processed_tasks = set()  # Track processed task IDs
    
    def process_task_completion(self, task: Dict[str, Any]) -> Optional[int]:
        """
        Process a task completion and create milestone.
        
        Args:
            task: Task dict from TaskFlow queue
                Expected keys:
                - 'id': Unique task ID
                - 'title': Task title
                - 'type': Task type (e.g., 'vscode.create_file')
                - 'status': 'completed' or 'done'
                - 'context': Optional project/file context
                - 'description': Optional task description
        
        Returns:
            Milestone ID if created, None otherwise
        """
        task_id = task.get('id')
        status = task.get('status', '').lower()
        
        # Only process completed tasks
        if status not in ['completed', 'done']:
            return None
        
        # Avoid reprocessing
        if task_id in self.last_processed_tasks:
            return None
        
        self.last_processed_tasks.add(task_id)
        
        # Extract milestone details
        title = task.get('title', 'Task completed')
        description = task.get('description', '')
        context = task.get('context', '')
        task_type = task.get('type', 'task')
        
        # Determine milestone type based on task type
        milestone_type = self._classify_milestone_type(task_type, title)
        
        # Create more interesting title
        rich_title = self._enrich_title(title, task_type)
        
        # Save to milestone store
        logger.info(f"Creating milestone for task: {title}")
        milestone_id = self.store.add_milestone(
            title=rich_title,
            milestone_type=milestone_type,
            description=description or f"Completed: {title}",
            context=context,
            meta={
                'task_id': task_id,
                'task_type': task_type,
                'original_title': title
            }
        )
        
        # Embed in ChromaDB
        embedding_id = self.embedder.embed_milestone(
            milestone_id=milestone_id,
            title=rich_title,
            description=description or f"Completed: {title}",
            context=context,
            milestone_type=milestone_type
        )
        
        # Update embedding_id in store
        if embedding_id:
            with get_milestone_store()._get_connection() as conn:
                conn.execute(
                    "UPDATE milestones SET embedding_id = ? WHERE id = ?",
                    (embedding_id, milestone_id)
                )
                conn.commit()
        
        return milestone_id
    
    def _classify_milestone_type(self, task_type: str, title: str) -> str:
        """Classify task completion as milestone type"""
        task_lower = task_type.lower()
        title_lower = title.lower()
        
        # Bug fixes
        if any(word in task_lower or word in title_lower 
               for word in ['bug', 'fix', 'issue', 'error']):
            return 'bug_fix'
        
        # Feature launches
        if any(word in task_lower or word in title_lower
               for word in ['feature', 'launch', 'ship', 'release', 'deploy']):
            return 'feature_ship'
        
        # Goal/milestone completions
        if any(word in title_lower
               for word in ['goal', 'objective', 'target', 'complete', 'finish']):
            return 'goal_complete'
        
        # Project starts
        if any(word in title_lower
               for word in ['start', 'begin', 'init', 'setup', 'initialize']):
            return 'project_start'
        
        # Default
        return 'achievement'
    
    def _enrich_title(self, original: str, task_type: str) -> str:
        """Make task title more engaging for milestones"""
        # Remove common prefixes
        title = original.strip()
        for prefix in ['completed', 'finished', 'done', 'task:', '[task]']:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Add context based on type
        if 'bug' in task_type.lower() or 'fix' in title.lower():
            return f"Fixed: {title}"
        elif 'feature' in task_type.lower() or 'ship' in title.lower():
            return f"Shipped: {title}"
        elif 'delete' in task_type.lower():
            return f"Cleaned up: {title}"
        elif 'refactor' in title.lower():
            return f"Refactored: {title}"
        
        return title
    
    def track_file_milestone(
        self,
        file_path: str,
        action: str = 'created',
        context: str = ''
    ) -> Optional[int]:
        """
        Manually track a file-based milestone.
        
        Args:
            file_path: Path to the file
            action: 'created', 'completed', 'shipped', 'refactored'
            context: Project context
        
        Returns:
            Milestone ID
        """
        file_name = Path(file_path).name
        title = f"{action.capitalize()}: {file_name}"
        
        return self.store.add_milestone(
            title=title,
            milestone_type='goal_complete' if action == 'completed' else 'feature_ship',
            description=f"{action} {file_path}",
            context=context,
            meta={'file_path': file_path, 'action': action}
        )
    
    def track_goal_completion(
        self,
        goal_title: str,
        description: str = '',
        context: str = ''
    ) -> int:
        """
        Manually track a goal completion milestone.
        
        Args:
            goal_title: Title of completed goal
            description: How it was completed
            context: Associated project/domain
        
        Returns:
            Milestone ID
        """
        return self.store.add_milestone(
            title=f"Completed: {goal_title}",
            milestone_type='goal_complete',
            description=description,
            context=context,
            meta={'goal': goal_title}
        )
    
    def track_project_start(
        self,
        project_name: str,
        description: str = '',
        context: str = ''
    ) -> int:
        """
        Track a new project start.
        
        Args:
            project_name: Name of new project
            description: Project description/goals
            context: Domain or category
        
        Returns:
            Milestone ID
        """
        return self.store.add_milestone(
            title=f"Started: {project_name}",
            milestone_type='project_start',
            description=description,
            context=context,
            meta={'project': project_name}
        )


# Singleton instance
_tracker = None


def get_taskflow_tracker(rag_memory=None) -> TaskFlowMilestoneTracker:
    """Get or create TaskFlow milestone tracker"""
    global _tracker
    if _tracker is None:
        _tracker = TaskFlowMilestoneTracker(rag_memory)
    return _tracker


# For backward compatibility
MilestoneStore._get_connection = lambda self: __import__('contextlib').contextmanager(
    lambda: (yield __import__('sqlite3').connect(self.db_path, check_same_thread=False))
)()
