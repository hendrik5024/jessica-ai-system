"""
Context Awareness Module - Tracks user habits and patterns
Learns:
- Active window patterns by time of day
- Application usage frequency and duration
- Productivity patterns
- Interruption recovery time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import os

logger = logging.getLogger("jessica.context_awareness")


class UserContextProfile:
    """Stores and analyzes user context patterns"""

    def __init__(self, profile_file: str = "jessica_context_profile.json"):
        self.profile_file = profile_file
        self.profile = self._load_profile()
        
        # Real-time tracking
        self.current_app: Optional[str] = None
        self.app_session_start: Optional[datetime] = None
        self.today_app_usage: Dict[str, float] = defaultdict(float)  # app_name -> seconds
        
        logger.info("UserContextProfile initialized")

    def _load_profile(self) -> Dict:
        """Load user profile from disk"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load profile: {e}")
        
        # Default profile structure
        return {
            'total_sessions': 0,
            'first_session': None,
            'last_session': None,
            'app_frequency': {},  # app_name -> count
            'app_daily_usage': {},  # app_name -> average_minutes_per_day
            'window_patterns': {},  # time_of_day -> list of active windows
            'productivity_score': 0,
            'focus_apps': [],  # High-priority apps
            'distraction_apps': [],  # Low-priority apps
            'peak_hours': [],  # Most productive hours
            'break_patterns': {},  # When user typically takes breaks
        }

    def _save_profile(self):
        """Save user profile to disk"""
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(self.profile, f, indent=2)
            logger.debug("Profile saved")
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")

    def record_app_activity(self, app_name: str, duration_seconds: float):
        """Record app usage session"""
        # Update frequency
        if app_name not in self.profile['app_frequency']:
            self.profile['app_frequency'][app_name] = 0
        self.profile['app_frequency'][app_name] += 1
        
        # Update daily usage
        if app_name not in self.profile['app_daily_usage']:
            self.profile['app_daily_usage'][app_name] = 0
        self.profile['app_daily_usage'][app_name] += duration_seconds / 60  # Convert to minutes
        
        # Update real-time tracking
        self.today_app_usage[app_name] += duration_seconds
        
        logger.info(f"Recorded {app_name} usage: {duration_seconds:.0f}s")

    def record_window_activity(self, window_name: str):
        """Record window activity for time-of-day patterns"""
        time_of_day = self._get_time_period()
        
        if time_of_day not in self.profile['window_patterns']:
            self.profile['window_patterns'][time_of_day] = []
        
        if window_name not in self.profile['window_patterns'][time_of_day]:
            self.profile['window_patterns'][time_of_day].append(window_name)

    def get_context_suggestion(self) -> Dict:
        """Get current context-aware suggestion"""
        context = {
            'current_app': self.current_app,
            'likely_next_apps': self._get_likely_next_apps(),
            'productivity_level': self._calculate_productivity_level(),
            'focus_recommendation': self._get_focus_recommendation(),
            'break_recommendation': self._should_suggest_break(),
        }
        return context

    def _get_likely_next_apps(self) -> List[str]:
        """Predict likely next apps based on patterns"""
        # Find top apps by frequency
        if not self.profile['app_frequency']:
            return []
        
        sorted_apps = sorted(
            self.profile['app_frequency'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [app for app, _ in sorted_apps[:5]]

    def _calculate_productivity_level(self) -> str:
        """Calculate current productivity level"""
        # Based on focus app usage
        focus_time = sum(
            self.today_app_usage.get(app, 0)
            for app in self.profile['focus_apps']
        )
        distraction_time = sum(
            self.today_app_usage.get(app, 0)
            for app in self.profile['distraction_apps']
        )
        
        if focus_time == 0:
            return 'idle'
        
        ratio = distraction_time / (focus_time + distraction_time) if (focus_time + distraction_time) > 0 else 0
        
        if ratio < 0.2:
            return 'highly_productive'
        elif ratio < 0.4:
            return 'productive'
        elif ratio < 0.6:
            return 'moderately_productive'
        elif ratio < 0.8:
            return 'distracted'
        else:
            return 'unfocused'

    def _get_focus_recommendation(self) -> str:
        """Get focus recommendation based on patterns"""
        productivity = self._calculate_productivity_level()
        
        if productivity == 'highly_productive':
            return "You're in the zone! Keep it up."
        elif productivity == 'productive':
            return "Good focus. Maybe a 5-minute break soon?"
        elif productivity == 'moderately_productive':
            return "Consider closing distracting apps."
        else:
            return "Lots of app switching detected. Try single-tasking?"

    def _should_suggest_break(self) -> bool:
        """Determine if break should be suggested"""
        # Check if user has been active for > 90 minutes
        total_active_time = sum(self.today_app_usage.values()) / 60  # Convert to minutes
        
        return total_active_time > 90

    def _get_time_period(self) -> str:
        """Get current time period"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def set_focus_apps(self, apps: List[str]):
        """Set which apps are considered 'focus' apps"""
        self.profile['focus_apps'] = apps
        logger.info(f"Focus apps set to: {apps}")

    def set_distraction_apps(self, apps: List[str]):
        """Set which apps are considered 'distraction' apps"""
        self.profile['distraction_apps'] = apps
        logger.info(f"Distraction apps set to: {apps}")

    def get_stats(self) -> Dict:
        """Get user statistics"""
        return {
            'total_apps_used': len(self.profile['app_frequency']),
            'top_app': max(self.profile['app_frequency'].items(), key=lambda x: x[1])[0] if self.profile['app_frequency'] else None,
            'today_usage': dict(self.today_app_usage),
            'productivity_level': self._calculate_productivity_level(),
        }


class ContextManager:
    """Manages all user context and awareness features"""

    def __init__(self):
        self.profile = UserContextProfile()
        self.system_state = None
        logger.info("ContextManager initialized")

    def update_context(self, system_state):
        """Update context with new system state"""
        self.system_state = system_state
        
        # Record active window and app
        if system_state.active_window:
            self.profile.record_window_activity(system_state.active_window)
        
        if system_state.active_process:
            if self.profile.current_app != system_state.active_process:
                # App changed - record previous app session
                if self.profile.current_app and self.profile.app_session_start:
                    duration = (datetime.now() - self.profile.app_session_start).total_seconds()
                    self.profile.record_app_activity(self.profile.current_app, duration)
                
                # Start new app session
                self.profile.current_app = system_state.active_process
                self.profile.app_session_start = datetime.now()

    def get_personalized_greeting(self) -> Dict:
        """Get personalized greeting based on context"""
        stats = self.profile.get_stats()
        suggestion = self.profile.get_context_suggestion()
        
        return {
            'greeting': self._generate_personalized_greeting(stats),
            'context': suggestion,
            'stats': stats,
        }

    def _generate_personalized_greeting(self, stats: Dict) -> str:
        """Generate personalized greeting"""
        top_app = stats.get('top_app')
        productivity = stats.get('productivity_level')
        
        greetings = {
            'highly_productive': "Great focus today! Keep up the excellent work!",
            'productive': "You're being productive! Good flow.",
            'moderately_productive': "Working away! Take breaks when you need them.",
            'distracted': "Lots of switching today. Need to focus?",
            'unfocused': "Consider closing some distracting apps?",
        }
        
        base_greeting = greetings.get(productivity, "Welcome back!")
        
        if top_app:
            return f"{base_greeting} Working on {top_app} today?"
        
        return base_greeting


# Singleton instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create context manager singleton"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
