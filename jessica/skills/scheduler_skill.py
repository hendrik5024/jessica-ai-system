"""
Scheduler Skill - Handles reminders, scheduling, and time-based events
"""

import logging
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os

logger = logging.getLogger("jessica.skills.scheduler_skill")


class EventType(Enum):
    """Types of scheduled events"""
    REMINDER = "reminder"
    ALARM = "alarm"
    BREAK = "break"
    MEDITATION = "meditation"
    MEETING = "meeting"
    TASK = "task"
    REFLECTION = "reflection"


@dataclass
class ScheduledEvent:
    """Represents a scheduled event"""
    id: str
    title: str
    description: str
    event_type: EventType
    scheduled_time: datetime
    recurrence: Optional[str]  # 'daily', 'weekly', 'monthly', or None
    active: bool
    notification_before_minutes: int = 5
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type.value,
            'scheduled_time': self.scheduled_time.isoformat(),
            'recurrence': self.recurrence,
            'active': self.active,
            'notification_before_minutes': self.notification_before_minutes,
        }


class SchedulerSkill:
    """
    Manages scheduling, reminders, and time-based events.
    Features:
    - Create and manage reminders
    - Set recurring events
    - Break reminders
    - Meditation sessions
    - Task scheduling
    """

    def __init__(self, schedule_file: str = "jessica_schedule.json"):
        self.schedule_file = schedule_file
        self.events: List[ScheduledEvent] = []
        self.load_schedule()
        
        # Callbacks
        self.on_event_trigger: Optional[Callable] = None
        
        # Monitor thread
        self.running = False
        self._monitor_thread = None
        
        logger.info("SchedulerSkill initialized")

    def load_schedule(self):
        """Load schedule from disk"""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    data = json.load(f)
                    self.events = []
                    for event_data in data:
                        event = ScheduledEvent(
                            id=event_data['id'],
                            title=event_data['title'],
                            description=event_data['description'],
                            event_type=EventType(event_data['event_type']),
                            scheduled_time=datetime.fromisoformat(event_data['scheduled_time']),
                            recurrence=event_data.get('recurrence'),
                            active=event_data.get('active', True),
                            notification_before_minutes=event_data.get('notification_before_minutes', 5),
                        )
                        self.events.append(event)
                logger.info(f"Loaded {len(self.events)} scheduled events")
            except Exception as e:
                logger.error(f"Failed to load schedule: {e}")

    def save_schedule(self):
        """Save schedule to disk"""
        try:
            data = [event.to_dict() for event in self.events]
            with open(self.schedule_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Schedule saved")
        except Exception as e:
            logger.error(f"Failed to save schedule: {e}")

    def start_monitoring(self):
        """Start the scheduler monitoring loop"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Scheduler monitoring started")

    def stop_monitoring(self):
        """Stop the scheduler monitoring loop"""
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Scheduler monitoring stopped")

    def _monitor_loop(self):
        """Main scheduler loop - checks for upcoming events"""
        while self.running:
            try:
                now = datetime.now()
                
                for event in self.events:
                    if not event.active:
                        continue
                    
                    # Check if event should trigger
                    time_until = (event.scheduled_time - now).total_seconds()
                    notification_seconds = event.notification_before_minutes * 60
                    
                    # Notification window
                    if 0 <= time_until <= notification_seconds:
                        self._trigger_event(event, time_until)
                    
                    # Handle recurring events
                    elif time_until < 0 and event.recurrence:
                        self._reschedule_recurring_event(event)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)

    def _trigger_event(self, event: ScheduledEvent, time_until_seconds: float):
        """Trigger a scheduled event"""
        logger.info(f"Triggering event: {event.title}")
        
        if self.on_event_trigger:
            try:
                self.on_event_trigger({
                    'event': event,
                    'time_until_seconds': time_until_seconds,
                    'message': self._generate_event_message(event, time_until_seconds),
                })
            except Exception as e:
                logger.error(f"Error in on_event_trigger callback: {e}")

    def _generate_event_message(self, event: ScheduledEvent, time_until_seconds: float) -> str:
        """Generate a message for the event"""
        if time_until_seconds > 0:
            minutes = int(time_until_seconds / 60)
            if minutes > 0:
                return f"Reminder: {event.title} in {minutes} minutes. {event.description}"
            else:
                return f"Reminder: {event.title} coming up. {event.description}"
        else:
            return f"Event: {event.title}. {event.description}"

    def _reschedule_recurring_event(self, event: ScheduledEvent):
        """Reschedule a recurring event for next occurrence"""
        if event.recurrence == 'daily':
            event.scheduled_time = event.scheduled_time + timedelta(days=1)
        elif event.recurrence == 'weekly':
            event.scheduled_time = event.scheduled_time + timedelta(weeks=1)
        elif event.recurrence == 'monthly':
            # Add 30 days as approximation
            event.scheduled_time = event.scheduled_time + timedelta(days=30)
        
        logger.info(f"Rescheduled {event.title} to {event.scheduled_time}")
        self.save_schedule()

    def add_reminder(self, title: str, description: str, scheduled_time: datetime,
                     recurrence: Optional[str] = None, notification_before_minutes: int = 5) -> str:
        """Add a new reminder"""
        event_id = self._generate_id()
        event = ScheduledEvent(
            id=event_id,
            title=title,
            description=description,
            event_type=EventType.REMINDER,
            scheduled_time=scheduled_time,
            recurrence=recurrence,
            active=True,
            notification_before_minutes=notification_before_minutes,
        )
        self.events.append(event)
        self.save_schedule()
        logger.info(f"Added reminder: {title}")
        return event_id

    def add_break_reminder(self, minutes_from_now: int = 60) -> str:
        """Add a break reminder"""
        scheduled_time = datetime.now() + timedelta(minutes=minutes_from_now)
        event_id = self._generate_id()
        event = ScheduledEvent(
            id=event_id,
            title="Take a break",
            description="Time to rest your eyes and stretch",
            event_type=EventType.BREAK,
            scheduled_time=scheduled_time,
            recurrence=None,
            active=True,
            notification_before_minutes=5,
        )
        self.events.append(event)
        self.save_schedule()
        logger.info(f"Added break reminder for {minutes_from_now} minutes from now")
        return event_id

    def add_meditation_session(self, duration_minutes: int = 10, scheduled_time: Optional[datetime] = None) -> str:
        """Add a meditation session"""
        if scheduled_time is None:
            scheduled_time = datetime.now() + timedelta(minutes=5)
        
        event_id = self._generate_id()
        event = ScheduledEvent(
            id=event_id,
            title="Meditation",
            description=f"{duration_minutes} minute meditation session",
            event_type=EventType.MEDITATION,
            scheduled_time=scheduled_time,
            recurrence=None,
            active=True,
            notification_before_minutes=2,
        )
        self.events.append(event)
        self.save_schedule()
        logger.info(f"Added meditation session for {scheduled_time}")
        return event_id

    def add_reflection_window(
        self,
        title: str = "Reflection Window",
        scheduled_time: Optional[datetime] = None,
        recurrence: Optional[str] = "daily",
        notification_before_minutes: int = 0,
    ) -> str:
        """Add a scheduled reflection window (private cognition)."""
        if scheduled_time is None:
            scheduled_time = datetime.now() + timedelta(minutes=5)

        event_id = self._generate_id()
        event = ScheduledEvent(
            id=event_id,
            title=title,
            description="Private reflection window (no user notification)",
            event_type=EventType.REFLECTION,
            scheduled_time=scheduled_time,
            recurrence=recurrence,
            active=True,
            notification_before_minutes=notification_before_minutes,
        )
        self.events.append(event)
        self.save_schedule()
        logger.info("Added reflection window")
        return event_id

    def add_task(self, title: str, description: str, due_datetime: datetime,
                 recurrence: Optional[str] = None) -> str:
        """Add a task with deadline"""
        event_id = self._generate_id()
        event = ScheduledEvent(
            id=event_id,
            title=title,
            description=description,
            event_type=EventType.TASK,
            scheduled_time=due_datetime,
            recurrence=recurrence,
            active=True,
            notification_before_minutes=60,
        )
        self.events.append(event)
        self.save_schedule()
        logger.info(f"Added task: {title}")
        return event_id

    def remove_event(self, event_id: str) -> bool:
        """Remove a scheduled event"""
        self.events = [e for e in self.events if e.id != event_id]
        self.save_schedule()
        logger.info(f"Removed event: {event_id}")
        return True

    def list_upcoming_events(self, hours: int = 24) -> List[Dict]:
        """List upcoming events in the next N hours"""
        now = datetime.now()
        future = now + timedelta(hours=hours)
        
        upcoming = [
            event.to_dict()
            for event in self.events
            if event.active and now <= event.scheduled_time <= future
        ]
        
        return sorted(upcoming, key=lambda e: e['scheduled_time'])

    def get_event(self, event_id: str) -> Optional[ScheduledEvent]:
        """Get event by ID"""
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def _generate_id(self) -> str:
        """Generate unique event ID"""
        import hashlib
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]


# Skill metadata for skill loader
META = {
    'name': 'scheduler_skill',
    'class': 'SchedulerSkill',
    'description': 'Scheduling, reminders, and time-based event management',
    'version': '1.0.0',
}
