"""Extended tests for demos to improve coverage."""
import pytest
from jessica.demos import (
    run_programming_e2e,
    run_model_e2e,
    run_office_e2e,
    run_browser_e2e,
)


class TestDemosExtended:
    """Extended coverage for all demo functions."""

    def test_programming_e2e_completes_without_error(self):
        """Test that programming E2E demo completes."""
        try:
            run_programming_e2e()
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.fail(f"Programming E2E demo failed: {e}")

    def test_model_e2e_completes_without_error(self):
        """Test that model E2E demo completes."""
        try:
            run_model_e2e()
            assert True
        except Exception as e:
            pytest.fail(f"Model E2E demo failed: {e}")

    def test_office_e2e_completes_without_error(self):
        """Test that office E2E demo completes."""
        try:
            run_office_e2e()
            assert True
        except Exception as e:
            pytest.fail(f"Office E2E demo failed: {e}")

    def test_browser_e2e_completes_without_error(self):
        """Test that browser E2E demo completes."""
        try:
            run_browser_e2e()
            assert True
        except Exception as e:
            pytest.fail(f"Browser E2E demo failed: {e}")

    def test_all_demos_are_callable(self):
        """Test that all demo functions exist and are callable."""
        assert callable(run_programming_e2e)
        assert callable(run_model_e2e)
        assert callable(run_office_e2e)
        assert callable(run_browser_e2e)
