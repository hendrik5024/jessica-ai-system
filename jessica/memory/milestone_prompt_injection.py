"""
Milestone Prompt Injection - Weaves achievement milestones into conversations.

Provides functions to:
1. Inject milestone mentions into prompts (random 30+ days old)
2. Build milestone context for agent loop
3. Generate achievement summaries for conversation intro
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from jessica.memory.milestone_system import (
    get_milestone_recaller,
    get_milestone_store,
    MilestoneRecaller,
    MilestoneStore
)

logger = logging.getLogger("jessica.milestone_prompt_injection")


class MilestonePromptInjector:
    """
    Injects milestone context into prompts for natural conversation continuity.
    
    Strategies:
    1. Occasional anniversary mentions ("It's been X days since...")
    2. Achievement summary in system context
    3. Milestone-related follow-ups
    """
    
    def __init__(self):
        self.recaller = get_milestone_recaller()
        self.store = get_milestone_store()
    
    def maybe_inject_milestone(
        self,
        min_days_old: int = 30,
        max_days_old: int = 365
    ) -> Optional[str]:
        """
        Randomly decide to inject a milestone mention.
        
        Returns a natural sentence mentioning an old milestone,
        or None if conditions not met.
        
        Args:
            min_days_old: Minimum days for milestone age
            max_days_old: Maximum days for milestone age
        
        Returns:
            Formatted milestone mention or None
        """
        milestone = self.recaller.maybe_recall_milestone(min_days_old=min_days_old)
        
        if not milestone:
            return None
        
        mention = self.recaller.format_milestone_mention(milestone)
        logger.debug(f"Injected milestone mention: {mention}")
        
        return mention
    
    def build_milestone_context(
        self,
        include_recent: int = 3,
        include_old: bool = True,
        min_days_old: int = 30
    ) -> Optional[str]:
        """
        Build comprehensive milestone context for system prompt.
        
        Includes recent achievements and optionally an old milestone mention.
        
        Args:
            include_recent: Number of recent milestones to include
            include_old: Whether to include an old milestone mention
            min_days_old: Minimum days for "old" milestone
        
        Returns:
            Milestone context string or None
        """
        parts = []
        
        # Add recent achievements
        recent = self.store.get_milestones(limit=include_recent)
        if recent:
            recent_text = self.recaller.get_random_achievement_summary(limit=include_recent)
            if recent_text:
                parts.append(f"Recent achievements: {recent_text}")
        
        # Add old milestone mention
        if include_old:
            milestone = self.recaller.maybe_recall_milestone(min_days_old=min_days_old)
            if milestone:
                mention = self.recaller.format_milestone_mention(milestone)
                parts.append(mention)
        
        if not parts:
            return None
        
        return "\n".join(parts)
    
    def inject_into_system_prompt(
        self,
        base_prompt: str,
        include_milestone: bool = True,
        include_context: bool = True
    ) -> str:
        """
        Inject milestone context into an existing system prompt.
        
        Args:
            base_prompt: Original system prompt
            include_milestone: Add specific milestone mention
            include_context: Add achievement context
        
        Returns:
            Enhanced prompt with milestone context
        """
        additions = []
        
        # Add milestone context section
        if include_context:
            context = self.build_milestone_context(
                include_recent=2,
                include_old=False
            )
            if context:
                additions.append(f"[Achievements]\n{context}")
        
        # Add occasional milestone mention
        if include_milestone:
            mention = self.maybe_inject_milestone(min_days_old=30)
            if mention:
                additions.append(f"[Milestone Mention]\n{mention}")
        
        # Append to prompt
        if additions:
            return base_prompt + "\n\n" + "\n\n".join(additions)
        
        return base_prompt
    
    def get_milestone_intro(self, limit: int = 2) -> Optional[str]:
        """
        Get an achievement-focused introduction for responses.
        
        Can be used at the start of conversational responses.
        
        Args:
            limit: Number of recent milestones to reference
        
        Returns:
            Short intro mentioning achievements, or None
        """
        milestones = self.store.get_milestones(limit=limit)
        
        if not milestones:
            return None
        
        # Build engaging intro
        if len(milestones) == 1:
            m = milestones[0]
            return f"Speaking of progress, I'm really proud of what we did with {m['title'].lower()}!"
        else:
            titles = [m['title'].lower() for m in milestones[:2]]
            return f"You know, thinking about all we've accomplished lately—like {titles[0]} and {titles[1]}—it's pretty cool!"
        
    def get_milestone_reflection(self) -> Optional[str]:
        """
        Get a reflective statement about overall progress.
        
        Suitable for end-of-conversation or reflection moments.
        
        Returns:
            Reflection statement or None
        """
        total = self.store.count_milestones()
        
        if total == 0:
            return "We're just getting started on this journey!"
        elif total < 5:
            return f"We've made {total} notable achievements so far. That's a great foundation!"
        elif total < 20:
            return f"We've reached {total} milestones now. The momentum is building!"
        else:
            return f"Look at us—{total} milestones achieved! That's real progress."
    
    def inject_milestone_reminder(self) -> Optional[str]:
        """
        Get a reminder about old achievements to celebrate progress.
        
        Returns a formatted milestone mention from 20-90 days ago.
        """
        milestones = self.store.get_milestones_in_range(
            days_ago_min=20,
            days_ago_max=90,
            limit=10
        )
        
        if not milestones:
            return None
        
        import random
        milestone = random.choice(milestones)
        
        return self.recaller.format_milestone_mention(milestone)
    
    def enhance_prompt_with_milestones(
        self,
        user_text: str,
        base_system_prompt: str
    ) -> Tuple[str, Optional[Dict]]:
        """
        Comprehensively enhance a prompt with milestone context.
        
        Returns both enhanced prompt and milestone metadata for logging.
        
        Args:
            user_text: User's input
            base_system_prompt: Original system prompt
        
        Returns:
            Tuple of (enhanced_prompt, milestone_metadata)
        """
        milestone_meta = None
        enhanced = base_system_prompt
        
        # Check for milestone context relevance
        if self._should_inject_milestone(user_text):
            enhanced = self.inject_into_system_prompt(
                enhanced,
                include_milestone=True,
                include_context=True
            )
            
            # Log metadata
            milestone_meta = {
                'injection_type': 'context_relevant',
                'milestones_count': self.store.count_milestones()
            }
        else:
            # Random chance for background injection
            import random
            if random.random() < 0.15:  # 15% chance
                milestone_mention = self.maybe_inject_milestone()
                if milestone_mention:
                    enhanced = enhanced + f"\n\n[Background Context]\n{milestone_mention}"
                    milestone_meta = {'injection_type': 'random_background'}
        
        return enhanced, milestone_meta
    
    def _should_inject_milestone(self, user_text: str) -> bool:
        """Determine if milestone context is relevant to user's text"""
        keywords = [
            'progress', 'accomplished', 'done', 'finished', 'complete',
            'achieve', 'success', 'memory', 'remember', 'back when',
            'milestone', 'goal', 'objective', 'celebrate'
        ]
        
        text_lower = user_text.lower()
        return any(keyword in text_lower for keyword in keywords)


# Singleton instance
_injector = None


def get_milestone_injector() -> MilestonePromptInjector:
    """Get or create milestone prompt injector"""
    global _injector
    if _injector is None:
        _injector = MilestonePromptInjector()
    return _injector


# Convenience functions for agent loop integration

def inject_milestone_mention(min_days_old: int = 30) -> Optional[str]:
    """Quick function to inject a milestone mention"""
    injector = get_milestone_injector()
    return injector.maybe_inject_milestone(min_days_old=min_days_old)


def build_milestone_context_for_prompt() -> Optional[str]:
    """Quick function to get milestone context"""
    injector = get_milestone_injector()
    return injector.build_milestone_context()


def enhance_prompt(
    user_text: str,
    base_prompt: str
) -> Tuple[str, Optional[Dict]]:
    """Quick function to enhance a prompt with milestones"""
    injector = get_milestone_injector()
    return injector.enhance_prompt_with_milestones(user_text, base_prompt)
