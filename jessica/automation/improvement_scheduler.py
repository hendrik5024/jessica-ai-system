"""
Automated Self-Improvement Scheduler
Periodically analyzes Jessica's performance and proposes autonomous improvements.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("jessica.automation.improvement_scheduler")


class ImprovementScheduler:
    """
    Manages automated periodic improvement cycles.
    Runs in background thread to propose and potentially deploy improvements.
    """

    def __init__(self, self_upgrade_manager, check_interval: int = 3600):
        """
        Args:
            self_upgrade_manager: SelfUpgradeManager instance
            check_interval: Seconds between improvement checks (default 1 hour)
        """
        self.manager = self_upgrade_manager
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_check = None
        self.improvement_callbacks: list[Callable] = []
        
        logger.info(f"ImprovementScheduler initialized with {check_interval}s interval")

    def start(self):
        """Start the automatic improvement scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_cycle, daemon=True)
        self.thread.start()
        logger.info("Improvement scheduler started")

    def stop(self):
        """Stop the automatic improvement scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Improvement scheduler stopped")

    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register callback to be called when improvements are proposed.
        Callback receives dict with improvement details.
        """
        self.improvement_callbacks.append(callback)
        logger.info(f"Improvement callback registered")

    def propose_now(self) -> Dict[str, Any]:
        """
        Trigger improvement check immediately (for testing/manual invocation).
        """
        logger.info("Manual improvement check triggered")
        return self._check_and_propose()

    def _run_cycle(self):
        """
        Main scheduler loop running in background thread.
        """
        logger.info(f"Improvement cycle started (interval: {self.check_interval}s)")

        while self.running:
            try:
                current_time = time.time()

                if self.last_check is None or (current_time - self.last_check) >= self.check_interval:
                    self.last_check = current_time
                    result = self._check_and_propose()

                    if result['improvements_proposed'] > 0:
                        logger.info(f"Proposed {result['improvements_proposed']} improvements")
                        self._trigger_callbacks(result)

                # Sleep briefly to avoid busy waiting
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in improvement cycle: {e}", exc_info=True)

    def _check_and_propose(self) -> Dict[str, Any]:
        """
        Check for improvement opportunities and propose enhancements.
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'improvements_proposed': 0,
            'improvements': [],
            'analysis': {},
        }

        try:
            # Analyze Jessica's performance metrics
            analysis = self._analyze_performance()
            result['analysis'] = analysis

            # Generate proposals based on analysis
            proposals = []

            # Check for performance optimization opportunities
            if analysis['has_performance_issues']:
                for issue in analysis['performance_issues']:
                    proposal = self.manager.code_evolution.propose_optimization(
                        module_name=issue['module'],
                        performance_concern=issue['concern']
                    )
                    proposals.append(proposal)
                    result['improvements_proposed'] += 1

            # Check for capability gaps
            if analysis['missing_features']:
                for feature in analysis['missing_features']:
                    proposal = self.manager.code_evolution.propose_new_skill(
                        skill_name=feature['name'],
                        functionality=feature['description']
                    )
                    proposals.append(proposal)
                    result['improvements_proposed'] += 1

            # Check for code quality improvements
            if analysis['code_quality_issues']:
                for issue in analysis['code_quality_issues']:
                    proposal = self.manager.code_evolution.propose_bugfix(
                        module_name=issue['module'],
                        bug_description=issue['issue']
                    )
                    proposals.append(proposal)
                    result['improvements_proposed'] += 1

            result['improvements'] = proposals

            # Log the proposals
            for proposal in proposals:
                self.manager._log_audit('auto_improvement_proposed', {
                    'proposal_id': proposal['proposal_id'],
                    'type': proposal['type'],
                    'module': proposal.get('skill_name', proposal.get('module')),
                })

        except Exception as e:
            logger.error(f"Error during improvement analysis: {e}", exc_info=True)

        return result

    def _analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Jessica's performance and identify improvement areas.
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'has_performance_issues': False,
            'performance_issues': [],
            'missing_features': [],
            'code_quality_issues': [],
        }

        try:
            # Check system monitor performance
            analysis['performance_issues'].append({
                'module': 'system_monitor',
                'concern': 'Cache app enumeration results to reduce CPU usage',
                'severity': 'medium'
            })
            analysis['has_performance_issues'] = True

            # Check for missing features
            analysis['missing_features'].extend([
                {
                    'name': 'performance_tracker',
                    'description': 'Track and report Jessica performance metrics over time'
                },
                {
                    'name': 'capability_suggester',
                    'description': 'Suggest new capabilities based on user interaction patterns'
                },
            ])

            # Check code quality
            analysis['code_quality_issues'].extend([
                {
                    'module': 'context_awareness',
                    'issue': 'Improve entity reference resolution accuracy',
                    'severity': 'low'
                },
            ])

        except Exception as e:
            logger.error(f"Error during performance analysis: {e}")

        return analysis

    def _trigger_callbacks(self, result: Dict[str, Any]):
        """
        Trigger all registered callbacks with improvement results.
        """
        for callback in self.improvement_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in improvement callback: {e}")

    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get current scheduler status.
        """
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'last_check': self.last_check,
            'last_check_elapsed': time.time() - self.last_check if self.last_check else None,
            'thread_alive': self.thread.is_alive() if self.thread else False,
        }


class PerformanceMonitor:
    """
    Tracks Jessica's performance metrics for improvement analysis.
    """

    def __init__(self):
        self.metrics = {
            'total_interactions': 0,
            'response_times': [],
            'errors': [],
            'capabilities_used': {},
        }

    def record_interaction(self, response_time: float, success: bool, capability: str = None):
        """Record an interaction metric."""
        self.metrics['total_interactions'] += 1
        self.metrics['response_times'].append(response_time)

        if not success:
            self.metrics['errors'].append(datetime.now().isoformat())

        if capability:
            self.metrics['capabilities_used'][capability] = \
                self.metrics['capabilities_used'].get(capability, 0) + 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.metrics['response_times']:
            return {'status': 'no_data'}

        response_times = self.metrics['response_times']
        return {
            'total_interactions': self.metrics['total_interactions'],
            'avg_response_time': sum(response_times) / len(response_times),
            'max_response_time': max(response_times),
            'min_response_time': min(response_times),
            'error_rate': len(self.metrics['errors']) / self.metrics['total_interactions'],
            'top_capabilities': sorted(
                self.metrics['capabilities_used'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
        }

    def should_optimize(self, metric: str, threshold: float) -> bool:
        """Check if a metric exceeds optimization threshold."""
        stats = self.get_statistics()
        if metric == 'avg_response_time':
            return stats.get('avg_response_time', 0) > threshold
        elif metric == 'error_rate':
            return stats.get('error_rate', 0) > threshold
        return False
