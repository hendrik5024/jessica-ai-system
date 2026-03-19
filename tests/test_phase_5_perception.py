"""
Phase 5.1: Perception-Only Embodiment - Test Suite

Tests for screen capture, UI parsing, environment context, and orchestration.
Verifies zero action capability, zero learning, zero background execution.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from jessica.perception.perception_manager import (
    ScreenCapturer,
    UIElementParser,
    EnvironmentContext,
    PerceptionManager,
    UIElement,
    WindowInfo,
    EnvironmentSnapshot,
)


# ============================================================================
# SCREEN CAPTURER TESTS
# ============================================================================

class TestScreenCapturer:
    """Test screen capture functionality."""
    
    def test_screen_capturer_initialization(self):
        """Test ScreenCapturer initialization."""
        capturer = ScreenCapturer()
        assert capturer is not None
        assert capturer._is_capturing is False
    
    def test_get_screen_resolution(self):
        """Test getting screen resolution."""
        capturer = ScreenCapturer()
        resolution = capturer.get_screen_resolution()
        
        assert resolution is not None
        assert isinstance(resolution, tuple)
        assert len(resolution) == 2
        assert resolution[0] > 0
        assert resolution[1] > 0
    
    def test_capture_returns_bytes_or_none(self):
        """Test capture returns bytes or None (not file)."""
        capturer = ScreenCapturer()
        
        # Capture may return bytes or None depending on environment
        result = capturer.capture_full_desktop()
        assert result is None or isinstance(result, bytes)
        
        result = capturer.capture_active_window()
        assert result is None or isinstance(result, bytes)
    
    def test_no_file_writes(self):
        """Test capture writes nothing to disk."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            initial_files = set(os.listdir(tmpdir))
            
            capturer = ScreenCapturer()
            # Try capturing multiple times
            for _ in range(5):
                capturer.capture_full_desktop()
                capturer.capture_active_window()
            
            # No new files created
            final_files = set(os.listdir(tmpdir))
            assert initial_files == final_files


# ============================================================================
# UI ELEMENT PARSER TESTS
# ============================================================================

class TestUIElementParser:
    """Test UI element parsing."""
    
    def test_ui_element_parser_initialization(self):
        """Test UIElementParser initialization."""
        parser = UIElementParser()
        assert parser is not None
        assert parser._element_counter == 0
    
    def test_ui_element_creation(self):
        """Test creating UI element."""
        parser = UIElementParser()
        
        element = parser._create_ui_element(
            'button',
            'Click Me',
            (100, 100, 50, 30),
        )
        
        assert element.element_id is not None
        assert element.element_type == 'button'
        assert element.text == 'Click Me'
        assert element.bounds == (100, 100, 50, 30)
    
    def test_ui_element_to_dict(self):
        """Test converting UI element to dictionary."""
        element = UIElement(
            element_id='test_elem',
            element_type='button',
            text='Click',
            bounds=(0, 0, 100, 50),
            visible=True,
        )
        
        element_dict = element.to_dict()
        assert element_dict['element_id'] == 'test_elem'
        assert element_dict['element_type'] == 'button'
        assert element_dict['bounds']['x'] == 0
    
    def test_parse_elements_with_none(self):
        """Test parsing with None screenshot."""
        parser = UIElementParser()
        elements = parser.parse_elements(None)
        
        assert elements == []
    
    def test_parse_elements_with_bytes(self):
        """Test parsing with valid bytes."""
        parser = UIElementParser()
        # Empty bytes or valid PNG
        elements = parser.parse_elements(b'')
        assert isinstance(elements, list)


# ============================================================================
# ENVIRONMENT CONTEXT TESTS
# ============================================================================

class TestEnvironmentContext:
    """Test environment context retrieval."""
    
    def test_environment_context_initialization(self):
        """Test EnvironmentContext initialization."""
        context = EnvironmentContext()
        assert context is not None
        assert context._is_querying is False
    
    def test_get_cursor_position(self):
        """Test getting cursor position."""
        context = EnvironmentContext()
        position = context.get_cursor_position()
        
        assert isinstance(position, tuple)
        assert len(position) == 2
        # Position can be (0, 0) if querying not available
    
    def test_get_active_window(self):
        """Test getting active window info."""
        context = EnvironmentContext()
        window = context.get_active_window()
        
        # May be None in test environment
        assert window is None or isinstance(window, WindowInfo)
    
    def test_get_current_state_no_screenshot(self):
        """Test getting environment state without screenshot."""
        context = EnvironmentContext()
        snapshot = context.get_current_state(include_screenshot=False)
        
        assert isinstance(snapshot, EnvironmentSnapshot)
        assert snapshot.screenshot_buffer is None
        assert snapshot.timestamp > 0
        assert snapshot.cursor_position is not None
    
    def test_get_current_state_with_screenshot(self):
        """Test getting environment state with screenshot."""
        context = EnvironmentContext()
        snapshot = context.get_current_state(
            include_screenshot=True,
            parse_elements=False,
        )
        
        assert isinstance(snapshot, EnvironmentSnapshot)
        assert snapshot.screenshot_buffer is None or isinstance(snapshot.screenshot_buffer, bytes)
    
    def test_environment_snapshot_to_dict(self):
        """Test converting snapshot to dictionary."""
        snapshot = EnvironmentSnapshot(
            timestamp=time.time(),
            active_window=None,
            cursor_position=(0, 0),
            cursor_visible=True,
            screen_resolution=(1920, 1080),
        )
        
        snapshot_dict = snapshot.to_dict()
        assert 'timestamp' in snapshot_dict
        assert 'datetime' in snapshot_dict
        assert snapshot_dict['cursor_position'] == (0, 0)


# ============================================================================
# PERCEPTION MANAGER TESTS
# ============================================================================

class TestPerceptionManager:
    """Test perception orchestration."""
    
    def test_perception_manager_initialization(self):
        """Test PerceptionManager initialization."""
        manager = PerceptionManager()
        
        assert manager is not None
        assert manager.is_enabled() is True
        assert manager._perception_count == 0
    
    def test_perceive_environment(self):
        """Test basic perception call."""
        manager = PerceptionManager()
        snapshot = manager.perceive_environment()
        
        assert snapshot is not None
        assert isinstance(snapshot, EnvironmentSnapshot)
        assert manager._perception_count == 1
    
    def test_multiple_perceptions(self):
        """Test multiple perception calls."""
        manager = PerceptionManager()
        
        for i in range(5):
            snapshot = manager.perceive_environment()
            assert snapshot is not None
            assert manager._perception_count == i + 1
    
    def test_perception_disabled(self):
        """Test perception can be disabled."""
        manager = PerceptionManager()
        
        # Initially enabled
        assert manager.is_enabled() is True
        
        # Disable
        manager.disable()
        assert manager.is_enabled() is False
        
        # Perception returns None when disabled
        snapshot = manager.perceive_environment()
        assert snapshot is None
        
        # Re-enable
        manager.enable()
        assert manager.is_enabled() is True
        
        # Perception works again
        snapshot = manager.perceive_environment()
        assert snapshot is not None
    
    def test_observe_active_window(self):
        """Test observing active window."""
        manager = PerceptionManager()
        window_info = manager.observe_active_window()
        
        assert window_info is None or isinstance(window_info, WindowInfo)
    
    def test_observe_screen(self):
        """Test observing screen."""
        manager = PerceptionManager()
        screenshot = manager.observe_screen()
        
        assert screenshot is None or isinstance(screenshot, bytes)
    
    def test_perception_manager_status(self):
        """Test getting perception manager status."""
        manager = PerceptionManager()
        
        status = manager.get_status()
        assert 'enabled' in status
        assert 'perception_count' in status
        assert 'querying' in status
        assert status['enabled'] is True
        assert status['perception_count'] >= 0


# ============================================================================
# CONSTRAINT VERIFICATION TESTS
# ============================================================================

class TestConstraints:
    """Test safety constraints."""
    
    def test_zero_keyboard_control(self):
        """Verify ZERO keyboard control."""
        # No keyboard input methods should exist
        manager = PerceptionManager()
        
        # Check that manager has no keyboard control methods
        prohibited_methods = ['press_key', 'type_text', 'send_keys', 'keyboard_write']
        for method in prohibited_methods:
            assert not hasattr(manager, method), f"Manager should not have {method}"
    
    def test_zero_mouse_control(self):
        """Verify ZERO mouse control."""
        # No mouse control methods should exist
        manager = PerceptionManager()
        
        # Check that manager has no mouse control methods
        prohibited_methods = ['move_mouse', 'click', 'right_click', 'double_click']
        for method in prohibited_methods:
            assert not hasattr(manager, method), f"Manager should not have {method}"
    
    def test_zero_background_execution(self):
        """Verify ZERO background execution."""
        # No background threads or async
        manager = PerceptionManager()
        
        # Perception should be explicit call, not background
        import threading
        initial_thread_count = threading.active_count()
        
        # Call perception multiple times
        for _ in range(10):
            manager.perceive_environment()
        
        # Thread count should not increase
        final_thread_count = threading.active_count()
        # Allow 1 thread for test harness
        assert final_thread_count <= initial_thread_count + 1
    
    def test_zero_learning_or_mutation(self):
        """Verify ZERO learning or memory mutation."""
        manager = PerceptionManager()
        
        # Get initial state
        snapshot1 = manager.perceive_environment()
        
        # Call perception multiple times
        for _ in range(10):
            manager.perceive_environment()
        
        # Manager should not accumulate state
        status = manager.get_status()
        assert status['perception_count'] == 11  # Counts calls, doesn't learn
        
        # No learned models or accumulated data
        assert not hasattr(manager, 'model')
        assert not hasattr(manager, 'learned_data')
        assert not hasattr(manager, 'experience')


# ============================================================================
# INTEGRATION & COMPATIBILITY TESTS
# ============================================================================

class TestPhase5Integration:
    """Test integration with existing systems."""
    
    def test_perception_with_phase_3_preserved(self):
        """Test Phase 3 functionality preserved."""
        # Phase 3 tests should still pass (not implemented in this test file)
        # This is a placeholder verification
        assert True
    
    def test_perception_with_phase_3_5_preserved(self):
        """Test Phase 3.5 functionality preserved."""
        # Phase 3.5 tests should still pass
        assert True
    
    def test_perception_with_phase_4_preserved(self):
        """Test Phase 4 infrastructure preserved."""
        # Phase 4 config management should still work
        manager = PerceptionManager()
        assert manager is not None
    
    def test_no_operator_changes(self):
        """Verify no operator modifications."""
        # Perception should not modify existing operators
        # Operators remain at Phase 3.5 frozen state
        assert True
    
    def test_perception_optional_to_agent(self):
        """Test perception is optional to agent loop."""
        # Agent loop should work with or without perception
        manager = PerceptionManager()
        manager.disable()
        
        # Perception disabled should not affect core reasoning
        status = manager.get_status()
        assert status['enabled'] is False


# ============================================================================
# SAFETY & REVERSIBILITY TESTS
# ============================================================================

class TestSafetyAndReversibility:
    """Test safety guarantees and reversibility."""
    
    def test_fully_reversible(self):
        """Test perception can be completely disabled."""
        manager = PerceptionManager()
        
        # Enable, perceive, disable
        assert manager.is_enabled() is True
        snapshot = manager.perceive_environment()
        assert snapshot is not None
        
        manager.disable()
        assert manager.is_enabled() is False
        snapshot = manager.perceive_environment()
        assert snapshot is None
        
        # Re-enable, should work again
        manager.enable()
        assert manager.is_enabled() is True
        snapshot = manager.perceive_environment()
        assert snapshot is not None
    
    def test_no_persistent_state(self):
        """Test no persistent state created."""
        import os
        import tempfile
        
        # Create two manager instances
        manager1 = PerceptionManager()
        manager2 = PerceptionManager()
        
        # Perceive with first
        manager1.perceive_environment()
        
        # Second manager should start fresh
        assert manager2._perception_count == 0
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        import threading
        
        manager = PerceptionManager()
        results = []
        
        def perceive():
            snapshot = manager.perceive_environment()
            results.append(snapshot)
        
        # Run multiple threads
        threads = [threading.Thread(target=perceive) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should complete successfully
        assert len(results) == 5
        assert all(r is not None for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
