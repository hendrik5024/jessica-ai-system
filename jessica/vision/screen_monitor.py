"""Screen monitoring and vision capabilities for Jessica.

Future capability: allows Jessica to take screenshots, perform OCR,
and understand what the user is currently doing on their laptop.

PRIVACY NOTE: All processing happens locally. No data leaves your machine.
User approval is required before any screen capture.
"""
from __future__ import annotations

import os
import time
from typing import Dict, Optional

try:
    from PIL import ImageGrab
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    # Configure pytesseract to find Tesseract on Windows
    import platform
    if platform.system() == "Windows":
        pytesseract.pytesseract.pytesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except ImportError:
    TESSERACT_AVAILABLE = False


class ScreenMonitor:
    """Captures and analyzes screen content with user permission."""

    def __init__(self, screenshots_dir: str = "jessica/data/screenshots"):
        self.screenshots_dir = screenshots_dir
        os.makedirs(screenshots_dir, exist_ok=True)
        self.last_capture_time: Optional[float] = None

    def check_dependencies(self) -> Dict[str, bool]:
        """Verify required libraries are installed."""
        return {
            "pillow": PILLOW_AVAILABLE,
            "tesseract": TESSERACT_AVAILABLE,
        }

    def request_screenshot(self, reason: str = "analysis", approval_callback=None) -> Optional[str]:
        """Request permission and capture a screenshot.

        Returns the path to the saved screenshot if approved, None otherwise.
        """
        if not PILLOW_AVAILABLE:
            return None

        # Use GUI approval if callback provided, otherwise fall back to terminal
        if approval_callback:
            approve = approval_callback(f"Jessica wants to take a screenshot for: {reason}\nYour screen will be captured and analyzed locally (offline).")
        else:
            print(f"[vision] Jessica wants to take a screenshot for: {reason}")
            print("[vision] Your screen will be captured and analyzed locally (offline).")
            approve = input("Allow screenshot? [y/N]: ").strip().lower()
            approve = approve in {"y", "yes"}

        if not approve:
            return None

        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            filename = f"screen_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            screenshot.save(filepath)
            self.last_capture_time = time.time()
            print(f"[vision] Screenshot saved: {filepath}")
            return filepath
        except Exception as exc:
            print(f"[vision] Screenshot failed: {exc}")
            return None

    def extract_text(self, image_path: str) -> Optional[str]:
        """Extract text from a screenshot using OCR."""
        if not TESSERACT_AVAILABLE:
            return "[vision] Tesseract OCR not installed. Install: pip install pytesseract"

        try:
            # Ensure path is set before use
            import platform
            if platform.system() == "Windows":
                pytesseract.pytesseract.pytesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as exc:
            return f"[vision] OCR failed: {exc}"

    def describe_screen(self, context: str = "", approval_callback=None) -> str:
        """Capture screen and provide a text description.

        This is the main entry point for Jessica to "see" what you're doing.
        """
        deps = self.check_dependencies()
        if not deps["pillow"]:
            return "[vision] Screen capture requires Pillow. Install: pip install Pillow"

        reason = f"understand current context: {context}" if context else "see what you're working on"
        screenshot_path = self.request_screenshot(reason, approval_callback)

        if not screenshot_path:
            return "[vision] Screenshot was not approved or failed."

        # Return success message with path - OCR is optional
        result = f"[vision] Screenshot captured successfully!\nSaved to: {screenshot_path}\n"
        
        # Try OCR if available, but don't fail if it's not
        if deps["tesseract"]:
            text = self.extract_text(screenshot_path)
            if text and not text.startswith("[vision]"):
                result += f"\nText found on screen:\n{text}"
            else:
                result += "\nOCR attempted but no text extracted (or Tesseract configuration issue)."
        else:
            result += "\nNote: Install Tesseract OCR to extract text from screenshots."
        
        return result


def can_handle(intent):
    """Check if this skill should handle the intent."""
    text = intent.get("text", "").lower()
    triggers = [
        "screenshot",
        "see my screen",
        "what am i doing",
        "look at my screen",
        "capture screen",
        "show you my screen",
    ]
    return any(t in text for t in triggers)


def run(intent, context, relevant, manager):
    """Skill entry point for screen monitoring requests."""
    monitor = ScreenMonitor()
    user_text = intent.get("text", "")
    result = monitor.describe_screen(context=user_text)
    return {"reply": result}
