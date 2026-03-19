"""
Audit Log for Jessica

Records all permission checks and security events.
Fully transparent for auditability.
"""

from datetime import datetime
from pathlib import Path
import json


class AuditLog:
    """
    Logs security events and permission checks.
    """

    def __init__(self, log_file="jessica_audit.log"):
        self.log_file = Path(log_file)
        self.logs = self._load_logs()

    def _load_logs(self):
        """Load existing logs from file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return [json.loads(line) for line in f if line.strip()]
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def record(self, action, status, details=None):
        """
        Record an action in the audit log.
        
        Args:
            action: What was attempted (e.g., "memory_write", "system_control")
            status: "allowed", "denied", or other status
            details: Optional additional information
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status
        }

        if details:
            entry["details"] = details

        self.logs.append(entry)
        self._save_entry(entry)

    def _save_entry(self, entry):
        """Append entry to log file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError:
            pass  # Fail silently

    def get_logs(self):
        """Get all log entries."""
        return list(self.logs)

    def get_logs_for_action(self, action):
        """Get logs for a specific action."""
        return [log for log in self.logs if log["action"] == action]

    def get_denied_actions(self):
        """Get all denied actions."""
        return [log for log in self.logs if log["status"] == "denied"]

    def clear_logs(self):
        """Clear all logs (for testing)."""
        self.logs = []
        try:
            self.log_file.unlink()
        except FileNotFoundError:
            pass

    def get_summary(self):
        """Get summary of audit events."""
        total = len(self.logs)
        allowed = sum(1 for log in self.logs if log["status"] == "allowed")
        denied = sum(1 for log in self.logs if log["status"] == "denied")

        return {
            "total_events": total,
            "allowed": allowed,
            "denied": denied,
            "denial_rate": denied / total if total > 0 else 0
        }
