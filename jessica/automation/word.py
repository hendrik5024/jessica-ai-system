from typing import Optional, Dict, Any
from jessica.automation.consent_manager import ConsentManager

try:
    import win32com.client
except Exception:
    win32com = None


def is_available() -> bool:
    return win32com is not None


def open_word(file_path: Optional[str] = None, visible: bool = True, consent: ConsentManager = None) -> Dict[str, Any]:
    if consent and not consent.is_allowed("word"):
        return {"ok": False, "error": "Word automation not consented"}
    if not is_available():
        return {"ok": False, "error": "pywin32 not available"}
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = bool(visible)
        doc = None
        if file_path:
            doc = word.Documents.Open(file_path)
        else:
            doc = word.Documents.Add()
        return {
            "ok": True,
            "visible": word.Visible,
            "document_opened": bool(doc is not None),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def insert_text(text: str, consent: ConsentManager = None) -> Dict[str, Any]:
    if consent and not consent.is_allowed("word"):
        return {"ok": False, "error": "Word automation not consented"}
    if not is_available():
        return {"ok": False, "error": "pywin32 not available"}
    try:
        word = win32com.client.Dispatch("Word.Application")
        doc = word.ActiveDocument
        if not doc:
            return {"ok": False, "error": "No active document"}
        selection = word.Selection
        selection.TypeText(text)
        return {"ok": True, "text_length": len(text)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
