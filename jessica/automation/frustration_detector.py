"""
Frustration Detector - Monitors user behavior patterns for frustration signals.

Tracks:
- File open/close patterns (repeated opens of same file)
- Undo command frequency (Ctrl+Z detection)
- Error patterns from OCR (repeated error dialogs)
- Rapid window switching (context-switching behavior)

Triggers proactive assistance when frustration threshold is reached.
"""
from __future__ import annotations

import time
import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Deque
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("jessica.frustration_detector")


@dataclass
class FrustrationEvent:
    """Single frustration signal event"""
    event_type: str  # 'file_reopen', 'undo', 'error_dialog', 'rapid_switch'
    timestamp: float
    context: str  # File name, error message, etc.
    severity: float  # 0.0 - 1.0


class FrustrationDetector:
    """
    Monitors user behavior for frustration signals.
    
    Triggers proactive assistance after detecting repeated failing actions.
    """
    
    def __init__(
        self, 
        failure_threshold: int = 3,
        time_window_seconds: int = 300,  # 5 minutes
        cooldown_seconds: int = 900  # 15 minutes
    ):
        self.failure_threshold = failure_threshold
        self.time_window_seconds = time_window_seconds
        self.cooldown_seconds = cooldown_seconds
        
        # Event tracking
        self.events: Deque[FrustrationEvent] = deque(maxlen=100)
        self.file_open_history: Dict[str, List[float]] = defaultdict(list)
        self.undo_timestamps: List[float] = []
        self.error_history: Dict[str, List[float]] = defaultdict(list)
        self.window_switch_timestamps: List[float] = []
        
        # State tracking
        self.last_assistance_trigger = 0.0
        self.current_frustration_score = 0.0
        self.triggered_contexts = set()  # Avoid duplicate triggers for same context
        
        # Activity tracking
        self.last_file_opened: Optional[str] = None
        self.last_window: Optional[str] = None
        self.window_switch_count = 0
        
        logger.info(f"FrustrationDetector initialized (threshold={failure_threshold}, window={time_window_seconds}s)")
    
    def track_file_opened(self, file_path: str) -> Optional[Dict]:
        """
        Track file open event. Detects repeated file reopening.
        
        Returns proactive assistance dict if frustration detected.
        """
        now = time.time()
        
        # Normalize path
        normalized = file_path.lower().strip()
        
        # Track this open
        self.file_open_history[normalized].append(now)
        
        # Clean old entries (outside time window)
        cutoff = now - self.time_window_seconds
        self.file_open_history[normalized] = [
            ts for ts in self.file_open_history[normalized] if ts > cutoff
        ]
        
        # Count opens in time window
        open_count = len(self.file_open_history[normalized])
        
        # Record event
        if open_count > 1:
            event = FrustrationEvent(
                event_type='file_reopen',
                timestamp=now,
                context=normalized,
                severity=min(open_count / self.failure_threshold, 1.0)
            )
            self.events.append(event)
            logger.debug(f"File reopened {open_count} times: {normalized}")
        
        # Check threshold
        if open_count >= self.failure_threshold:
            return self._maybe_trigger_assistance(
                context=f"file:{normalized}",
                message=f"I noticed you've reopened this file {open_count} times in the last few minutes. Would you like me to help troubleshoot or find related documentation?"
            )
        
        return None
    
    def track_undo_command(self) -> Optional[Dict]:
        """
        Track Ctrl+Z (undo) command. Detects rapid undo sequences.
        
        Returns proactive assistance dict if frustration detected.
        """
        now = time.time()
        
        # Track this undo
        self.undo_timestamps.append(now)
        
        # Clean old entries
        cutoff = now - self.time_window_seconds
        self.undo_timestamps = [ts for ts in self.undo_timestamps if ts > cutoff]
        
        # Count undos in time window
        undo_count = len(self.undo_timestamps)
        
        # Record event
        event = FrustrationEvent(
            event_type='undo',
            timestamp=now,
            context='undo_sequence',
            severity=min(undo_count / (self.failure_threshold * 2), 1.0)
        )
        self.events.append(event)
        logger.debug(f"Undo count: {undo_count}")
        
        # Check threshold (use 2x threshold for undo since it's common)
        if undo_count >= self.failure_threshold * 2:
            return self._maybe_trigger_assistance(
                context="undo_sequence",
                message=f"I noticed you've used undo {undo_count} times recently. It looks like we might be stuck on something. Would you like me to suggest a different approach or review the logic?"
            )
        
        return None
    
    def track_error_dialog(self, error_message: str) -> Optional[Dict]:
        """
        Track error dialog appearance (from OCR or system monitoring).
        
        Returns proactive assistance dict if frustration detected.
        """
        now = time.time()
        
        # Normalize error message
        normalized = error_message.lower().strip()[:100]  # First 100 chars
        
        # Track this error
        self.error_history[normalized].append(now)
        
        # Clean old entries
        cutoff = now - self.time_window_seconds
        self.error_history[normalized] = [
            ts for ts in self.error_history[normalized] if ts > cutoff
        ]
        
        # Count occurrences
        error_count = len(self.error_history[normalized])
        
        # Record event
        event = FrustrationEvent(
            event_type='error_dialog',
            timestamp=now,
            context=normalized,
            severity=min(error_count / self.failure_threshold, 1.0)
        )
        self.events.append(event)
        logger.info(f"Error dialog repeated {error_count} times: {normalized[:50]}...")
        
        # Check threshold
        if error_count >= self.failure_threshold:
            return self._maybe_trigger_assistance(
                context=f"error:{normalized}",
                message=f"I've noticed this error appearing {error_count} times: '{error_message[:80]}...' Would you like me to research this error or suggest alternative solutions?"
            )
        
        return None
    
    def track_window_switch(self, window_title: str) -> Optional[Dict]:
        """
        Track window switching. Detects rapid context switching (possible frustration).
        
        Returns proactive assistance dict if frustration detected.
        """
        now = time.time()
        
        # Only count if actually switching to different window
        if window_title != self.last_window:
            self.last_window = window_title
            self.window_switch_timestamps.append(now)
            
            # Clean old entries
            cutoff = now - 60  # Check for rapid switching in last 60 seconds
            self.window_switch_timestamps = [
                ts for ts in self.window_switch_timestamps if ts > cutoff
            ]
            
            # Count switches
            switch_count = len(self.window_switch_timestamps)
            
            # Detect rapid switching (10+ switches in 60 seconds)
            if switch_count >= 10:
                event = FrustrationEvent(
                    event_type='rapid_switch',
                    timestamp=now,
                    context='rapid_context_switching',
                    severity=min(switch_count / 15, 1.0)
                )
                self.events.append(event)
                logger.info(f"Rapid window switching detected: {switch_count} switches")
                
                return self._maybe_trigger_assistance(
                    context="rapid_switching",
                    message="I noticed you've been switching between windows rapidly. Are you looking for something specific? I can help search or organize your workflow."
                )
        
        return None
    
    def track_keyboard_activity(self, key_name: str) -> Optional[Dict]:
        """
        Track keyboard activity for frustration signals.
        
        Detects Ctrl+Z (undo) automatically.
        """
        # Detect Ctrl+Z
        if 'ctrl' in key_name.lower() and 'z' in key_name.lower():
            return self.track_undo_command()
        
        return None
    
    def get_frustration_score(self) -> float:
        """
        Calculate current frustration score (0.0 - 1.0) based on recent events.
        
        Returns weighted average of recent event severities.
        """
        now = time.time()
        cutoff = now - self.time_window_seconds
        
        # Get recent events
        recent_events = [e for e in self.events if e.timestamp > cutoff]
        
        if not recent_events:
            return 0.0
        
        # Weight recent events more heavily
        total_weight = 0.0
        weighted_severity = 0.0
        
        for event in recent_events:
            age = now - event.timestamp
            # Exponential decay: newer events weighted more
            weight = 1.0 / (1.0 + age / 60.0)  # Decay over 60 seconds
            weighted_severity += event.severity * weight
            total_weight += weight
        
        score = weighted_severity / total_weight if total_weight > 0 else 0.0
        self.current_frustration_score = score
        
        return score
    
    def _maybe_trigger_assistance(self, context: str, message: str) -> Optional[Dict]:
        """
        Check if we should trigger proactive assistance.
        
        Returns assistance dict or None if on cooldown or already triggered for this context.
        """
        now = time.time()
        
        # Check cooldown
        if (now - self.last_assistance_trigger) < self.cooldown_seconds:
            logger.debug(f"Assistance on cooldown (triggered {(now - self.last_assistance_trigger):.0f}s ago)")
            return None
        
        # Check if already triggered for this context
        if context in self.triggered_contexts:
            logger.debug(f"Already triggered for context: {context}")
            return None
        
        # Trigger assistance
        self.last_assistance_trigger = now
        self.triggered_contexts.add(context)
        
        logger.info(f"🚨 Frustration detected! Triggering proactive assistance: {context}")
        
        return {
            'type': 'frustration_detected',
            'context': context,
            'message': message,
            'frustration_score': self.get_frustration_score(),
            'timestamp': now,
            'voice_alert': True,  # Enable voice notification
            'priority': 'high'
        }
    
    def reset_context(self, context: str):
        """Reset triggered state for a specific context (e.g., after user accepts help)"""
        if context in self.triggered_contexts:
            self.triggered_contexts.remove(context)
            logger.debug(f"Reset context: {context}")
    
    def clear_history(self):
        """Clear all tracking history (useful for testing or manual reset)"""
        self.events.clear()
        self.file_open_history.clear()
        self.undo_timestamps.clear()
        self.error_history.clear()
        self.window_switch_timestamps.clear()
        self.triggered_contexts.clear()
        self.current_frustration_score = 0.0
        logger.info("Frustration detector history cleared")
    
    def get_summary(self) -> Dict:
        """Get summary of current frustration state"""
        now = time.time()
        cutoff = now - self.time_window_seconds
        
        recent_events = [e for e in self.events if e.timestamp > cutoff]
        
        return {
            'frustration_score': self.get_frustration_score(),
            'recent_events': len(recent_events),
            'event_breakdown': {
                'file_reopens': len([e for e in recent_events if e.event_type == 'file_reopen']),
                'undos': len([e for e in recent_events if e.event_type == 'undo']),
                'errors': len([e for e in recent_events if e.event_type == 'error_dialog']),
                'rapid_switches': len([e for e in recent_events if e.event_type == 'rapid_switch'])
            },
            'cooldown_remaining': max(0, self.cooldown_seconds - (now - self.last_assistance_trigger)),
            'triggered_contexts': list(self.triggered_contexts)
        }
