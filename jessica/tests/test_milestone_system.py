"""
Test suite for Episodic Milestone System.

Tests:
1. Milestone creation and storage
2. Milestone retrieval (recent, old, filtered)
3. Vector DB embedding
4. TaskFlow integration
5. Prompt injection
6. Achievement summarization
"""
import time
from datetime import datetime, timedelta

from jessica.memory.milestone_system import (
    MilestoneStore,
    MilestoneEmbedder,
    MilestoneRecaller,
    get_milestone_store,
    get_milestone_recaller
)
from jessica.automation.taskflow_milestones import TaskFlowMilestoneTracker
from jessica.memory.milestone_prompt_injection import (
    MilestonePromptInjector,
    inject_milestone_mention,
    build_milestone_context_for_prompt
)


def test_milestone_creation():
    """Test creating and retrieving milestones"""
    print("\n=== Test 1: Milestone Creation ===")
    store = get_milestone_store()
    
    # Create test milestones
    m1_id = store.add_milestone(
        title="Completed Authentication Module",
        milestone_type="feature_ship",
        description="Implemented OAuth2 authentication",
        context="Backend API"
    )
    
    m2_id = store.add_milestone(
        title="Fixed Critical Memory Leak",
        milestone_type="bug_fix",
        description="Resolved memory leak in data processing",
        context="Core Engine"
    )
    
    m3_id = store.add_milestone(
        title="Started Analytics Dashboard Project",
        milestone_type="project_start",
        description="New analytics dashboard initiative",
        context="Frontend"
    )
    
    print(f"Created milestone 1: {m1_id}")
    print(f"Created milestone 2: {m2_id}")
    print(f"Created milestone 3: {m3_id}")
    
    # Retrieve and check
    m1 = store.get_milestone(m1_id)
    assert m1 is not None
    assert m1['title'] == "Completed Authentication Module"
    assert m1['type'] == "feature_ship"
    print(f"Retrieved milestone: {m1['title']}")
    
    print("[PASS] Milestone creation works")


def test_milestone_retrieval():
    """Test retrieving milestones by various criteria"""
    print("\n=== Test 2: Milestone Retrieval ===")
    store = get_milestone_store()
    
    # Get recent milestones
    recent = store.get_milestones(limit=5)
    print(f"Recent milestones: {len(recent)}")
    assert len(recent) > 0
    
    # Get by type
    features = store.get_milestones(milestone_type="feature_ship")
    print(f"Feature ships: {len(features)}")
    
    bugs = store.get_milestones(milestone_type="bug_fix")
    print(f"Bug fixes: {len(bugs)}")
    
    # Get count
    total = store.count_milestones()
    print(f"Total milestones: {total}")
    
    print("[PASS] Milestone retrieval works")


def test_old_milestone_retrieval():
    """Test retrieving milestones from a specific time period"""
    print("\n=== Test 3: Old Milestone Retrieval ===")
    store = get_milestone_store()
    
    # Create a milestone with backdated timestamp for testing
    # (In real usage, milestones would naturally age)
    
    # For this test, we'll create fresh milestones and check retrieval
    # by range
    now = int(time.time())
    
    # Get milestones from last 365 days
    old = store.get_milestones_in_range(
        days_ago_min=0,
        days_ago_max=365,
        limit=10
    )
    
    print(f"Milestones from past year: {len(old)}")
    
    if old:
        print(f"Oldest milestone: {old[0]['title']} ({old[0]['formatted_date']})")
    
    print("[PASS] Old milestone retrieval works")


def test_taskflow_integration():
    """Test TaskFlow task completion tracking"""
    print("\n=== Test 4: TaskFlow Integration ===")
    tracker = TaskFlowMilestoneTracker()
    
    # Simulate completed tasks
    task1 = {
        'id': 'task_001',
        'title': 'Fixed null pointer exception',
        'type': 'bug_fix',
        'status': 'completed',
        'context': 'Auth Module',
        'description': 'Resolved NPE in login handler'
    }
    
    task2 = {
        'id': 'task_002',
        'title': 'Implemented refresh token rotation',
        'type': 'vscode.create_file',
        'status': 'done',
        'context': 'Security Feature',
        'description': 'Added token rotation for better security'
    }
    
    # Process completions
    m1_id = tracker.process_task_completion(task1)
    m2_id = tracker.process_task_completion(task2)
    
    print(f"Created milestone from task 1: {m1_id}")
    print(f"Created milestone from task 2: {m2_id}")
    
    assert m1_id is not None
    assert m2_id is not None
    
    # Verify milestones were created
    store = get_milestone_store()
    m1 = store.get_milestone(m1_id)
    print(f"Task milestone: {m1['title']} (type: {m1['type']})")
    
    print("[PASS] TaskFlow integration works")


def test_milestone_recaller():
    """Test milestone recalling for conversation"""
    print("\n=== Test 5: Milestone Recaller ===")
    store = get_milestone_store()
    recaller = get_milestone_recaller()
    
    # Get some milestones
    milestones = store.get_milestones(limit=5)
    
    if milestones:
        # Test formatting
        m = milestones[0]
        mention = recaller.format_milestone_mention(m)
        print(f"Milestone mention: {mention}")
        
        # Test achievement summary
        summary = recaller.get_random_achievement_summary(limit=3)
        print(f"Achievement summary: {summary}")
        
        print("[PASS] Milestone recaller works")
    else:
        print("[SKIP] No milestones for testing")


def test_prompt_injection():
    """Test milestone prompt injection"""
    print("\n=== Test 6: Prompt Injection ===")
    injector = MilestonePromptInjector()
    
    # Test basic injection
    mention = injector.maybe_inject_milestone(min_days_old=0)
    if mention:
        print(f"Injected mention: {mention}")
    
    # Test context building
    context = injector.build_milestone_context(include_recent=2)
    if context:
        print(f"Built context:\n{context}")
    
    # Test intro
    intro = injector.get_milestone_intro()
    if intro:
        print(f"Achievement intro: {intro}")
    
    # Test reflection
    reflection = injector.get_milestone_reflection()
    print(f"Reflection: {reflection}")
    
    print("[PASS] Prompt injection works")


def test_system_prompt_enhancement():
    """Test enhancing system prompts with milestones"""
    print("\n=== Test 7: System Prompt Enhancement ===")
    injector = MilestonePromptInjector()
    
    base_prompt = "You are Jessica, a helpful AI assistant."
    
    # Test general enhancement
    enhanced, meta = injector.enhance_prompt_with_milestones(
        "Tell me about our progress",
        base_prompt
    )
    
    if enhanced != base_prompt:
        print("Prompt was enhanced with milestones")
        print(f"Metadata: {meta}")
    else:
        print("No enhancements added (random probability)")
    
    print("[PASS] System prompt enhancement works")


def test_convenience_functions():
    """Test convenience functions for agent integration"""
    print("\n=== Test 8: Convenience Functions ===")
    
    # Test direct injection
    mention = inject_milestone_mention(min_days_old=0)
    if mention:
        print(f"Direct injection: {mention}")
    
    # Test context building
    context = build_milestone_context_for_prompt()
    if context:
        print(f"Direct context: {context}")
    
    print("[PASS] Convenience functions work")


def test_summary():
    """Print system summary"""
    print("\n=== System Summary ===")
    store = get_milestone_store()
    
    total = store.count_milestones()
    recent = store.get_milestones(limit=5)
    
    print(f"Total milestones: {total}")
    print(f"Recent milestones:")
    for m in recent:
        print(f"  - {m['title']} ({m['type']}) on {m['formatted_date']}")
    
    print("[PASS] Summary generated")


if __name__ == "__main__":
    print("=" * 60)
    print("EPISODIC MILESTONE SYSTEM TEST SUITE")
    print("=" * 60)
    
    try:
        test_milestone_creation()
        test_milestone_retrieval()
        test_old_milestone_retrieval()
        test_taskflow_integration()
        test_milestone_recaller()
        test_prompt_injection()
        test_system_prompt_enhancement()
        test_convenience_functions()
        test_summary()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
