"""
System Integration Module - Integrates system monitoring with Jessica
Connects system_monitor, greeting_skill, and context_awareness
"""

import logging
from typing import Optional
from jessica.automation.system_monitor import SystemEventMonitor, get_system_monitor
from jessica.automation.context_awareness import ContextManager, get_context_manager
from jessica.automation.proactive_nudger import ProactiveNudger
from jessica.automation.background_curiosity import BackgroundCuriosity
from jessica.automation.frustration_detector import FrustrationDetector
from jessica.skills.greeting_skill import GreetingSkill
from jessica.skills.scheduler_skill import SchedulerSkill, EventType
from jessica.meta.reflection_window import ReflectionWindow
from jessica.memory.sqlite_store import EpisodicStore

logger = logging.getLogger("jessica.system_integration")


class SystemIntegration:
    """
    Integrates all system awareness components:
    - System monitoring (keyboard, mouse, apps, window)
    - Greetings
    - Context awareness
    - Scheduling
    """

    def __init__(self):
        self.monitor = get_system_monitor()
        self.context_manager = get_context_manager()
        self.greeting_skill = GreetingSkill()
        self.scheduler_skill = SchedulerSkill()
        self.nudger = ProactiveNudger()
        self.curiosity = BackgroundCuriosity()
        self.frustration = FrustrationDetector()
        
        self.enabled = True
        self.greeting_queue = []
        
        logger.info("SystemIntegration initialized")

    def initialize(self, on_greeting_callback=None, on_event_callback=None):
        """Initialize all system monitoring components"""
        logger.info("Initializing system integration...")
        
        # Set up monitor callbacks
        self.monitor.on_user_active = self._on_user_active
        self.monitor.on_user_idle = self._on_user_idle
        self.monitor.on_app_launched = self._on_app_launched
        self.monitor.on_app_closed = self._on_app_closed
        self.monitor.on_window_changed = self._on_window_changed
        self.monitor.on_keyboard_press = self._on_keyboard_press  # NEW: Frustration detection
        
        # Set up scheduler callback
        self.scheduler_skill.on_event_trigger = on_event_callback or self._on_scheduler_event
        
        # Store external callbacks
        self.on_greeting = on_greeting_callback
        
        # Start monitoring
        self.monitor.start()
        self.scheduler_skill.start_monitoring()
        
        logger.info("System integration ready")

    def shutdown(self):
        """Shutdown all monitoring components"""
        logger.info("Shutting down system integration...")
        self.monitor.stop()
        self.scheduler_skill.stop_monitoring()

    def _on_user_active(self, system_state):
        """Handle user becoming active"""
        logger.info("User became active")
        
        # Update context
        self.context_manager.update_context(system_state)
        
        # Generate greeting
        result = self.greeting_skill.on_system_wake(system_state)
        if result['success']:
            greeting = result['greeting']
            logger.info(f"Greeting: {greeting}")
            
            if self.on_greeting:
                self.on_greeting({
                    'type': 'wake',
                    'greeting': greeting,
                    'context': result.get('context'),
                })

    def _on_user_idle(self, system_state):
        """Handle user becoming idle"""
        logger.info("User became idle")
        
        # Don't trigger greeting, but update context
        self.context_manager.update_context(system_state)
        
        # Could suggest break or meditation
        if self.on_greeting:
            self.on_greeting({
                'type': 'idle_notification',
                'message': "You've been away for a while. Want to take a break?",
                'context': self.context_manager.profile.get_context_suggestion(),
            })

        # Proactive nudge (gentle, rate-limited)
        nudge = self.nudger.maybe_idle_nudge(system_state, self.context_manager)
        if nudge and self.on_greeting:
            self.on_greeting({
                'type': 'proactive_nudge',
                'message': nudge['message'],
                'context': nudge.get('context'),
                'idle_seconds': nudge.get('idle_seconds'),
            })

        # Background curiosity (lightweight topics to revisit)
        try:
            insight = self.curiosity.maybe_research(system_state, self.context_manager)
        except Exception:
            insight = None
        if insight and self.on_greeting:
            self.on_greeting({
                'type': 'background_curiosity',
                'message': insight['message'],
                'topics': insight.get('topics'),
                'idle_seconds': insight.get('idle_seconds'),
            })

    def _on_app_launched(self, app_name, system_state):
        """Handle app launch"""
        logger.info(f"App launched: {app_name}")
        
        # Update context
        self.context_manager.update_context(system_state)
        
        # Generate contextual greeting
        result = self.greeting_skill.on_app_launched(app_name, system_state)
        if result['success']:
            greeting = result['greeting']
            logger.info(f"App greeting: {greeting}")
            
            if self.on_greeting:
                self.on_greeting({
                    'type': 'app_launch',
                    'app': app_name,
                    'greeting': greeting,
                    'context': result.get('context'),
                })

    def _on_app_closed(self, app_name, system_state):
        """Handle app close"""
        logger.info(f"App closed: {app_name}")
        
        # Record app usage
        if self.context_manager.profile.current_app == app_name and \
           self.context_manager.profile.app_session_start:
            duration = (system_state.last_activity - \
                       self.context_manager.profile.app_session_start).total_seconds()
            self.context_manager.profile.record_app_activity(app_name, duration)

    def _on_window_changed(self, window_name, system_state):
        """Handle window change"""
        logger.debug(f"Window changed: {window_name}")
        
        # Track for frustration detection (rapid switching)
        frustration_alert = self.frustration.track_window_switch(window_name)
        if frustration_alert and self.on_greeting:
            self.on_greeting({
                'type': 'frustration_alert',
                'message': frustration_alert['message'],
                'context': frustration_alert['context'],
                'frustration_score': frustration_alert['frustration_score'],
                'voice_alert': frustration_alert.get('voice_alert', True),
                'priority': 'high'
            })
        
        # Update context
        self.context_manager.update_context(system_state)
        
        # Generate contextual greeting if appropriate
        result = self.greeting_skill.on_window_changed(window_name, system_state)
        if result['success']:
            greeting = result['greeting']
            
            if self.on_greeting:
                self.on_greeting({
                    'type': 'window_change',
                    'window': window_name,
                    'greeting': greeting,
                    'context': result.get('context'),
                })

    def _on_keyboard_press(self, key_name, system_state):
        """Handle keyboard press for frustration detection"""
        # Track Ctrl+Z (undo) and other frustration signals
        frustration_alert = self.frustration.track_keyboard_activity(key_name)
        if frustration_alert and self.on_greeting:
            self.on_greeting({
                'type': 'frustration_alert',
                'message': frustration_alert['message'],
                'context': frustration_alert['context'],
                'frustration_score': frustration_alert['frustration_score'],
                'voice_alert': frustration_alert.get('voice_alert', True),
                'priority': 'high'
            })

    def _on_scheduler_event(self, event_data):
        """Handle scheduled event"""
        logger.info(f"Scheduled event: {event_data['event'].title}")

        event = event_data.get('event')
        if event and getattr(event, "event_type", None) == EventType.REFLECTION:
            try:
                memory = EpisodicStore("jessica_data.db")
                days = 7 if getattr(event, "recurrence", None) == "weekly" else 1
                ReflectionWindow(memory).run(days=days)
                logger.info("Reflection window completed")
            except Exception as exc:
                logger.error(f"Reflection window failed: {exc}")
            return
        
        if self.on_greeting:
            self.on_greeting({
                'type': 'scheduled_event',
                'event': event_data['event'].to_dict(),
                'message': event_data['message'],
            })

    def get_status(self) -> dict:
        """Get current system integration status"""
        return {
            'monitor_running': self.monitor.running,
            'scheduler_running': self.scheduler_skill.running,
            'enabled': self.enabled,
            'system_state': self.monitor.get_state().to_dict(),
            'context': self.context_manager.profile.get_context_suggestion(),
            'stats': self.context_manager.profile.get_stats(),
            'upcoming_events': self.scheduler_skill.list_upcoming_events(hours=24),
        }

    def enable(self):
        """Enable system integration"""
        self.enabled = True
        self.greeting_skill.enable()
        logger.info("System integration enabled")

    def disable(self):
        """Disable system integration"""
        self.enabled = False
        self.greeting_skill.disable()
        logger.info("System integration disabled")

    def set_greeting_cooldown(self, seconds: float):
        """Set greeting cooldown period"""
        self.greeting_skill.set_cooldown(seconds)

    def set_idle_threshold(self, seconds: float):
        """Set idle detection threshold"""
        self.monitor.set_idle_threshold(seconds)

    def add_break_reminder(self, minutes_from_now: int = 60):
        """Add a break reminder"""
        return self.scheduler_skill.add_break_reminder(minutes_from_now)

    def add_meditation_session(self, duration_minutes: int = 10, scheduled_time=None):
        """Add a meditation session"""
        return self.scheduler_skill.add_meditation_session(duration_minutes, scheduled_time)

    def add_reminder(self, title: str, description: str, scheduled_time, recurrence=None):
        """Add a reminder"""
        return self.scheduler_skill.add_reminder(title, description, scheduled_time, recurrence)


# Singleton instance
_integration_instance: Optional[SystemIntegration] = None


def get_system_integration() -> SystemIntegration:
    """Get or create system integration singleton"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = SystemIntegration()
    return _integration_instance
