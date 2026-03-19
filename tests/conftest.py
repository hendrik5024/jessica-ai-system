"""
Pytest configuration and fixtures for Jessica tests.
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path


# Add jessica root to path
JESSICA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(JESSICA_ROOT))


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_consent_file(temp_dir):
    """Temporary consent file for testing."""
    consent_file = temp_dir / ".jessica_consent.json"
    return str(consent_file)
