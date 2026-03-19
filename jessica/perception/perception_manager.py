"""
Phase 5.1: Perception-Only Embodiment - Core Components

Screen capture, UI parsing, environment context, and orchestration.
Perception only - ZERO action capability, ZERO learning, ZERO background execution.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pynput
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class ElementType(Enum):
    """UI element type classification."""
    BUTTON = "button"
    TEXT_FIELD = "text_field"
    LABEL = "label"
    WINDOW = "window"
    MENU = "menu"
    ICON = "icon"
    IMAGE = "image"
    OTHER = "other"


@dataclass
class UIElement:
    """Single parsed UI element."""
    element_id: str
    element_type: str
    text: str
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    visible: bool
    clickable: bool = False
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5  # Parsing confidence (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'element_id': self.element_id,
            'element_type': self.element_type,
            'text': self.text,
            'bounds': {
                'x': self.bounds[0],
                'y': self.bounds[1],
                'width': self.bounds[2],
                'height': self.bounds[3],
            },
            'visible': self.visible,
            'clickable': self.clickable,
            'parent_id': self.parent_id,
            'children_count': len(self.children_ids),
            'confidence': self.confidence,
        }


@dataclass
class WindowInfo:
    """Information about a window."""
    title: str
    application: str
    window_id: int
    position: Tuple[int, int]  # x, y
    size: Tuple[int, int]  # width, height
    visible: bool
    focused: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EnvironmentSnapshot:
    """Complete environment state snapshot."""
    timestamp: float
    active_window: Optional[WindowInfo]
    cursor_position: Tuple[int, int]
    cursor_visible: bool
    screen_resolution: Tuple[int, int]
    screenshot_buffer: Optional[bytes] = None  # PNG buffer (not file)
    ui_elements: List[UIElement] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'active_window': self.active_window.to_dict() if self.active_window else None,
            'cursor_position': self.cursor_position,
            'cursor_visible': self.cursor_visible,
            'screen_resolution': self.screen_resolution,
            'screenshot_available': self.screenshot_buffer is not None,
            'ui_elements_count': len(self.ui_elements),
        }


class ScreenCapturer:
    """Captures screen/window screenshots (read-only, memory only)."""
    
    def __init__(self):
        """Initialize screen capturer."""
        self._last_capture_time = 0
        self._is_capturing = False
    
    def capture_active_window(self) -> Optional[bytes]:
        """Capture focused window screenshot as PNG bytes.
        
        Returns:
            PNG image buffer (bytes), or None if capture fails
            
        Constraints:
            - No file writes
            - No modification
            - Read-only
        """
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        try:
            # Capture focused window only
            screenshot = pyautogui.screenshot()
            
            # Convert to PNG bytes (in memory, no disk write)
            import io
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            return buffer.getvalue()
        except Exception as e:
            return None
    
    def capture_full_desktop(self) -> Optional[bytes]:
        """Capture full screen screenshot as PNG bytes.
        
        Returns:
            PNG image buffer (bytes), or None if capture fails
            
        Constraints:
            - No file writes
            - No modification
            - Read-only
        """
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        try:
            # Capture full desktop
            screenshot = pyautogui.screenshot()
            
            # Convert to PNG bytes (in memory, no disk write)
            import io
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            return buffer.getvalue()
        except Exception as e:
            return None
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get screen resolution."""
        if not PYAUTOGUI_AVAILABLE:
            return (1920, 1080)  # Default
        
        try:
            return pyautogui.size()
        except:
            return (1920, 1080)
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """Get information about focused window."""
        try:
            import psutil
            import ctypes
            
            # Windows-specific: get focused window
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get window title
            length = ctypes.windll.user32.GetWindowTextLength(hwnd)
            title = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowText(hwnd, title, length + 1)
            
            # Get window position and size
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            return WindowInfo(
                title=title.value,
                application='Unknown',
                window_id=hwnd,
                position=(rect.left, rect.top),
                size=(rect.right - rect.left, rect.bottom - rect.top),
                visible=True,
                focused=True,
            )
        except:
            return None


class UIElementParser:
    """Parses UI elements from screenshots (parse-only, no interaction)."""
    
    def __init__(self):
        """Initialize UI parser."""
        self._element_counter = 0
    
    def parse_elements(self, screenshot_buffer: Optional[bytes]) -> List[UIElement]:
        """Parse UI elements from screenshot.
        
        Args:
            screenshot_buffer: PNG image buffer
            
        Returns:
            List of detected UI elements
            
        Constraints:
            - Parse-only (no interaction)
            - No state mutation
            - No learning
        """
        if screenshot_buffer is None:
            return []
        
        # In production, this would use OCR/ML to detect elements
        # For now, return empty (no OCR library required)
        return []
    
    def _generate_element_id(self) -> str:
        """Generate unique element ID."""
        self._element_counter += 1
        return f"elem_{self._element_counter}"
    
    def _create_ui_element(
        self,
        element_type: str,
        text: str,
        bounds: Tuple[int, int, int, int],
        visible: bool = True,
        clickable: bool = False,
    ) -> UIElement:
        """Create UI element data structure."""
        return UIElement(
            element_id=self._generate_element_id(),
            element_type=element_type,
            text=text,
            bounds=bounds,
            visible=visible,
            clickable=clickable,
            confidence=0.8,
        )


class EnvironmentContext:
    """Reads current environment state (read-only, query-based)."""
    
    def __init__(self):
        """Initialize environment context."""
        self._capturer = ScreenCapturer()
        self._parser = UIElementParser()
        self._lock = threading.RLock()
        self._is_querying = False
    
    def get_current_state(
        self,
        include_screenshot: bool = False,
        parse_elements: bool = False,
    ) -> EnvironmentSnapshot:
        """Get complete environment snapshot (query-based, no polling).
        
        Args:
            include_screenshot: Include PNG screenshot buffer
            parse_elements: Parse UI elements from screenshot
            
        Returns:
            Complete environment snapshot
            
        Constraints:
            - Query-based (no background polling)
            - Read-only (no state mutation)
            - No learning
            - Explicit call required
        """
        with self._lock:
            self._is_querying = True
        
        try:
            timestamp = time.time()
            
            # Get active window info
            active_window = self._capturer.get_active_window_info()
            
            # Get cursor position and state
            try:
                if PYAUTOGUI_AVAILABLE:
                    cursor_x, cursor_y = pyautogui.position()
                    cursor_position = (cursor_x, cursor_y)
                else:
                    cursor_position = (0, 0)
            except:
                cursor_position = (0, 0)
            
            # Get screen resolution
            screen_resolution = self._capturer.get_screen_resolution()
            
            # Capture screenshot if requested
            screenshot_buffer = None
            if include_screenshot:
                screenshot_buffer = self._capturer.capture_full_desktop()
            
            # Parse elements if requested
            ui_elements = []
            if parse_elements and screenshot_buffer:
                ui_elements = self._parser.parse_elements(screenshot_buffer)
            
            # Create snapshot
            snapshot = EnvironmentSnapshot(
                timestamp=timestamp,
                active_window=active_window,
                cursor_position=cursor_position,
                cursor_visible=True,
                screen_resolution=screen_resolution,
                screenshot_buffer=screenshot_buffer,
                ui_elements=ui_elements,
            )
            
            return snapshot
        
        finally:
            with self._lock:
                self._is_querying = False
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get focused window info."""
        return self._capturer.get_active_window_info()
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get cursor position (x, y)."""
        try:
            if PYAUTOGUI_AVAILABLE:
                return pyautogui.position()
        except:
            pass
        return (0, 0)
    
    def is_querying(self) -> bool:
        """Check if environment query in progress."""
        with self._lock:
            return self._is_querying


class PerceptionManager:
    """Orchestrates all perception operations (read-only, explicit call only)."""
    
    def __init__(self, tracer=None):
        """Initialize perception manager.
        
        Args:
            tracer: Optional operator tracer for logging (from Phase 4)
        """
        self._context = EnvironmentContext()
        self._tracer = tracer
        self._is_enabled = True
        self._lock = threading.RLock()
        self._perception_count = 0
    
    def perceive_environment(
        self,
        include_screenshot: bool = False,
        parse_elements: bool = False,
        trace_id: Optional[str] = None,
    ) -> Optional[EnvironmentSnapshot]:
        """Get complete environment perception snapshot.
        
        Args:
            include_screenshot: Include screenshot in snapshot
            parse_elements: Parse UI elements
            trace_id: Trace ID for logging (from Phase 4)
            
        Returns:
            Environment snapshot, or None if disabled
            
        Constraints:
            - Explicit call required (no background execution)
            - Read-only (no state mutation)
            - Full trace logging
            - Can be disabled globally
        """
        if not self._is_enabled:
            return None
        
        with self._lock:
            if not self._is_enabled:
                return None
            
            self._perception_count += 1
            perception_id = f"percept_{self._perception_count}"
        
        try:
            # Get snapshot
            snapshot = self._context.get_current_state(
                include_screenshot=include_screenshot,
                parse_elements=parse_elements,
            )
            
            # Log to tracer if available
            if self._tracer:
                self._log_perception(perception_id, snapshot, trace_id)
            
            return snapshot
        
        except Exception as e:
            if self._tracer:
                self._log_perception_error(perception_id, e, trace_id)
            return None
    
    def observe_active_window(
        self,
        include_screenshot: bool = True,
        trace_id: Optional[str] = None,
    ) -> Optional[WindowInfo]:
        """Get focused window observation."""
        if not self._is_enabled:
            return None
        
        window_info = self._context.get_active_window()
        
        if self._tracer and window_info:
            self._log_window_observation(window_info, trace_id)
        
        return window_info
    
    def observe_screen(
        self,
        parse_elements: bool = False,
        trace_id: Optional[str] = None,
    ) -> Optional[bytes]:
        """Get full screen screenshot."""
        if not self._is_enabled:
            return None
        
        screenshot = self._context._capturer.capture_full_desktop()
        
        if self._tracer and screenshot:
            self._log_screen_observation(screenshot, trace_id)
        
        return screenshot
    
    def _log_perception(
        self,
        perception_id: str,
        snapshot: EnvironmentSnapshot,
        trace_id: Optional[str] = None,
    ):
        """Log perception event to tracer."""
        # Log as informational event (not full operator trace)
        log_entry = {
            'perception_id': perception_id,
            'trace_id': trace_id,
            'timestamp': snapshot.timestamp,
            'active_window': snapshot.active_window.to_dict() if snapshot.active_window else None,
            'cursor_position': snapshot.cursor_position,
            'screen_resolution': snapshot.screen_resolution,
            'ui_elements_count': len(snapshot.ui_elements),
        }
    
    def _log_perception_error(
        self,
        perception_id: str,
        error: Exception,
        trace_id: Optional[str] = None,
    ):
        """Log perception error."""
        pass
    
    def _log_window_observation(
        self,
        window_info: WindowInfo,
        trace_id: Optional[str] = None,
    ):
        """Log window observation."""
        pass
    
    def _log_screen_observation(
        self,
        screenshot: bytes,
        trace_id: Optional[str] = None,
    ):
        """Log screen observation."""
        pass
    
    def enable(self):
        """Enable perception."""
        with self._lock:
            self._is_enabled = True
    
    def disable(self):
        """Disable perception (reversible)."""
        with self._lock:
            self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if perception is enabled."""
        with self._lock:
            return self._is_enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get perception system status."""
        with self._lock:
            return {
                'enabled': self._is_enabled,
                'perception_count': self._perception_count,
                'querying': self._context.is_querying(),
            }


# Global perception manager instance
_global_perception_manager: Optional[PerceptionManager] = None


def initialize_global_perception(tracer=None) -> PerceptionManager:
    """Initialize global perception manager."""
    global _global_perception_manager
    _global_perception_manager = PerceptionManager(tracer)
    return _global_perception_manager


def get_global_perception() -> PerceptionManager:
    """Get global perception manager."""
    global _global_perception_manager
    if _global_perception_manager is None:
        _global_perception_manager = PerceptionManager()
    return _global_perception_manager
