from typing import Dict, Any
from jessica.automation.consent_manager import ConsentManager

try:
    from pynput.keyboard import Controller as KeyboardController, Key
    from pynput.mouse import Controller as MouseController, Button
except ImportError:
    KeyboardController = None
    MouseController = None
    Key = None
    Button = None


def is_available() -> bool:
    return KeyboardController is not None and MouseController is not None


def type_text(text: str, consent: ConsentManager = None) -> Dict[str, Any]:
    """Type text using the keyboard."""
    if consent and not consent.is_allowed("keyboard_mouse"):
        return {"ok": False, "error": "Keyboard/mouse control not consented"}
    if not is_available():
        return {"ok": False, "error": "pynput not available"}
    try:
        kb = KeyboardController()
        kb.type(text)
        return {"ok": True, "text_length": len(text)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def press_key(key: str, consent: ConsentManager = None) -> Dict[str, Any]:
    """Press a special key (e.g., 'enter', 'tab')."""
    if consent and not consent.is_allowed("keyboard_mouse"):
        return {"ok": False, "error": "Keyboard/mouse control not consented"}
    if not is_available():
        return {"ok": False, "error": "pynput not available"}
    try:
        kb = KeyboardController()
        key_map = {"enter": Key.enter, "tab": Key.tab, "esc": Key.esc, "backspace": Key.backspace}
        k = key_map.get(key.lower(), key)
        kb.press(k)
        kb.release(k)
        return {"ok": True, "key": key}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def move_mouse(x: int, y: int, consent: ConsentManager = None) -> Dict[str, Any]:
    """Move mouse to position."""
    if consent and not consent.is_allowed("keyboard_mouse"):
        return {"ok": False, "error": "Keyboard/mouse control not consented"}
    if not is_available():
        return {"ok": False, "error": "pynput not available"}
    try:
        mouse = MouseController()
        mouse.position = (x, y)
        return {"ok": True, "position": (x, y)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def click_mouse(button: str = "left", consent: ConsentManager = None) -> Dict[str, Any]:
    """Click mouse button."""
    if consent and not consent.is_allowed("keyboard_mouse"):
        return {"ok": False, "error": "Keyboard/mouse control not consented"}
    if not is_available():
        return {"ok": False, "error": "pynput not available"}
    try:
        mouse = MouseController()
        btn = Button.left if button.lower() == "left" else Button.right
        mouse.click(btn)
        return {"ok": True, "button": button}
    except Exception as e:
        return {"ok": False, "error": str(e)}
