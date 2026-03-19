from typing import Optional, Dict, Any
from jessica.automation.consent_manager import ConsentManager

try:
    import win32com.client
except Exception:
    win32com = None


def is_available() -> bool:
    return win32com is not None


def open_excel(file_path: Optional[str] = None, visible: bool = True, consent: ConsentManager = None) -> Dict[str, Any]:
    if consent and not consent.is_allowed("excel"):
        return {"ok": False, "error": "Excel automation not consented"}
    if not is_available():
        return {"ok": False, "error": "pywin32 not available"}
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = bool(visible)
        wb = None
        if file_path:
            wb = excel.Workbooks.Open(file_path)
        return {
            "ok": True,
            "visible": excel.Visible,
            "workbook_opened": bool(wb is not None),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def write_cell(sheet_name: str, cell: str, value: Any, consent: ConsentManager = None) -> Dict[str, Any]:
    if consent and not consent.is_allowed("excel"):
        return {"ok": False, "error": "Excel automation not consented"}
    if not is_available():
        return {"ok": False, "error": "pywin32 not available"}
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        wb = excel.ActiveWorkbook
        if not wb:
            return {"ok": False, "error": "No active workbook"}
        sheet = wb.Sheets(sheet_name)
        sheet.Range(cell).Value = value
        return {"ok": True, "cell": cell, "value": value}
    except Exception as e:
        return {"ok": False, "error": str(e)}
