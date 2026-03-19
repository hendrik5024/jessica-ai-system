"""Extended tests for PackageManager to improve coverage."""
import pytest
from jessica.skills.package_manager import PackageManager


class TestPackageManagerExtended:
    """Extended coverage for PackageManager edge cases."""

    def test_package_manager_all_common_packages_accessible(self):
        """Test accessing common packages dictionary."""
        pm = PackageManager()
        # Test a few common ones exist and are accessible
        assert pm.COMMON_PACKAGES.get("requests") is not None
        assert pm.COMMON_PACKAGES.get("numpy") is not None
        assert pm.COMMON_PACKAGES.get("pandas") is not None

    def test_api_resources_have_structure(self):
        """Test API resources have structure."""
        pm = PackageManager()
        assert hasattr(pm, "API_RESOURCES")
        assert len(pm.API_RESOURCES) > 0

    def test_get_api_resource_info_returns_dict(self):
        """Test getting info for API returns dictionary."""
        pm = PackageManager()
        result = pm.get_api_resource_info("openai")
        assert isinstance(result, dict)

    def test_check_optional_dependencies_returns_dict(self):
        """Test checking optional dependencies returns dictionary."""
        pm = PackageManager()
        result = pm.check_optional_dependencies()
        assert isinstance(result, dict)
        assert len(result) > 0

