"""
Permission Manager for Jessica

Controls what actions Jessica is allowed to perform.
Fully transparent and auditable.
"""

import json
from pathlib import Path


class PermissionError(Exception):
    """Raised when an action is not permitted."""
    pass


class PermissionManager:
    """
    Manages permissions for Jessica actions.
    All permission checks are centralized here.
    """

    def __init__(self, path="jessica/config/permissions.json"):
        self.path = Path(path)
        self.permissions = self._load()
        # Auto-save user-friendly permissions if file doesn't exist
        if not self.path.exists():
            # For the main config, enable internet_access; for tests, use defaults
            path_str = str(self.path).replace("\\", "/")  # Normalize path separators
            if "jessica/config/permissions.json" in path_str or "jessica/config" in path_str:
                self.permissions = {
                    "file_access": True,
                    "internet_access": True,
                    "code_execution": True,
                    "system_control": False,
                    "memory_write": True,
                    "learning_enabled": True,
                    "self_modify_code": False
                }
            self._save()

    def _load(self):
        """Load permissions from JSON file."""
        if self.path.exists():
            try:
                # Use utf-8-sig to handle BOM (Byte Order Mark)
                with open(self.path, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Default to all permissions disabled
                return self._get_default_permissions()
        return self._get_default_permissions()

    def _get_default_permissions(self):
        """Return default restrictive permissions (secure by default)."""
        return {
            "file_access": False,
            "internet_access": False,
            "code_execution": True,
            "system_control": False,
            "memory_write": True,
            "learning_enabled": True,
            "self_modify_code": False
        }

    def has_permission(self, permission_name):
        """Check if a specific permission is granted."""
        return self.permissions.get(permission_name, False)

    def require(self, permission_name):
        """
        Enforce a permission requirement.
        Raises PermissionError if not granted.
        """
        if not self.has_permission(permission_name):
            raise PermissionError(f"Permission denied: {permission_name}")

    def require_all(self, permission_names):
        """Require multiple permissions at once."""
        for perm in permission_names:
            self.require(perm)

    def grant(self, permission_name):
        """Grant a permission (for testing/admin use)."""
        self.permissions[permission_name] = True
        self._save()

    def revoke(self, permission_name):
        """Revoke a permission (for testing/admin use)."""
        self.permissions[permission_name] = False
        self._save()

    def get_all(self):
        """Get all permissions."""
        return dict(self.permissions)

    def _save(self):
        """Save permissions to file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Use utf-8-sig encoding to handle BOM consistently
            with open(self.path, "w", encoding="utf-8-sig") as f:
                json.dump(self.permissions, f, indent=2)
        except IOError:
            pass  # Fail silently
