"""
Self-Upgrade API and Integration Guide
Complete API for using Jessica's self-upgrade system.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from jessica.automation.self_upgrade_integration import SelfUpgradeManager
from jessica.automation.improvement_scheduler import ImprovementScheduler, PerformanceMonitor
from jessica.monitoring.self_upgrade_dashboard import MonitoringDashboard
from jessica.skills.improvement_request_skill import ImprovementRequestSkill

logger = logging.getLogger("jessica.api.self_upgrade")


class SelfUpgradeAPI:
    """
    Complete API for Jessica's self-upgrade system.
    Provides all methods needed for integration and user interaction.
    """

    def __init__(self):
        """Initialize the complete self-upgrade system."""
        self.manager = SelfUpgradeManager()
        self.scheduler = ImprovementScheduler(self.manager, check_interval=3600)
        self.dashboard = MonitoringDashboard(self.manager, self.scheduler)
        self.request_skill = ImprovementRequestSkill(self.manager)
        self.performance_monitor = PerformanceMonitor()

        logger.info("SelfUpgradeAPI initialized")

    # ========== Agent Loop Integration ==========

    def check_improvements(self) -> Optional[Dict[str, Any]]:
        """
        Called periodically by Jessica's agent loop.
        Returns improvement proposals if available.
        """
        return self.manager.check_for_improvements()

    def apply_pending_improvements(self) -> Dict[str, Any]:
        """
        Apply improvements during quiet periods.
        Called by agent loop when idle.
        """
        return self.manager.apply_pending_improvements()

    # ========== User-Requested Improvements ==========

    def request_improvement(self, query: str) -> Dict[str, Any]:
        """
        User requests an improvement. Parse and process naturally.
        
        Example queries:
        - "Improve greeting_skill to add emoji support"
        - "Add multilingual support to greeting_skill"
        - "Optimize system_monitor for performance"
        """
        return self.request_skill.handle_improvement_request(query)

    def approve_improvement(self, proposal_id: str) -> Dict[str, Any]:
        """Approve a proposed improvement for deployment."""
        return self.request_skill.approve_improvement(proposal_id)

    def reject_improvement(self, proposal_id: str) -> Dict[str, Any]:
        """Reject a proposed improvement."""
        return self.request_skill.reject_improvement(proposal_id)

    def list_pending(self) -> Dict[str, Any]:
        """List all pending improvements awaiting approval."""
        return self.request_skill.list_pending_improvements()

    def get_improvement_status(self, proposal_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific improvement."""
        return self.request_skill.get_improvement_status(proposal_id)

    # ========== Automated Cycles ==========

    def start_auto_improvements(self, interval_hours: int = 1):
        """
        Start automatic improvement scheduler.
        Jessica will periodically propose improvements.
        """
        self.manager.setup_improvement_scheduler(interval_hours)
        self.scheduler.start()
        logger.info(f"Auto improvements started ({interval_hours}h interval)")

    def stop_auto_improvements(self):
        """Stop the automatic improvement scheduler."""
        self.scheduler.stop()
        logger.info("Auto improvements stopped")

    def trigger_improvement_check(self) -> Dict[str, Any]:
        """Manually trigger an improvement check (for testing)."""
        return self.scheduler.propose_now()

    # ========== Monitoring & Analytics ==========

    def get_status_report(self) -> str:
        """Get human-readable status report."""
        return self.manager.get_status_report()

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive improvement statistics."""
        return self.manager.get_improvement_statistics()

    def get_history(self, limit: int = 50) -> list:
        """Get improvement history."""
        return self.manager.get_audit_log(limit=limit)

    def get_audit_log(self, action_filter: Optional[str] = None, limit: int = 50) -> list:
        """
        Get audit log with optional filtering.
        
        Actions: 'improvement_proposed', 'improvement_deployed', 'improvement_rejected'
        """
        return self.manager.get_audit_log(action_filter, limit)

    # ========== Dashboard & UI ==========

    def generate_dashboard(self) -> str:
        """Generate HTML dashboard."""
        return self.dashboard.generate_dashboard_html()

    def save_dashboard(self) -> Optional[Path]:
        """Save dashboard to HTML file."""
        return self.dashboard.save_dashboard()

    def get_json_status(self) -> Dict[str, Any]:
        """Get current status as JSON (for API/REST endpoints)."""
        return self.dashboard.get_json_status()

    # ========== Performance Monitoring ==========

    def record_interaction(self, response_time: float, success: bool, capability: str = None):
        """Record an interaction for performance tracking."""
        self.performance_monitor.record_interaction(response_time, success, capability)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.performance_monitor.get_statistics()

    def should_optimize(self, metric: str, threshold: float) -> bool:
        """Check if optimization is needed for a metric."""
        return self.performance_monitor.should_optimize(metric, threshold)

    # ========== Configuration ==========

    def configure_approval_requirement(self, require_approval: bool = True):
        """Configure whether improvements require user approval."""
        self.manager.require_approval = require_approval
        logger.info(f"Approval requirement: {require_approval}")

    def configure_auto_interval(self, hours: int = 1):
        """Configure auto-improvement check interval."""
        self.manager.setup_improvement_scheduler(hours)
        logger.info(f"Auto-improvement interval: {hours} hours")

    # ========== Diagnostics ==========

    def health_check(self) -> Dict[str, Any]:
        """Check health of self-upgrade system."""
        return {
            'manager': 'ok' if self.manager else 'error',
            'scheduler': 'running' if self.scheduler.running else 'stopped',
            'dashboard': 'ok' if self.dashboard else 'error',
            'audit_log_exists': self.manager.audit_log_path.exists(),
            'staging_available': self.manager.staging.staging_dir.exists(),
            'versions_available': self.manager.versioning.versions_dir.exists(),
        }


# ========== Integration Examples ==========

def integrate_with_agent_loop(agent_loop, api: SelfUpgradeAPI):
    """
    Example: Integrate self-upgrade into agent's main loop.
    
    Call this during Jessica's initialization.
    """
    
    # Hook check_improvements into respond method
    original_respond = agent_loop.respond

    def respond_with_improvements(text: str, user: str = "default", stream: bool = False, **kwargs):
        # Check for improvements to propose
        improvement = api.check_improvements()
        if improvement:
            logger.info(f"Proposing improvements: {improvement}")
            # Could insert improvement notifications here

        # Continue with normal response
        return original_respond(text, user, stream, **kwargs)

    agent_loop.respond = respond_with_improvements

    # Start auto-improvement scheduler
    api.start_auto_improvements(interval_hours=1)

    logger.info("Self-upgrade system integrated with agent loop")


def integrate_with_skill_loader(skill_loader, api: SelfUpgradeAPI):
    """
    Example: Register self-upgrade skill with skill loader.
    
    Call this during skill initialization.
    """
    skill_loader.register_skill(
        name='improvement_request',
        skill=api.request_skill,
        keywords=['improve', 'upgrade', 'enhance', 'optimize']
    )

    logger.info("Improvement request skill registered")


# ========== Quick Start ==========

def quick_start():
    """
    Quick start example for using the self-upgrade API.
    """
    # Initialize API
    api = SelfUpgradeAPI()

    # Example 1: User requests improvement
    print("\\n=== User Request ===")
    result = api.request_improvement("Improve greeting_skill to add emoji support")
    print(f"Proposal: {result['proposal_id']}")
    print(f"Status: {result['status']}")

    # Example 2: Check pending improvements
    print("\\n=== Pending Improvements ===")
    pending = api.list_pending()
    print(f"Pending: {pending}")

    # Example 3: Get statistics
    print("\\n=== Statistics ===")
    stats = api.get_statistics()
    print(f"Total actions: {stats['total_actions']}")

    # Example 4: Start auto improvements
    print("\\n=== Auto Improvements ===")
    api.start_auto_improvements(interval_hours=1)
    print("Auto improvement scheduler started")

    # Example 5: Generate dashboard
    print("\\n=== Dashboard ===")
    dashboard_path = api.save_dashboard()
    print(f"Dashboard saved to: {dashboard_path}")

    # Example 6: Get status report
    print("\\n=== Status Report ===")
    print(api.get_status_report())

    return api


if __name__ == '__main__':
    # Run quick start example
    api = quick_start()
