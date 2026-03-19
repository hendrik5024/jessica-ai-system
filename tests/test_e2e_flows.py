"""
Integration tests for E2E demo flows.
"""

import pytest
from pathlib import Path
from jessica.demos import run_programming_e2e, run_model_e2e, run_office_e2e, run_browser_e2e


class TestE2EFlows:
    """Test end-to-end demo flows."""

    def test_programming_e2e_creates_file(self, capsys, temp_dir):
        """Test programming E2E creates a runnable script."""
        # Redirect demos output
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            run_programming_e2e()
            output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Check that script was created and ran
        assert "Created:" in output
        assert "Run: OK" in output

    def test_model_e2e_downloads_model(self, capsys):
        """Test model E2E downloads and runs inference."""
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            run_model_e2e()
            output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Check that model was processed
        assert "Created:" in output or "Downloading" in output
        assert "Run: OK" in output

    def test_office_e2e_creates_excel(self):
        """Test office E2E creates Excel file."""
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            run_office_e2e()
            output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Check that Excel file was created
        assert "Saved:" in output or "Status: OK" in output

    def test_browser_e2e_fetches_page(self):
        """Test browser E2E fetches and reports."""
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            run_browser_e2e()
            output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Check that page was fetched
        assert "Fetching" in output or "Report saved" in output
        assert "Status: OK" in output
