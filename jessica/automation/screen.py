from typing import Dict, Any, Optional
from jessica.automation.consent_manager import ConsentManager
import os

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


def is_available() -> bool:
    return ImageGrab is not None


def capture_screen(save_path: Optional[str] = None, consent: ConsentManager = None) -> Dict[str, Any]:
    """Capture the entire screen."""
    if consent and not consent.is_allowed("screen_capture"):
        return {"ok": False, "error": "Screen capture not consented"}
    if not is_available():
        return {"ok": False, "error": "PIL/Pillow not available"}
    try:
        img = ImageGrab.grab()
        if save_path:
            img.save(save_path)
            return {"ok": True, "saved": save_path, "size": img.size}
        return {"ok": True, "size": img.size, "saved": False}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def describe_screen(consent: ConsentManager = None) -> Dict[str, Any]:
    """Capture and provide basic screen info (for future vision integration)."""
    if consent and not consent.is_allowed("screen_capture"):
        return {"ok": False, "error": "Screen capture not consented"}
    if not is_available():
        return {"ok": False, "error": "PIL/Pillow not available"}
    try:
        img = ImageGrab.grab()
        return {
            "ok": True,
            "size": img.size,
            "mode": img.mode,
            "note": "Screen captured; vision analysis not yet implemented"
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
