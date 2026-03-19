"""
System Event Monitor - Jessica's Awareness of System Events
Handles:
- Laptop wake/login detection
- Keyboard and mouse activity tracking
- Running applications enumeration
- User presence and activity state
"""

import threading
import time
import logging
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import psutil

# Platform-specific imports
import sys
if sys.platform == "win32":
    import win32api
    import win32con
    from pynput import mouse, keyboard
    import subprocess
else:
    from pynput import mouse, keyboard

logger = logging.getLogger("jessica.system_monitor")


@dataclass
class SystemState:
    """Current system state snapshot"""
    is_active: bool
    last_activity: datetime
    active_window: Optional[str]
    active_process: Optional[str]
    running_apps: List[str]
    keyboard_idle_seconds: float
    mouse_idle_seconds: float
    
    def to_dict(self):
        return {
            'is_active': self.is_active,
            'last_activity': self.last_activity.isoformat(),
            'active_window': self.active_window,
            'active_process': self.active_process,
            'running_apps': self.running_apps,
            'keyboard_idle_seconds': self.keyboard_idle_seconds,
            'mouse_idle_seconds': self.mouse_idle_seconds,
        }


class SystemEventMonitor:
    """
    Monitors system events and maintains awareness of:
    - User activity (keyboard, mouse, window changes)
    - System state (wake, sleep, lock)
    - Running applications
    - User presence/idle time
    """

    def __init__(self):
        self.running = False
        self.state = SystemState(
            is_active=True,
            last_activity=datetime.now(),
            active_window=None,
            active_process=None,
            running_apps=[],
            keyboard_idle_seconds=0,
            mouse_idle_seconds=0,
        )
        
        # Event callbacks
        self.on_system_wake: Optional[Callable] = None
        self.on_user_idle: Optional[Callable] = None
        self.on_user_active: Optional[Callable] = None
        self.on_app_launched: Optional[Callable] = None
        self.on_app_closed: Optional[Callable] = None
        self.on_window_changed: Optional[Callable] = None
        self.on_keyboard_press: Optional[Callable] = None  # NEW: For frustration detection
        
        # Configuration
        self.idle_threshold_seconds = 300  # 5 minutes
        self.activity_check_interval = 1   # Check every 1 second
        self.app_check_interval = 5        # Check apps every 5 seconds
        
        # State tracking
        self._last_app_list = set()
        self._was_idle = False
        self._last_window = None
        self._keyboard_last_activity = time.time()
        self._mouse_last_activity = time.time()
        
        # Threads
        self._monitor_thread = None
        self._keyboard_listener = None
        self._mouse_listener = None
        
        logger.info("SystemEventMonitor initialized")

    def start(self):
        """Start monitoring system events"""
        if self.running:
            logger.warning("Monitor already running")
            return
        
        self.running = True
        logger.info("Starting system event monitor")
        
        # Start input listeners
        self._start_input_listeners()
        
        # Start main monitor thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        """Stop monitoring system events"""
        self.running = False
        logger.info("Stopping system event monitor")
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _start_input_listeners(self):
        """Setup keyboard and mouse event listeners"""
        try:
            # Keyboard listener
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_keyboard_press
            )
            self._keyboard_listener.start()
            logger.info("Keyboard listener started")
            
            # Mouse listener
            self._mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click
            )
            self._mouse_listener.start()
            logger.info("Mouse listener started")
            
        except Exception as e:
            logger.error(f"Failed to start input listeners: {e}")

    def _on_keyboard_press(self, key):
        """Called on keyboard press"""
        self._keyboard_last_activity = time.time()
        self.state.last_activity = datetime.now()
        self._check_user_active()
        
        # NEW: Notify frustration detector of key press
        if self.on_keyboard_press:
            try:
                key_name = str(key)
                self.on_keyboard_press(key_name, self.state)
            except Exception as e:
                logger.debug(f"Keyboard callback error: {e}")

    def _on_mouse_move(self, x, y):
        """Called on mouse movement"""
        self._mouse_last_activity = time.time()
        self.state.last_activity = datetime.now()
        self._check_user_active()

    def _on_mouse_click(self, x, y, button, pressed):
        """Called on mouse click"""
        if pressed:
            self._mouse_last_activity = time.time()
            self.state.last_activity = datetime.now()
            self._check_user_active()

    def _monitor_loop(self):
        """Main monitoring loop"""
        app_check_counter = 0
        
        while self.running:
            try:
                # Update idle times
                current_time = time.time()
                self.state.keyboard_idle_seconds = current_time - self._keyboard_last_activity
                self.state.mouse_idle_seconds = current_time - self._mouse_last_activity
                
                # Check activity state
                self._check_user_idle()
                
                # Update window info
                self._update_active_window()
                
                # Periodically check running apps
                app_check_counter += 1
                if app_check_counter >= (self.app_check_interval / self.activity_check_interval):
                    self._update_running_apps()
                    app_check_counter = 0
                
                time.sleep(self.activity_check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(1)

    def _check_user_active(self):
        """Check if user just became active from idle"""
        if self._was_idle:
            self._was_idle = False
            logger.info("User active")
            if self.on_user_active:
                try:
                    self.on_user_active(self.state)
                except Exception as e:
                    logger.error(f"Error in on_user_active callback: {e}")

    def _check_user_idle(self):
        """Check if user is now idle"""
        idle_time = max(self.state.keyboard_idle_seconds, self.state.mouse_idle_seconds)
        is_idle = idle_time >= self.idle_threshold_seconds
        
        if is_idle and not self._was_idle:
            self._was_idle = True
            logger.info(f"User idle for {idle_time:.0f} seconds")
            if self.on_user_idle:
                try:
                    self.on_user_idle(self.state)
                except Exception as e:
                    logger.error(f"Error in on_user_idle callback: {e}")

    def _update_active_window(self):
        """Get the currently active window"""
        try:
            if sys.platform == "win32":
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
                
                if window_title != self._last_window:
                    self._last_window = window_title
                    logger.debug(f"Active window: {window_title}")
                    
                    if self.on_window_changed:
                        try:
                            self.on_window_changed(window_title, self.state)
                        except Exception as e:
                            logger.error(f"Error in on_window_changed callback: {e}")
                
                self.state.active_window = window_title
        except Exception as e:
            logger.debug(f"Failed to get active window: {e}")

    def _update_running_apps(self):
        """Update list of running applications"""
        try:
            current_apps = set()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Get process name
                    app_name = proc.info['name']
                    
                    # Filter out system processes
                    if app_name and not app_name.startswith('System'):
                        current_apps.add(app_name)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Check for new apps
            new_apps = current_apps - self._last_app_list
            for app in new_apps:
                logger.debug(f"App launched: {app}")
                if self.on_app_launched:
                    try:
                        self.on_app_launched(app, self.state)
                    except Exception as e:
                        logger.error(f"Error in on_app_launched callback: {e}")
            
            # Check for closed apps
            closed_apps = self._last_app_list - current_apps
            for app in closed_apps:
                logger.debug(f"App closed: {app}")
                if self.on_app_closed:
                    try:
                        self.on_app_closed(app, self.state)
                    except Exception as e:
                        logger.error(f"Error in on_app_closed callback: {e}")
            
            self._last_app_list = current_apps
            self.state.running_apps = sorted(list(current_apps))
            
        except Exception as e:
            logger.error(f"Failed to update running apps: {e}")

    def get_state(self) -> SystemState:
        """Get current system state"""
        return self.state

    def set_idle_threshold(self, seconds: float):
        """Set idle detection threshold in seconds"""
        self.idle_threshold_seconds = seconds
        logger.info(f"Idle threshold set to {seconds} seconds")

    def set_activity_check_interval(self, seconds: float):
        """Set how often to check activity (in seconds)"""
        self.activity_check_interval = seconds
        logger.info(f"Activity check interval set to {seconds} seconds")


# Singleton instance
_monitor_instance: Optional[SystemEventMonitor] = None


def get_system_monitor() -> SystemEventMonitor:
    """Get or create the system monitor singleton"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemEventMonitor()
    return _monitor_instance


if __name__ == "__main__":
    # Test the system monitor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    monitor = get_system_monitor()
    
    # Define callbacks
    def on_wake(state):
        print(f"✓ User is active! Active window: {state.active_window}")
    
    def on_idle(state):
        print(f"⏸ User is idle for {state.keyboard_idle_seconds:.0f}s")
    
    def on_app_launched(app, state):
        print(f"▶ App launched: {app}")
    
    def on_window_changed(window, state):
        print(f"◆ Window changed: {window}")
    
    # Attach callbacks
    monitor.on_user_active = on_wake
    monitor.on_user_idle = on_idle
    monitor.on_app_launched = on_app_launched
    monitor.on_window_changed = on_window_changed
    
    # Start monitoring
    monitor.start()
    
    try:
        print("System monitor running... (Press Ctrl+C to stop)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitor...")
        monitor.stop()
        print("Monitor stopped")
