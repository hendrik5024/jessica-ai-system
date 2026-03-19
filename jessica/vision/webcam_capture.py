"""Webcam access for Jessica with user approval.

Allows Jessica to capture images from webcam for visual understanding.
All processing happens locally (offline).
"""
from __future__ import annotations

import os
import time
from typing import Optional

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class WebcamCapture:
    """Capture images from webcam with user permission."""

    def __init__(self, camera_index: int = 0, save_dir: str = "jessica/data/webcam"):
        self.camera_index = camera_index
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def check_dependencies(self) -> dict:
        """Check if required libraries are available."""
        return {
            "opencv": CV2_AVAILABLE,
            "pillow": PILLOW_AVAILABLE,
        }

    def capture_frame(self, reason: str = "visual analysis") -> Optional[str]:
        """Capture a single frame from webcam with user approval.
        
        Returns path to saved image if successful, None otherwise.
        """
        if not CV2_AVAILABLE:
            return None

        print(f"[Webcam] Jessica wants to access the camera for: {reason}")
        print("[Webcam] A single frame will be captured and analyzed locally (offline).")
        approve = input("Allow camera access? [y/N]: ").strip().lower()

        if approve not in {"y", "yes"}:
            print("[Webcam] Camera access denied.")
            return None

        try:
            # Initialize camera
            cap = cv2.VideoCapture(self.camera_index)
            
            if not cap.isOpened():
                print("[Webcam] Could not access camera.")
                return None

            # Capture frame
            ret, frame = cap.read()
            cap.release()

            if not ret:
                print("[Webcam] Failed to capture frame.")
                return None

            # Save frame
            timestamp = int(time.time())
            filename = f"webcam_{timestamp}.jpg"
            filepath = os.path.join(self.save_dir, filename)
            cv2.imwrite(filepath, frame)
            
            print(f"[Webcam] Frame captured: {filepath}")
            return filepath

        except Exception as e:
            print(f"[Webcam] Error: {e}")
            return None

    def get_available_cameras(self) -> list:
        """List available camera devices."""
        if not CV2_AVAILABLE:
            return []

        available = []
        for i in range(5):  # Check first 5 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        
        return available


def install_instructions() -> str:
    """Return installation instructions."""
    return """Install webcam support:
    pip install opencv-python pillow

For webcam access, Jessica will:
1. Ask for your permission before each capture
2. Capture a single frame (not video)
3. Process it locally (fully offline)
4. Save it to jessica/data/webcam/"""


def can_handle(intent):
    """Check if this skill should handle camera requests."""
    text = intent.get("text", "").lower()
    triggers = [
        "camera",
        "webcam",
        "take a photo",
        "take a picture",
        "show you via camera",
        "look through camera",
        "see me",
        "visual",
    ]
    return any(t in text for t in triggers)


def run(intent, context, relevant, manager):
    """Skill entry point for webcam requests."""
    webcam = WebcamCapture()
    deps = webcam.check_dependencies()

    if not deps["opencv"]:
        return {"reply": "Webcam support requires opencv-python. Install: pip install opencv-python pillow"}

    user_text = intent.get("text", "")
    
    # Capture frame
    image_path = webcam.capture_frame(reason=user_text)
    
    if not image_path:
        return {"reply": "Camera access was not approved or failed."}

    # For now, just confirm capture
    # In future, integrate with vision model for image understanding
    return {
        "reply": f"I've captured an image from your webcam and saved it at {image_path}. "
                 "In the future, I'll be able to analyze what I see. For now, the image is saved for your review."
    }


if __name__ == "__main__":
    print(install_instructions())
    
    # Test camera access
    webcam = WebcamCapture()
    cameras = webcam.get_available_cameras()
    print(f"\nAvailable cameras: {cameras}")
    
    if cameras:
        print("\nTesting camera capture...")
        result = webcam.capture_frame("test")
        if result:
            print(f"Success! Image saved: {result}")
