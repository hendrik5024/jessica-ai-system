"""
Helper functions to expose frustration detector to Jessica's agent loop.
"""
from jessica.automation.frustration_detector import FrustrationDetector

# Global frustration detector instance
_frustration_detector = None


def get_frustration_detector() -> FrustrationDetector:
    """Get or create global frustration detector singleton"""
    global _frustration_detector
    if _frustration_detector is None:
        _frustration_detector = FrustrationDetector(
            failure_threshold=3,
            time_window_seconds=300,  # 5 minutes
            cooldown_seconds=900  # 15 minutes
        )
    return _frustration_detector


def track_file_opened(file_path: str):
    """Track file open event - returns assistance dict if frustration detected"""
    detector = get_frustration_detector()
    return detector.track_file_opened(file_path)


def track_error_dialog(error_message: str):
    """Track error dialog - returns assistance dict if frustration detected"""
    detector = get_frustration_detector()
    return detector.track_error_dialog(error_message)


def get_frustration_summary():
    """Get current frustration state summary"""
    detector = get_frustration_detector()
    return detector.get_summary()


def reset_frustration_context(context: str):
    """Reset specific context after user accepts help"""
    detector = get_frustration_detector()
    detector.reset_context(context)
