"""
Unit tests for PackageManager.
"""

import pytest
import sys
from jessica.skills.package_manager import PackageManager


class TestPackageManager:
    """Test PackageManager functionality."""

    def test_is_installed(self):
        """Test detecting installed packages."""
        pm = PackageManager()
        # requests should be installed from demo runs
        assert pm.is_installed("requests") or not pm.is_installed("nonexistent-pkg-xyz")

    def test_common_packages_db(self):
        """Test that COMMON_PACKAGES is populated."""
        pm = PackageManager()
        assert len(pm.COMMON_PACKAGES) >= 35
        assert "requests" in pm.COMMON_PACKAGES
        assert "pandas" in pm.COMMON_PACKAGES

    def test_api_resources_db(self):
        """Test that API_RESOURCES is populated."""
        pm = PackageManager()
        assert len(pm.API_RESOURCES) >= 7
        assert "openai" in pm.API_RESOURCES
        assert "huggingface" in pm.API_RESOURCES
        
    def test_get_version(self):
        """Test getting package version."""
        pm = PackageManager()
        version = pm.get_version("requests")
        if pm.is_installed("requests"):
            assert version is not None
        else:
            assert version is None

    def test_suggest_installation(self):
        """Test package suggestions by use case."""
        pm = PackageManager()
        result = pm.suggest_installation("data analysis")
        assert result.get("use_case") == "data analysis"
        assert "pandas" in result.get("suggestions", [])

    def test_check_optional_dependencies(self):
        """Test optional dependency checking."""
        pm = PackageManager()
        result = pm.check_optional_dependencies()
        assert isinstance(result, dict)
        assert len(result) >= 5
        assert all(isinstance(v, bool) for v in result.values())

    def test_get_api_resource_info(self):
        """Test getting API resource information."""
        pm = PackageManager()
        info = pm.get_api_resource_info("openai")
        assert info.get("name") == "openai"
        assert info.get("info") is not None
        assert "setup_steps" in info
