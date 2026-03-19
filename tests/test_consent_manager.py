"""
Unit tests for ConsentManager.
"""

import pytest
import json
from pathlib import Path
from jessica.automation.consent_manager import ConsentManager


class TestConsentManager:
    """Test ConsentManager functionality."""

    def test_init_creates_defaults(self, temp_consent_file):
        """Test that init creates default consent file."""
        cm = ConsentManager(temp_consent_file)
        assert Path(temp_consent_file).exists()
        
        with open(temp_consent_file) as f:
            data = json.load(f)
        assert "vscode" in data
        assert "excel" in data
        assert "browser" in data

    def test_grant_consent(self, temp_consent_file):
        """Test granting consent."""
        cm = ConsentManager(temp_consent_file)
        cm.grant("excel")
        assert cm.is_allowed("excel") is True

    def test_revoke_consent(self, temp_consent_file):
        """Test revoking consent."""
        cm = ConsentManager(temp_consent_file)
        cm.grant("browser")
        cm.revoke("browser")
        assert cm.is_allowed("browser") is False

    def test_get_all_consents(self, temp_consent_file):
        """Test retrieving all consents."""
        cm = ConsentManager(temp_consent_file)
        all_consents = cm.get_all()
        assert isinstance(all_consents, dict)
        assert "vscode" in all_consents
        assert len(all_consents) >= 5

    def test_vscode_enabled_by_default(self, temp_consent_file):
        """Test that VS Code is enabled by default."""
        cm = ConsentManager(temp_consent_file)
        assert cm.is_allowed("vscode") is True

    def test_others_disabled_by_default(self, temp_consent_file):
        """Test that most capabilities are disabled by default."""
        cm = ConsentManager(temp_consent_file)
        assert cm.is_allowed("excel") is False
        assert cm.is_allowed("browser") is False
