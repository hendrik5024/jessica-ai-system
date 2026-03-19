"""Live Excel workbook automation for Jessica.

Allows Jessica to interact with currently open Excel files using Windows COM.
Features:
- Detect open Excel instances
- Read cell values
- Write to cells
- Get sheet information
- List available sheets
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    import win32com.client
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False


class ExcelLiveController:
    """Control and read from active Excel workbooks via COM automation."""

    def __init__(self):
        self.excel = None
        self.active_workbook = None
        self.active_sheet = None

    def check_dependencies(self) -> Dict[str, bool]:
        """Verify pywin32 is available."""
        return {"pywin32": PYWIN32_AVAILABLE}

    def connect_to_excel(self) -> bool:
        """Connect to the active Excel instance."""
        if not PYWIN32_AVAILABLE:
            return False

        try:
            self.excel = win32com.client.GetObject(Class="Excel.Application")
            if self.excel.Workbooks.Count == 0:
                return False
            
            self.active_workbook = self.excel.ActiveWorkbook
            self.active_sheet = self.excel.ActiveSheet
            return True
        except Exception as e:
            print(f"[excel_live] Failed to connect to Excel: {e}")
            return False

    def get_active_workbook_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active workbook."""
        if not self.connect_to_excel():
            return None

        try:
            info = {
                "name": self.active_workbook.Name,
                "path": self.active_workbook.FullName,
                "sheet_count": self.active_workbook.Sheets.Count,
                "active_sheet": self.active_sheet.Name,
                "sheets": [sheet.Name for sheet in self.active_workbook.Sheets]
            }
            return info
        except Exception as e:
            print(f"[excel_live] Error getting workbook info: {e}")
            return None

    def read_cell(self, cell_ref: str, sheet_name: Optional[str] = None) -> Optional[str]:
        """Read a single cell value.
        
        Args:
            cell_ref: Cell reference like "A1", "B2:B5"
            sheet_name: Sheet name (uses active sheet if not specified)
        """
        if not self.connect_to_excel():
            return None

        try:
            if sheet_name:
                sheet = self.active_workbook.Sheets(sheet_name)
            else:
                sheet = self.active_sheet

            cell = sheet.Range(cell_ref)
            value = cell.Value
            return str(value) if value is not None else "[empty]"
        except Exception as e:
            return f"[excel_live] Error reading {cell_ref}: {e}"

    def write_cell(self, cell_ref: str, value: str, sheet_name: Optional[str] = None) -> bool:
        """Write a value to a cell.
        
        Args:
            cell_ref: Cell reference like "A1"
            value: Value to write
            sheet_name: Sheet name (uses active sheet if not specified)
        """
        if not self.connect_to_excel():
            return False

        try:
            if sheet_name:
                sheet = self.active_workbook.Sheets(sheet_name)
            else:
                sheet = self.active_sheet

            sheet.Range(cell_ref).Value = value
            return True
        except Exception as e:
            print(f"[excel_live] Error writing to {cell_ref}: {e}")
            return False

    def read_range(self, range_ref: str, sheet_name: Optional[str] = None) -> Optional[List[List[str]]]:
        """Read a range of cells.
        
        Args:
            range_ref: Range reference like "A1:C5"
            sheet_name: Sheet name (uses active sheet if not specified)
        """
        if not self.connect_to_excel():
            return None

        try:
            if sheet_name:
                sheet = self.active_workbook.Sheets(sheet_name)
            else:
                sheet = self.active_sheet

            range_obj = sheet.Range(range_ref)
            
            # Handle single cell
            if range_obj.Count == 1:
                val = range_obj.Value
                return [[str(val) if val is not None else ""]]
            
            # Handle range
            rows = []
            for row in range_obj:
                row_data = []
                for cell in row:
                    val = cell.Value
                    row_data.append(str(val) if val is not None else "")
                rows.append(row_data)
            
            return rows
        except Exception as e:
            print(f"[excel_live] Error reading range {range_ref}: {e}")
            return None

    def get_used_range(self, sheet_name: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """Get dimensions of used range (rows, columns).
        
        Returns:
            Tuple of (row_count, column_count)
        """
        if not self.connect_to_excel():
            return None

        try:
            if sheet_name:
                sheet = self.active_workbook.Sheets(sheet_name)
            else:
                sheet = self.active_sheet

            used_range = sheet.UsedRange
            rows = used_range.Rows.Count
            cols = used_range.Columns.Count
            return (rows, cols)
        except Exception as e:
            print(f"[excel_live] Error getting used range: {e}")
            return None

    def get_cell_summary(self, max_rows: int = 10) -> str:
        """Get a summary of the active sheet data."""
        if not self.connect_to_excel():
            return "[excel_live] Not connected to Excel"

        try:
            dims = self.get_used_range()
            if not dims:
                return "[excel_live] Could not determine sheet dimensions"

            rows, cols = dims
            info = self.get_active_workbook_info()
            
            summary = f"📊 Excel Workbook: {info['name']}\n"
            summary += f"📄 Active Sheet: {info['active_sheet']}\n"
            summary += f"📈 Dimensions: {rows} rows × {cols} columns\n"
            summary += f"📑 Sheets: {', '.join(info['sheets'])}\n"
            
            # Show preview of data
            preview_rows = min(max_rows, rows)
            if preview_rows > 0 and cols > 0:
                summary += f"\n🔍 Data Preview (first {preview_rows} rows):\n"
                range_ref = f"A1:{chr(64 + min(cols, 5))}{preview_rows}"
                data = self.read_range(range_ref)
                if data:
                    for i, row in enumerate(data[:max_rows], 1):
                        row_str = " | ".join(str(cell)[:15] for cell in row[:5])
                        if cols > 5:
                            row_str += " | ..."
                        summary += f"  Row {i}: {row_str}\n"
            
            return summary
        except Exception as e:
            return f"[excel_live] Error: {e}"


def can_handle(intent):
    """Check if this skill should handle the intent."""
    text = intent.get("text", "").lower()
    triggers = [
        "read excel",
        "read cell",
        "get cell",
        "what's in",
        "show me",
        "active excel",
        "current spreadsheet",
        "open sheet",
        "current sheet",
    ]
    return any(t in text for t in triggers)


def run(intent, context, relevant, manager):
    """Skill entry point for live Excel operations."""
    controller = ExcelLiveController()
    deps = controller.check_dependencies()

    if not deps["pywin32"]:
        return {"reply": "pywin32 not installed. Install with: pip install pywin32"}

    user_text = intent.get("text", "").lower()

    # Try to connect to Excel
    if not controller.connect_to_excel():
        return {
            "reply": "No active Excel workbook detected. Please open an Excel file first."
        }

    # Get summary of current sheet
    summary = controller.get_cell_summary()
    return {"reply": summary}
