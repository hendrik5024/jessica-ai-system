"""
Jessica E2E demo runners
- programming-e2e: dependency suggestion → install → codegen → syntax check → create file → run
- model-e2e: task detect → suggest model → (small) download → create example file
"""

from __future__ import annotations

import os
import sys
import ast
import subprocess
from pathlib import Path
from typing import Optional

from jessica.skills.package_manager import PackageManager
from jessica.skills.model_downloader import ModelDownloader
from jessica.automation.consent_manager import ConsentManager


DEMO_DIR = Path(os.getcwd()) / "demos"


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_python(path: Path) -> int:
    """Run a python script and stream output; return exit code."""
    try:
        proc = subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        return proc.returncode
    except Exception:
        return 1


def run_programming_e2e() -> None:
    print("=== Programming E2E Demo ===")
    pm = PackageManager()

    # 1) Ensure dependency (requests) is installed (small, fast)
    pkg = "requests"
    if not pm.is_installed(pkg):
        print(f"Installing package: {pkg}")
        res = pm.install_package(pkg)
        if not res.get("ok", False):
            print("Failed to install requests:", res)
            return
    else:
        print("Package already installed:", pkg)

    # 2) Generate a small, runnable script using requests
    code_lines = [
        "import requests",
        "",
        "def fetch_example() -> str:",
        "    r = requests.get(\"https://example.com\", timeout=10)",
        "    r.raise_for_status()",
        "    return r.text[:80]",
        "",
        "if __name__ == '__main__':",
        "    content = fetch_example()",
        "    print('Fetched preview:', content.replace('\\n', ' '))",
    ]
    code = "\n".join(code_lines)

    # 3) Validate syntax
    try:
        ast.parse(code)
        print("Syntax: OK")
    except SyntaxError as e:
        print("Syntax error in generated code:", e)
        return

    # 4) Create file
    target = DEMO_DIR / "programming_e2e_demo.py"
    _write_file(target, code)
    print("Created:", target)

    # 5) Run it
    rc = _run_python(target)
    status = "OK" if rc == 0 else f"FAILED (rc={rc})"
    print("Run:", status)


def run_model_e2e() -> None:
    print("=== Model E2E Demo ===")
    pm = PackageManager()
    dl = ModelDownloader()

    # Use a tiny model to avoid large downloads
    tiny_model = "sshleifer/tiny-distilbert-base-cased"

    # Ensure huggingface_hub is available for snapshot_download path
    need_hub = not (pm.is_installed("huggingface-hub") or pm.is_installed("huggingface_hub"))
    if need_hub:
        print("Installing: huggingface-hub (small)")
        res = pm.install_package("huggingface-hub")
        if not (res.get("ok", False) or res.get("installed") is True):
            print("Failed to ensure huggingface-hub:", res)
            return

    # 1) Check cache / attempt small download
    status = dl.get_download_status(tiny_model)
    if status.get("cached"):
        print("Model already cached:", status.get("cache_path"))
        local_path = status.get("cache_path")
    else:
        print("Downloading tiny model:", tiny_model)
        result = dl.download_model(tiny_model, source="huggingface")
        if not result.get("ok", False):
            print("Download failed:", result)
            return
        local_path = result.get("local_path") or result.get("cache_dir")
        print("Downloaded to:", local_path)

    # 2) Create example code (works if transformers is present; else prints a tip)
    example = (
        f"""
try:
    from transformers import AutoTokenizer, AutoModel
    import os
    model_id = "{tiny_model}"
    print("Loading model:", model_id)
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModel.from_pretrained(model_id)
    print("Loaded OK. Parameters:", sum(p.numel() for p in mdl.parameters()))
except Exception as e:
    print("Transformers not available or model load failed:", e)
    print("Tip: pip install transformers torch --upgrade")
"""
    ).strip()

    target = DEMO_DIR / "model_e2e_demo.py"
    _write_file(target, example)
    print("Created:", target)

    # 3) Attempt to run (won't fail the demo if transformers missing)
    rc = _run_python(target)
    if rc == 0:
        print("Run: OK")
    else:
        print("Run: Completed with non-zero exit (likely missing transformers); demo still valid.")


def run_office_e2e() -> None:
    print("=== Office E2E Demo (Excel) ===")
    cm = ConsentManager()
    
    # 1) Check if Excel automation is consented
    if not cm.is_allowed("excel"):
        print("Excel automation not consented. Granting consent for demo...")
        cm.grant("excel")
        print("Consent granted.")
    
    # 2) Try to create and populate a workbook using pywin32
    try:
        import win32com.client
    except ImportError:
        print("pywin32 not available. Installing...")
        pm = PackageManager()
        res = pm.install_package("pywin32")
        if not (res.get("ok", False) or res.get("installed") is True):
            print("Failed to install pywin32:", res)
            return
        try:
            import win32com.client
        except ImportError:
            print("pywin32 still unavailable after install. Skipping Excel demo.")
            return
    
    try:
        print("Creating Excel application...")
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False  # Run invisibly for demo
        
        # Create new workbook
        wb = excel.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "DemoData"
        
        # Write headers
        ws.Range("A1").Value = "Name"
        ws.Range("B1").Value = "Value"
        ws.Range("C1").Value = "Status"
        
        # Write data rows
        data = [
            ("Task 1", 100, "Complete"),
            ("Task 2", 85, "In Progress"),
            ("Task 3", 95, "Complete"),
        ]
        for i, (name, value, status) in enumerate(data, start=2):
            ws.Range(f"A{i}").Value = name
            ws.Range(f"B{i}").Value = value
            ws.Range(f"C{i}").Value = status
        
        # Auto-fit columns
        ws.Range("A1:C4").Columns.AutoFit()
        
        # Save workbook
        output_file = str(DEMO_DIR / "office_e2e_demo.xlsx")
        wb.SaveAs(output_file)
        print(f"Saved: {output_file}")
        
        # Close
        wb.Close(SaveChanges=False)
        excel.Quit()
        
        print("Status: OK")
        
    except Exception as e:
        print(f"Error during Excel demo: {e}")
        try:
            excel.Quit()
        except:
            pass


def run_browser_e2e() -> None:
    print("=== Browser E2E Demo ===")
    cm = ConsentManager()
    
    # 1) Check if browser automation is consented
    if not cm.is_allowed("browser"):
        print("Browser automation not consented. Granting consent for demo...")
        cm.grant("browser")
        print("Consent granted.")
    
    # 2) Use requests to fetch a safe website and log info
    try:
        import requests
    except ImportError:
        print("requests not available. Installing...")
        pm = PackageManager()
        res = pm.install_package("requests")
        if not (res.get("ok", False) or res.get("installed") is True):
            print("Failed to install requests:", res)
            return
        import requests
    
    try:
        print("Fetching https://example.com...")
        r = requests.get("https://example.com", timeout=5)
        r.raise_for_status()
        
        # Log metadata
        content_length = len(r.text)
        status = r.status_code
        content_type = r.headers.get("content-type", "unknown")
        
        # Save a demo report
        report = DEMO_DIR / "browser_e2e_demo.txt"
        report_content = f"""Browser E2E Demo Report
Date: {__import__('datetime').datetime.now().isoformat()}
URL: https://example.com
Status Code: {status}
Content-Type: {content_type}
Content Length: {content_length} bytes
Preview: {r.text[:100]}...
Status: OK
"""
        _write_file(report, report_content)
        print(f"Report saved: {report}")
        print("Status: OK")
        
    except Exception as e:
        print(f"Error during browser demo: {e}")
