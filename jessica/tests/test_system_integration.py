"""
Test script for system monitoring and greeting integration
Run: python -m jessica.tests.test_system_integration
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_system_monitor():
    """Test basic system monitoring"""
    print("\n" + "="*50)
    print("TEST 1: System Monitor")
    print("="*50)
    
    from jessica.automation.system_monitor import get_system_monitor
    
    monitor = get_system_monitor()
    
    # Create callback
    def on_activity(state):
        print(f"✓ User active! Window: {state.active_window}")
    
    monitor.on_user_active = on_activity
    monitor.start()
    
    print("Monitor started. Move your mouse or press a key...")
    time.sleep(5)
    
    state = monitor.get_state()
    print(f"Current state:")
    print(f"  - Active: {state.is_active}")
    print(f"  - Active window: {state.active_window}")
    print(f"  - Running apps: {len(state.running_apps)}")
    print(f"  - Last activity: {state.last_activity}")
    
    monitor.stop()
    print("✓ System monitor test passed")
    return True


def test_greeting_skill():
    """Test greeting skill"""
    print("\n" + "="*50)
    print("TEST 2: Greeting Skill")
    print("="*50)
    
    from jessica.skills.greeting_skill import GreetingSkill, GreetingContext
    
    skill = GreetingSkill()
    
    # Test morning greeting
    context = GreetingContext(
        event_type='wake',
        active_window='VS Code',
        active_app='code.exe',
        time_of_day='morning',
        user_idle_time=3600,
        last_greeting_ago_seconds=float('inf')
    )
    
    greeting = skill.generate_greeting(context)
    print(f"Morning greeting: {greeting}")
    
    # Test afternoon greeting
    context.time_of_day = 'afternoon'
    context.active_app = 'chrome.exe'
    greeting = skill.generate_greeting(context)
    print(f"Afternoon greeting: {greeting}")
    
    print("✓ Greeting skill test passed")
    return True


def test_context_awareness():
    """Test context awareness"""
    print("\n" + "="*50)
    print("TEST 3: Context Awareness")
    print("="*50)
    
    from jessica.automation.context_awareness import get_context_manager
    
    manager = get_context_manager()
    
    # Simulate some activity
    manager.profile.set_focus_apps(['code.exe', 'pycharm.exe', 'vscode.exe'])
    manager.profile.set_distraction_apps(['spotify.exe', 'discord.exe', 'youtube.exe'])
    
    # Simulate app usage
    manager.profile.record_app_activity('code.exe', 3600)  # 1 hour
    manager.profile.record_app_activity('spotify.exe', 1800)  # 30 mins
    
    # Get stats
    stats = manager.profile.get_stats()
    print(f"Stats:")
    print(f"  - Total apps used: {stats['total_apps_used']}")
    print(f"  - Top app: {stats['top_app']}")
    print(f"  - Productivity level: {stats['productivity_level']}")
    
    suggestion = manager.profile.get_context_suggestion()
    print(f"Focus recommendation: {suggestion['focus_recommendation']}")
    
    print("✓ Context awareness test passed")
    return True


def test_scheduler():
    """Test scheduler skill"""
    print("\n" + "="*50)
    print("TEST 4: Scheduler Skill")
    print("="*50)
    
    from jessica.skills.scheduler_skill import SchedulerSkill
    from datetime import datetime, timedelta
    
    scheduler = SchedulerSkill()
    
    # Add test events
    future_time = datetime.now() + timedelta(hours=1)
    reminder_id = scheduler.add_reminder(
        "Test reminder",
        "This is a test reminder",
        future_time
    )
    print(f"Added reminder with ID: {reminder_id}")
    
    # Add break reminder
    break_id = scheduler.add_break_reminder(60)
    print(f"Added break reminder with ID: {break_id}")
    
    # List upcoming events
    upcoming = scheduler.list_upcoming_events(hours=24)
    print(f"Upcoming events in next 24 hours: {len(upcoming)}")
    for event in upcoming:
        print(f"  - {event['title']} at {event['scheduled_time']}")
    
    print("✓ Scheduler test passed")
    return True


def test_system_integration():
    """Test full system integration"""
    print("\n" + "="*50)
    print("TEST 5: Full System Integration")
    print("="*50)
    
    from jessica.automation.system_integration import get_system_integration
    
    integration = get_system_integration()
    
    # Test greeting callback
    greetings_received = []
    def on_greeting(greeting_data):
        greetings_received.append(greeting_data)
        print(f"Greeting received: {greeting_data['type']}")
        if 'greeting' in greeting_data:
            print(f"  Message: {greeting_data['greeting']}")
    
    # Initialize with callback
    integration.initialize(on_greeting_callback=on_greeting)
    
    print("System integration initialized")
    
    # Get status
    status = integration.get_status()
    print(f"Monitor running: {status['monitor_running']}")
    print(f"Scheduler running: {status['scheduler_running']}")
    
    # Let it run for a bit
    print("Running for 5 seconds...")
    time.sleep(5)
    
    integration.shutdown()
    
    print(f"Greetings received: {len(greetings_received)}")
    print("✓ System integration test passed")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*48 + "╗")
    print("║" + " "*10 + "JESSICA SYSTEM INTEGRATION TESTS" + " "*6 + "║")
    print("╚" + "="*48 + "╝")
    
    tests = [
        ("System Monitor", test_system_monitor),
        ("Greeting Skill", test_greeting_skill),
        ("Context Awareness", test_context_awareness),
        ("Scheduler", test_scheduler),
        ("Full Integration", test_system_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} passed")
    
    return all(r for _, r in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
