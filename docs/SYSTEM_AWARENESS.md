# Jessica System Awareness & Integration Features

## Overview

Jessica now includes comprehensive system awareness capabilities that enable her to be contextually aware of user activity, provide contextual greetings, manage schedules, and learn user patterns.

## New Components

### 1. System Monitor (`jessica/automation/system_monitor.py`)

**Purpose:** Tracks system-level events and user activity

**Features:**
- **Keyboard & Mouse Tracking:** Real-time detection of keyboard/mouse activity
- **Window Monitoring:** Tracks active window changes
- **Application Enumeration:** Lists all running applications
- **Idle Detection:** Identifies when user is idle (configurable threshold)
- **Activity Callbacks:** Event-driven architecture for responding to system events

**Key Classes:**
- `SystemEventMonitor`: Main monitoring class
- `SystemState`: Data class representing current system state

**Usage:**
```python
from jessica.automation.system_monitor import get_system_monitor

monitor = get_system_monitor()

def on_user_active(state):
    print(f"User active! Window: {state.active_window}")

monitor.on_user_active = on_user_active
monitor.start()
# ... do stuff ...
monitor.stop()
```

**Configuration:**
- `idle_threshold_seconds`: How long until user is considered idle (default: 300s)
- `activity_check_interval`: How often to check activity (default: 1s)
- `app_check_interval`: How often to check running apps (default: 5s)

---

### 2. Greeting Skill (`jessica/skills/greeting_skill.py`)

**Purpose:** Generates contextual, personalized greetings based on system events and time of day

**Features:**
- **Time-Aware Greetings:** Different greetings for morning, afternoon, evening, night
- **Event-Specific Greetings:** Tailored responses for wake, app launch, window change
- **App-Specific Recognition:** Recognizes popular apps and provides relevant commentary
- **Idle Time Tracking:** Mentions how long user was away
- **Cooldown Management:** Prevents greeting spam (configurable)

**Key Classes:**
- `GreetingSkill`: Main skill
- `GreetingContext`: Context data for generating greetings

**Example Greetings:**
- "Good morning! You've been away for 2 hours."
- "Good afternoon! I see you're opening VS Code. Ready to code?"
- "Welcome back! You've been away for 2 hours. Spotify opened. Want some music?"

**Configuration:**
- `greeting_cooldown_seconds`: Minimum time between greetings (default: 300s)
- `app_greetings`: Custom greetings for specific apps

**Usage:**
```python
from jessica.skills.greeting_skill import GreetingSkill, GreetingContext

skill = GreetingSkill()
context = GreetingContext(
    event_type='wake',
    active_window='VS Code',
    active_app='code.exe',
    time_of_day='morning',
    user_idle_time=3600,
    last_greeting_ago_seconds=float('inf')
)

greeting = skill.generate_greeting(context)
```

---

### 3. Context Awareness (`jessica/automation/context_awareness.py`)

**Purpose:** Learns and tracks user patterns, habits, and productivity levels

**Features:**
- **Application Usage Tracking:** Records frequency and duration of app usage
- **Time-of-Day Patterns:** Learns which apps user uses at different times
- **Productivity Scoring:** Calculates productivity level based on app usage
- **Focus/Distraction Classification:** Distinguishes between productive and distracting apps
- **Break Recommendations:** Suggests breaks based on activity duration
- **Persistent Storage:** Saves profile to disk for learning over time

**Key Classes:**
- `ContextManager`: Main manager
- `UserContextProfile`: User profile and analytics

**Metrics Tracked:**
- App frequency (how often used)
- Daily app usage (average minutes per day)
- Window patterns (by time of day)
- Productivity level
- Peak hours
- Break patterns

**Productivity Levels:**
- `highly_productive`: <20% distraction apps
- `productive`: 20-40% distraction
- `moderately_productive`: 40-60% distraction
- `distracted`: 60-80% distraction
- `unfocused`: >80% distraction

**Usage:**
```python
from jessica.automation.context_awareness import get_context_manager

manager = get_context_manager()
manager.profile.set_focus_apps(['code.exe', 'pycharm.exe'])
manager.profile.set_distraction_apps(['spotify.exe', 'discord.exe'])

stats = manager.profile.get_stats()
print(f"Productivity: {stats['productivity_level']}")
```

---

### 4. Scheduler Skill (`jessica/skills/scheduler_skill.py`)

**Purpose:** Manages reminders, scheduled events, and time-based notifications

**Features:**
- **Flexible Scheduling:** One-time and recurring events
- **Multiple Event Types:** Reminders, alarms, breaks, meditation, meetings, tasks
- **Notifications:** Configurable advance notifications
- **Recurring Events:** Daily, weekly, monthly patterns
- **Persistent Storage:** Saves schedule to disk
- **Monitoring Loop:** Background thread monitors for upcoming events

**Key Classes:**
- `SchedulerSkill`: Main scheduler
- `ScheduledEvent`: Individual scheduled event
- `EventType`: Enum of event types

**Event Types:**
- `REMINDER`: General reminders
- `ALARM`: Time-critical alerts
- `BREAK`: Break reminders
- `MEDITATION`: Meditation sessions
- `MEETING`: Meeting alerts
- `TASK`: Task deadlines

**Usage:**
```python
from jessica.skills.scheduler_skill import SchedulerSkill
from datetime import datetime, timedelta

scheduler = SchedulerSkill()

# Add reminder
future_time = datetime.now() + timedelta(hours=1)
reminder_id = scheduler.add_reminder(
    "Standup meeting",
    "Daily team standup",
    future_time,
    notification_before_minutes=15
)

# Add recurring break reminder
break_id = scheduler.add_break_reminder(minutes_from_now=60)

# Start monitoring
scheduler.start_monitoring()

# Set callback for events
def on_event(event_data):
    print(f"Event: {event_data['message']}")

scheduler.on_event_trigger = on_event
```

---

### 5. System Integration (`jessica/automation/system_integration.py`)

**Purpose:** Orchestrates all system awareness components

**Features:**
- **Unified Interface:** Single entry point for all system features
- **Event Orchestration:** Coordinates between monitor, greeting, context, and scheduler
- **Callback Management:** Routes events to appropriate handlers
- **Status Monitoring:** Provides comprehensive system status
- **Control Functions:** Enable/disable, configure thresholds

**Key Class:**
- `SystemIntegration`: Main orchestrator

**Methods:**
- `initialize()`: Start all monitoring components
- `shutdown()`: Stop all monitoring
- `get_status()`: Get comprehensive status
- `enable()`/`disable()`: Control integration
- `set_idle_threshold()`: Configure idle detection
- `add_reminder()`, `add_meditation_session()`: Scheduler integration

**Usage:**
```python
from jessica.automation.system_integration import get_system_integration

integration = get_system_integration()

def on_greeting(greeting_data):
    print(f"Greeting: {greeting_data['greeting']}")
    if greeting_data.get('context'):
        print(f"Context: {greeting_data['context']}")

integration.initialize(on_greeting_callback=on_greeting)

# Get status
status = integration.get_status()
print(f"System: {status['system_state']}")
print(f"Context: {status['context']}")

# Add scheduled break
integration.add_break_reminder(minutes_from_now=60)

integration.shutdown()
```

---

## Integration with Jessica Core

All components are designed to integrate seamlessly with Jessica's existing architecture:

1. **Skills System:** Greeting and Scheduler skills registered in skill loader
2. **Automation Module:** System monitor and context awareness in automation folder
3. **Event-Driven:** All components use callbacks for event handling
4. **Singleton Pattern:** Components use singleton instances for ease of use
5. **Logging:** All components use standard Python logging

---

## Configuration Files

### jessica_schedule.json
Persists scheduled events across sessions
```json
[
  {
    "id": "abc123",
    "title": "Morning standup",
    "description": "Daily team meeting",
    "event_type": "meeting",
    "scheduled_time": "2026-01-09T09:00:00",
    "recurrence": "daily",
    "active": true,
    "notification_before_minutes": 15
  }
]
```

### jessica_context_profile.json
Persists user context and productivity data
```json
{
  "total_sessions": 42,
  "first_session": "2025-12-01T10:00:00",
  "last_session": "2026-01-09T13:25:00",
  "app_frequency": {
    "code.exe": 125,
    "chrome.exe": 98,
    "spotify.exe": 42
  },
  "app_daily_usage": {
    "code.exe": 480,
    "chrome.exe": 240
  },
  "focus_apps": ["code.exe", "pycharm.exe"],
  "distraction_apps": ["spotify.exe", "discord.exe"],
  "productivity_score": 0.75
}
```

---

## Performance Considerations

1. **System Monitor:** Minimal CPU impact
   - Keyboard/mouse listeners: Event-driven, no polling
   - App enumeration: 5-second interval, < 1% CPU
   - Window tracking: Low frequency polling

2. **Context Awareness:** Efficient storage
   - In-memory dictionary for current session
   - JSON serialization for persistence
   - Lazy loading of profiles

3. **Scheduler:** Background monitoring
   - 30-second check interval
   - Single monitoring thread
   - No blocking on main thread

---

## Testing

Run comprehensive tests:
```bash
python -m jessica.tests.test_system_integration
```

Tests include:
1. System Monitor (keyboard, mouse, app tracking)
2. Greeting Skill (time-aware, context-aware)
3. Context Awareness (tracking, analytics)
4. Scheduler (reminders, recurring events)
5. Full System Integration (end-to-end)

---

## Future Enhancements

1. **Machine Learning:** Predictive app suggestions based on patterns
2. **Adaptive Scheduling:** Auto-suggest optimal meeting times
3. **Focus Mode:** Auto-disable notifications during focus sessions
4. **Weekly Reports:** Summary of productivity and patterns
5. **Calendar Integration:** Sync with external calendars
6. **Email Integration:** Unified notification system
7. **Analytics Dashboard:** Visualize productivity metrics
8. **Voice Integration:** Voice-based scheduling and reminders

---

## Dependencies

New packages added to `requirements.txt`:
- `pynput`: Cross-platform keyboard and mouse monitoring
- `pywin32`: Windows-specific system APIs (optional, for enhanced features)

Existing dependencies used:
- `psutil`: System and process utilities
- `torch`, `transformers`: LLM capabilities
- `faiss-cpu`: Semantic memory embeddings

---

## API Reference

### SystemEventMonitor
```python
monitor = get_system_monitor()
monitor.on_user_active = callback
monitor.on_user_idle = callback
monitor.on_app_launched = callback
monitor.on_app_closed = callback
monitor.on_window_changed = callback
monitor.start()
monitor.stop()
monitor.set_idle_threshold(seconds)
monitor.get_state() -> SystemState
```

### GreetingSkill
```python
skill = GreetingSkill()
skill.generate_greeting(context) -> str
skill.should_greet(context) -> bool
skill.set_cooldown(seconds)
skill.enable()
skill.disable()
```

### ContextManager
```python
manager = get_context_manager()
manager.update_context(system_state)
manager.profile.set_focus_apps(apps)
manager.profile.get_stats() -> dict
manager.profile.record_app_activity(app, seconds)
manager.get_personalized_greeting() -> dict
```

### SchedulerSkill
```python
scheduler = SchedulerSkill()
scheduler.add_reminder(title, description, time, recurrence) -> id
scheduler.add_break_reminder(minutes_from_now) -> id
scheduler.add_meditation_session(duration) -> id
scheduler.start_monitoring()
scheduler.list_upcoming_events(hours) -> list
scheduler.on_event_trigger = callback
```

### SystemIntegration
```python
integration = get_system_integration()
integration.initialize(on_greeting_callback)
integration.shutdown()
integration.get_status() -> dict
integration.enable()
integration.disable()
integration.set_idle_threshold(seconds)
integration.add_reminder(title, description, time)
```
