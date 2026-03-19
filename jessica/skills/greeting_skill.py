"""
Greeting Skill - Jessica's welcome and awareness skill
Triggers greetings based on system events (wake, app launch, etc.)
"""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger("jessica.skills.greeting_skill")


@dataclass
class GreetingContext:
    """Context for generating appropriate greetings"""
    event_type: str  # 'wake', 'app_launch', 'window_change', 'scheduled'
    active_window: Optional[str]
    active_app: Optional[str]
    time_of_day: str  # 'morning', 'afternoon', 'evening', 'night'
    user_idle_time: float
    last_greeting_ago_seconds: float


class GreetingSkill:
    """
    Provides contextual greetings based on system events and time of day.
    Examples:
    - "Good morning! I see you're opening VS Code. Ready to code?"
    - "Welcome back! You've been away for 2 hours."
    - "I noticed Spotify opened. Want some music while you work?"
    """

    def __init__(self):
        self.last_greeting_time = None
        self.greeting_cooldown_seconds = 300  # Don't spam greetings (5 min cooldown)
        self.enabled = True
        
        # Personalization preferences (can be learned)
        self.app_greetings = {
            'code.exe': "Ready to code?",
            'notepad.exe': "Taking some notes?",
            'spotify.exe': "Music time!",
            'chrome.exe': "Browsing the web?",
            'outlook.exe': "Checking emails?",
            'slack.exe': "Team time?",
            'discord.exe': "Gaming or socializing?",
        }
        
        logger.info("GreetingSkill initialized")

    def should_greet(self, context: GreetingContext) -> bool:
        """Determine if we should send a greeting"""
        if not self.enabled:
            return False
        
        # Don't greet if we've greeted recently
        if context.last_greeting_ago_seconds < self.greeting_cooldown_seconds:
            return False
        
        # Only greet on certain events
        if context.event_type not in ['wake', 'app_launch', 'window_change']:
            return False
        
        return True

    def generate_greeting(self, context: GreetingContext) -> str:
        """Generate a contextual greeting message"""
        greeting = self._get_time_greeting(context.time_of_day)
        
        # Add context-specific greeting
        if context.event_type == 'wake':
            greeting += " You've been away for " + self._format_idle_time(context.user_idle_time) + "."
        
        elif context.event_type == 'app_launch' or context.event_type == 'window_change':
            if context.active_app:
                app_suffix = self._get_app_specific_greeting(context.active_app)
                if app_suffix:
                    greeting += " " + app_suffix
        
        return greeting

    def _get_time_greeting(self, time_of_day: str) -> str:
        """Get greeting based on time of day"""
        greetings = {
            'morning': "Good morning!",
            'afternoon': "Good afternoon!",
            'evening': "Good evening!",
            'night': "Hello! Working late?",
        }
        return greetings.get(time_of_day, "Hello!")

    def _get_app_specific_greeting(self, app_name: str) -> Optional[str]:
        """Get app-specific greeting suffix"""
        app_name_lower = app_name.lower()
        
        # Check exact match first
        if app_name_lower in self.app_greetings:
            return self.app_greetings[app_name_lower]
        
        # Check partial match
        for app_pattern, greeting in self.app_greetings.items():
            if app_pattern.replace('.exe', '').lower() in app_name_lower:
                return greeting
        
        return None

    def _format_idle_time(self, seconds: float) -> str:
        """Format idle time in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''}"

    def get_time_of_day(self) -> str:
        """Determine current time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def on_system_wake(self, system_state):
        """Handle system wake event"""
        logger.info("System wake detected")
        
        greeting_context = GreetingContext(
            event_type='wake',
            active_window=system_state.active_window,
            active_app=system_state.active_process,
            time_of_day=self.get_time_of_day(),
            user_idle_time=max(
                system_state.keyboard_idle_seconds,
                system_state.mouse_idle_seconds
            ),
            last_greeting_ago_seconds=self._get_seconds_since_last_greeting()
        )
        
        if self.should_greet(greeting_context):
            greeting = self.generate_greeting(greeting_context)
            self.last_greeting_time = datetime.now()
            return {
                'success': True,
                'greeting': greeting,
                'context': greeting_context
            }
        
        return {'success': False, 'reason': 'Greeting cooldown active'}

    def on_app_launched(self, app_name: str, system_state):
        """Handle app launch event"""
        logger.info(f"App launched: {app_name}")
        
        greeting_context = GreetingContext(
            event_type='app_launch',
            active_window=system_state.active_window,
            active_app=app_name,
            time_of_day=self.get_time_of_day(),
            user_idle_time=0,  # Just became active
            last_greeting_ago_seconds=self._get_seconds_since_last_greeting()
        )
        
        if self.should_greet(greeting_context):
            greeting = self.generate_greeting(greeting_context)
            self.last_greeting_time = datetime.now()
            return {
                'success': True,
                'greeting': greeting,
                'context': greeting_context
            }
        
        return {'success': False, 'reason': 'Greeting cooldown active'}

    def on_window_changed(self, window_name: str, system_state):
        """Handle window change event"""
        logger.info(f"Window changed: {window_name}")
        
        greeting_context = GreetingContext(
            event_type='window_change',
            active_window=window_name,
            active_app=None,
            time_of_day=self.get_time_of_day(),
            user_idle_time=0,
            last_greeting_ago_seconds=self._get_seconds_since_last_greeting()
        )
        
        if self.should_greet(greeting_context):
            greeting = self.generate_greeting(greeting_context)
            self.last_greeting_time = datetime.now()
            return {
                'success': True,
                'greeting': greeting,
                'context': greeting_context
            }
        
        return {'success': False, 'reason': 'Greeting cooldown active'}

    def _get_seconds_since_last_greeting(self) -> float:
        """Get seconds since last greeting (large if never greeted)"""
        if self.last_greeting_time is None:
            return float('inf')
        
        return (datetime.now() - self.last_greeting_time).total_seconds()

    def set_cooldown(self, seconds: float):
        """Set greeting cooldown period in seconds"""
        self.greeting_cooldown_seconds = seconds
        logger.info(f"Greeting cooldown set to {seconds} seconds")

    def enable(self):
        """Enable greetings"""
        self.enabled = True
        logger.info("Greetings enabled")

    def disable(self):
        """Disable greetings"""
        self.enabled = False
        logger.info("Greetings disabled")


# Skill metadata for skill loader
META = {
    'name': 'greeting_skill',
    'class': 'GreetingSkill',
    'description': 'Contextual greetings based on system events and time of day',
    'version': '1.0.0',
}
