"""
Test script for frustration detection system.

Tests:
1. File reopening detection (3 opens in 5 minutes)
2. Undo command frequency (6 undos in 5 minutes)
3. Error dialog repetition (3 errors in 5 minutes)
4. Rapid window switching (10 switches in 60 seconds)
"""
import time
import os
from jessica.config.paths import get_base_dir
from jessica.automation.frustration_detector import FrustrationDetector


def test_file_reopening():
    """Test repeated file opening detection"""
    print("\n=== Test 1: File Reopening ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    file_path = os.path.join(get_base_dir(), "test_file.py")
    
    # Open file 3 times
    for i in range(3):
        result = detector.track_file_opened(file_path)
        print(f"Open {i+1}: {result}")
        time.sleep(0.5)  # Small delay
    
    # Check frustration score
    score = detector.get_frustration_score()
    summary = detector.get_summary()
    
    print(f"\nFrustration Score: {score:.2f}")
    print(f"Summary: {summary}")
    
    assert score > 0.5, "Frustration score should be elevated after 3 reopens"
    print("[PASS] Test passed: File reopening detected")


def test_undo_sequence():
    """Test rapid undo command detection"""
    print("\n=== Test 2: Undo Sequence ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    # Trigger 6 undos (threshold is 2x for undo, so 6 needed)
    result = None
    for i in range(6):
        result = detector.track_undo_command()
        print(f"Undo {i+1}: {result}")
        time.sleep(0.3)
    
    # Check that assistance was triggered
    assert result is not None, "Assistance should be triggered after 6 undos"
    assert result['type'] == 'frustration_detected'
    
    score = detector.get_frustration_score()
    print(f"\nFrustration Score: {score:.2f}")
    print("[PASS] Test passed: Undo sequence detected")


def test_error_repetition():
    """Test repeated error dialog detection"""
    print("\n=== Test 3: Error Repetition ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    error_msg = "TypeError: 'NoneType' object is not subscriptable"
    
    # Trigger same error 3 times
    for i in range(3):
        result = detector.track_error_dialog(error_msg)
        print(f"Error {i+1}: {result}")
        time.sleep(0.5)
    
    # Check frustration score
    score = detector.get_frustration_score()
    summary = detector.get_summary()
    
    print(f"\nFrustration Score: {score:.2f}")
    print(f"Summary: {summary}")
    
    assert score > 0.5, "Frustration score should be elevated after 3 errors"
    print("[PASS] Test passed: Error repetition detected")


def test_rapid_switching():
    """Test rapid window switching detection"""
    print("\n=== Test 4: Rapid Window Switching ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    windows = ["VS Code", "Browser", "Terminal", "VS Code", "Browser", 
               "Terminal", "VS Code", "Browser", "Terminal", "VS Code", "Browser"]
    
    result = None
    for i, window in enumerate(windows):
        result = detector.track_window_switch(window)
        print(f"Switch {i+1} ({window}): {result}")
        time.sleep(0.2)
    
    # Assistance triggered on 10th switch, but we check final result
    # Note: After cooldown trigger, subsequent switches return None
    score = detector.get_frustration_score()
    summary = detector.get_summary()
    
    print(f"\nFrustration Score: {score:.2f}")
    print(f"Summary: {summary}")
    
    # Check that at least one assistance was triggered
    assert summary['triggered_contexts'], "At least one assistance trigger expected"
    
    score = detector.get_frustration_score()
    print(f"\nFrustration Score: {score:.2f}")
    print("[PASS] Test passed: Rapid switching detected")


def test_keyboard_undo_tracking():
    """Test keyboard activity tracking (Ctrl+Z detection)"""
    print("\n=== Test 5: Keyboard Undo Tracking ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    # Simulate Ctrl+Z key presses
    result = None
    for i in range(6):
        result = detector.track_keyboard_activity("ctrl+z")
        print(f"Ctrl+Z {i+1}: {result}")
        time.sleep(0.3)
    
    # Check that assistance was triggered
    assert result is not None, "Assistance should be triggered after 6 Ctrl+Z"
    
    score = detector.get_frustration_score()
    print(f"\nFrustration Score: {score:.2f}")
    print("[PASS] Test passed: Keyboard undo tracking works")


def test_cooldown():
    """Test cooldown prevents spam"""
    print("\n=== Test 6: Cooldown Mechanism ===")
    detector = FrustrationDetector(
        failure_threshold=3, 
        time_window_seconds=300,
        cooldown_seconds=10  # Short cooldown for testing
    )
    
    file_path = os.path.join(get_base_dir(), "test_file.py")
    
    # Trigger first alert
    for i in range(3):
        result = detector.track_file_opened(file_path)
    
    print(f"First alert: {result}")
    
    # Try to trigger again immediately (should be blocked by cooldown)
    for i in range(3):
        result2 = detector.track_file_opened(file_path)
    
    print(f"Second attempt (should be None): {result2}")
    
    assert result2 is None, "Second alert should be blocked by cooldown"
    print("[PASS] Test passed: Cooldown prevents spam")


def test_frustration_summary():
    """Test summary generation"""
    print("\n=== Test 7: Frustration Summary ===")
    detector = FrustrationDetector(failure_threshold=3, time_window_seconds=300)
    
    # Generate multiple frustration signals
    detector.track_file_opened("test.py")
    detector.track_file_opened("test.py")
    detector.track_undo_command()
    detector.track_undo_command()
    detector.track_error_dialog("Test error")
    
    summary = detector.get_summary()
    
    print(f"Summary: {summary}")
    
    assert summary['recent_events'] > 0
    assert 'event_breakdown' in summary
    assert 'frustration_score' in summary
    
    print("[PASS] Test passed: Summary generation works")


if __name__ == "__main__":
    print("=" * 60)
    print("FRUSTRATION DETECTOR TEST SUITE")
    print("=" * 60)
    
    try:
        test_file_reopening()
        test_undo_sequence()
        test_error_repetition()
        test_rapid_switching()
        test_keyboard_undo_tracking()
        test_cooldown()
        test_frustration_summary()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
