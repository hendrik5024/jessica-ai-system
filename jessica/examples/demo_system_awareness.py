"""
Demo Script: Jessica System Awareness Features
Demonstrates how to use the new system monitoring and greeting features
Run: python -m jessica.examples.demo_system_awareness
"""

import logging
import time
from datetime import datetime, timedelta
from jessica.automation.system_integration import get_system_integration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_basic_monitoring():
    """Demo 1: Basic system monitoring"""
    print("\n" + "="*60)
    print("DEMO 1: Basic System Monitoring")
    print("="*60)
    print("Jessica will monitor your activity for 10 seconds...")
    print("Move your mouse or press a key to trigger events.\n")
    
    integration = get_system_integration()
    
    # Custom greeting callback
    def on_greeting(data):
        if data['type'] == 'wake':
            print(f"✓ GREETING: {data['greeting']}")
        elif data['type'] == 'app_launch':
            print(f"▶ APP LAUNCHED: {data['app']}")
            print(f"  {data['greeting']}")
        elif data['type'] == 'window_change':
            print(f"◆ WINDOW CHANGED: {data['window']}")
        elif data['type'] == 'idle_notification':
            print(f"⏸ IDLE: {data['message']}")
    
    integration.initialize(on_greeting_callback=on_greeting)
    print("System integration started...\n")
    
    # Let it run
    for i in range(10):
        time.sleep(1)
        print(f"[{i+1}/10]", end=" ", flush=True)
    
    print("\n")
    integration.shutdown()
    print("Demo 1 complete!")


def demo_context_awareness():
    """Demo 2: Context awareness and productivity tracking"""
    print("\n" + "="*60)
    print("DEMO 2: Context Awareness & Productivity")
    print("="*60)
    
    from jessica.automation.context_awareness import get_context_manager
    
    manager = get_context_manager()
    
    # Configure apps
    print("\nConfiguring app profiles...")
    focus_apps = [
        'code.exe', 'pycharm.exe', 'vscode.exe', 'notepad.exe'
    ]
    distraction_apps = [
        'spotify.exe', 'discord.exe', 'youtube.exe', 'reddit.com'
    ]
    
    manager.profile.set_focus_apps(focus_apps)
    manager.profile.set_distraction_apps(distraction_apps)
    
    print(f"Focus apps: {', '.join(focus_apps)}")
    print(f"Distraction apps: {', '.join(distraction_apps)}")
    
    # Simulate activity
    print("\nSimulating app usage patterns...")
    
    # Heavy coding day
    manager.profile.record_app_activity('code.exe', 7200)      # 2 hours
    manager.profile.record_app_activity('vscode.exe', 3600)    # 1 hour
    manager.profile.record_app_activity('spotify.exe', 900)    # 15 minutes
    manager.profile.record_app_activity('discord.exe', 600)    # 10 minutes
    
    # Get analytics
    print("\nProductivity Analysis:")
    print("-" * 40)
    
    stats = manager.profile.get_stats()
    print(f"Total apps used today: {stats['total_apps_used']}")
    print(f"Most used app: {stats['top_app']}")
    print(f"Productivity level: {stats['productivity_level'].upper()}")
    
    print("\nApp Usage Breakdown:")
    for app, duration in sorted(stats['today_usage'].items(), 
                                 key=lambda x: x[1], reverse=True):
        hours = duration / 3600
        print(f"  {app}: {hours:.1f} hours")
    
    suggestion = manager.profile.get_context_suggestion()
    print(f"\nFocus recommendation: {suggestion['focus_recommendation']}")
    print(f"Break needed: {suggestion['break_recommendation']}")
    
    greeting = manager.get_personalized_greeting()
    print(f"\nPersonalized greeting: {greeting['greeting']}")
    
    print("\nDemo 2 complete!")


def demo_scheduling():
    """Demo 3: Scheduling and reminders"""
    print("\n" + "="*60)
    print("DEMO 3: Scheduling & Reminders")
    print("="*60)
    
    from jessica.skills.scheduler_skill import SchedulerSkill
    
    scheduler = SchedulerSkill()
    
    print("\nScheduling events for the next 24 hours...\n")
    
    # Add various events
    now = datetime.now()
    
    events = [
        ("Morning standup", "Daily team standup meeting", now + timedelta(hours=1), 'daily', 'meeting'),
        ("Lunch break", "Time to grab lunch", now + timedelta(hours=5), None, 'break'),
        ("Code review", "Review PR #123", now + timedelta(hours=6), None, 'task'),
        ("Meditation", "10-minute meditation session", now + timedelta(hours=8), None, 'meditation'),
        ("1:1 with manager", "Weekly sync", now + timedelta(hours=10), None, 'meeting'),
    ]
    
    for title, description, scheduled_time, recurrence, event_type in events:
        scheduler.add_reminder(title, description, scheduled_time, recurrence)
        print(f"✓ Added: {title}")
    
    # List upcoming events
    print("\nUpcoming events:")
    print("-" * 60)
    
    upcoming = scheduler.list_upcoming_events(hours=24)
    for event in upcoming:
        scheduled = event['scheduled_time']
        hours_from_now = (datetime.fromisoformat(scheduled) - now).total_seconds() / 3600
        print(f"  • {event['title']}")
        print(f"    In {hours_from_now:.1f} hours")
        print(f"    {event['description']}")
    
    print("\nDemo 3 complete!")


def demo_full_integration():
    """Demo 4: Full system integration"""
    print("\n" + "="*60)
    print("DEMO 4: Full System Integration")
    print("="*60)
    
    integration = get_system_integration()
    
    # Comprehensive callback
    greeting_log = []
    
    def on_greeting(data):
        greeting_log.append(data)
        
        event_type = data.get('type', 'unknown')
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Event: {event_type.upper()}")
        
        if 'greeting' in data:
            print(f"  Greeting: {data['greeting']}")
        if 'message' in data:
            print(f"  Message: {data['message']}")
        if 'app' in data:
            print(f"  App: {data['app']}")
        if 'window' in data:
            print(f"  Window: {data['window']}")
        
        if data.get('context'):
            ctx = data['context']
            if 'focus_recommendation' in ctx:
                print(f"  Recommendation: {ctx['focus_recommendation']}")
    
    print("\nInitializing full system integration...")
    print("This will monitor your system activity.\n")
    
    integration.initialize(on_greeting_callback=on_greeting)
    
    # Get status
    status = integration.get_status()
    print("System Status:")
    print(f"  Monitor running: {status['monitor_running']}")
    print(f"  Scheduler running: {status['scheduler_running']}")
    print(f"  Active window: {status['system_state']['active_window']}")
    print(f"  Running apps: {status['system_state']['running_apps'].__len__()} apps")
    
    # Configure
    print("\nConfiguring Jessica...")
    integration.set_idle_threshold(120)  # 2 minutes
    integration.set_greeting_cooldown(60)  # 1 minute between greetings
    
    # Add scheduled events
    print("Adding scheduled events...")
    integration.add_break_reminder(minutes_from_now=3)
    integration.add_meditation_session(duration_minutes=5, scheduled_time=None)
    
    print("\nMonitoring for 30 seconds...")
    print("Move your mouse or change windows to trigger events.\n")
    
    for i in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        if (i + 1) % 10 == 0:
            print(f" [{i+1}s]")
    
    print("\n")
    
    # Summary
    print("\nSession Summary:")
    print(f"  Events triggered: {len(greeting_log)}")
    if greeting_log:
        event_types = {}
        for log in greeting_log:
            event_type = log.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("  Event breakdown:")
        for event_type, count in sorted(event_types.items()):
            print(f"    - {event_type}: {count}")
    
    integration.shutdown()
    print("\nDemo 4 complete!")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "JESSICA SYSTEM AWARENESS DEMO" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    demos = [
        ("Basic Monitoring", demo_basic_monitoring),
        ("Context Awareness", demo_context_awareness),
        ("Scheduling", demo_scheduling),
        ("Full Integration", demo_full_integration),
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all demos in sequence...\n")
    
    for name, demo_func in demos:
        try:
            demo_func()
            print(f"\n✓ {name} completed successfully")
        except KeyboardInterrupt:
            print(f"\n✗ {name} interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("All demos completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
