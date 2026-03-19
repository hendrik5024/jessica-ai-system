"""
Self-Upgrade Integration Module
Integrates the self-upgrade system into Jessica's agent loop and provides
user-facing skills for managing code improvements.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

from jessica.skills.code_evolution_skill import CodeEvolutionSkill
from jessica.automation.code_validator import CodeValidator
from jessica.automation.code_staging import StagingEnvironment
from jessica.automation.code_versioning import CodeVersioning
from jessica.automation.safe_deployment import SafeDeploymentOrchestrator

logger = logging.getLogger("jessica.self_upgrade_integration")


class SelfUpgradeManager:
    """
    Manages Jessica's self-upgrade capabilities and integrates with agent loop.
    Handles:
    - Autonomous improvement proposals
    - User-requested improvements
    - Automated improvement cycles
    - Audit logging and monitoring
    """

    def __init__(self):
        self.code_evolution = CodeEvolutionSkill()
        self.validator = CodeValidator()
        self.staging = StagingEnvironment()
        self.versioning = CodeVersioning()
        self.orchestrator = SafeDeploymentOrchestrator()
        
        self.improvement_history = []
        self.audit_log_path = Path("jessica/logs/self_upgrade_audit.json")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.last_analysis_time = None
        self.analysis_interval = 3600  # Check every hour
        
        logger.info("SelfUpgradeManager initialized")

    # ========== Agent Loop Integration ==========
    
    def check_for_improvements(self) -> Optional[Dict[str, Any]]:
        """
        Called periodically by agent loop to check if improvements should be proposed.
        Returns None if no improvements needed, or dict with improvement details.
        """
        import time
        
        current_time = time.time()
        if self.last_analysis_time is None or (current_time - self.last_analysis_time) < self.analysis_interval:
            return None
        
        self.last_analysis_time = current_time
        
        # Analyze performance metrics and propose improvements
        improvements = self._analyze_and_propose()
        
        if improvements:
            logger.info(f"Proposing {len(improvements)} improvements")
            return {
                'type': 'self_improvement_proposal',
                'improvements': improvements,
                'timestamp': datetime.now().isoformat()
            }
        
        return None

    def apply_pending_improvements(self) -> Dict[str, Any]:
        """
        Apply any improvements that are ready for deployment.
        Called during quieter periods in agent loop.
        """
        results = {
            'staged': 0,
            'validated': 0,
            'deployed': 0,
            'failed': 0,
        }
        
        # Get all proposals in staging
        stats = self.staging.get_statistics()
        
        if stats['staged_count'] > 0:
            logger.info(f"Applying {stats['staged_count']} staged improvements")
            results['staged'] = stats['staged_count']
            
            # Process each staged proposal
            # (In production, would implement actual pipeline progression)
        
        return results

    # ========== User-Requested Improvements ==========
    
    def request_improvement(self, target_module: str, description: str, 
                          approval_required: bool = True) -> Dict[str, Any]:
        """
        User requests an improvement to a specific module.
        
        Args:
            target_module: Module to improve (e.g., 'greeting_skill')
            description: Description of desired improvement
            approval_required: Whether to wait for user approval before deployment
            
        Returns:
            Proposal dict with status and details
        """
        logger.info(f"User requested improvement: {target_module} - {description}")
        
        # Generate improvement proposal
        proposal = self.code_evolution.propose_skill_improvement(
            skill_name=target_module,
            improvement_description=description
        )
        
        # Validate immediately
        result = self.validator.validate_code(proposal['code'])
        
        if not result['valid']:
            logger.warning(f"Generated code failed validation: {result['errors']}")
            return {
                'status': 'validation_failed',
                'proposal_id': proposal['proposal_id'],
                'errors': result['errors'],
            }
        
        # Stage the code
        staged_path = self.staging.stage_code(
            proposal_id=proposal['proposal_id'],
            module_name=target_module,
            code=proposal['code'],
            metadata={
                'type': 'user_requested',
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Process through orchestrator
        self.orchestrator.process_proposal(
            proposal_id=proposal['proposal_id'],
            proposal_code=proposal['code'],
            module_name=target_module,
            metadata={'user_requested': True}
        )
        
        status = self.orchestrator.get_deployment_status(proposal['proposal_id'])
        
        self._log_audit('improvement_proposed', {
            'proposal_id': proposal['proposal_id'],
            'module': target_module,
            'description': description,
            'status': status['status'],
            'requires_approval': approval_required
        })
        
        return {
            'status': 'proposed',
            'proposal_id': proposal['proposal_id'],
            'module': target_module,
            'staged_path': str(staged_path),
            'requires_approval': approval_required,
            'reasoning': proposal['reasoning'],
        }

    def approve_improvement(self, proposal_id: str, target_path: str = "jessica/_deployed.py") -> Dict[str, Any]:
        """
        Approve and deploy a proposed improvement.
        """
        logger.info(f"Approving improvement: {proposal_id}")
        
        self.orchestrator.approve_deployment(proposal_id)
        result = self.orchestrator.deploy(proposal_id, target_path)
        
        self._log_audit('improvement_deployed', {
            'proposal_id': proposal_id,
            'deployment_result': result,
        })
        
        return {
            'status': 'deployed',
            'proposal_id': proposal_id,
            'result': result,
        }

    def reject_improvement(self, proposal_id: str) -> Dict[str, Any]:
        """
        Reject a proposed improvement.
        """
        logger.info(f"Rejecting improvement: {proposal_id}")
        
        self.staging.reject_proposal(proposal_id)
        
        self._log_audit('improvement_rejected', {
            'proposal_id': proposal_id,
        })
        
        return {
            'status': 'rejected',
            'proposal_id': proposal_id,
        }

    # ========== Automated Improvement Cycles ==========
    
    def _analyze_and_propose(self) -> List[Dict[str, Any]]:
        """
        Analyze Jessica's performance and propose improvements.
        This is called periodically to identify optimization opportunities.
        """
        proposals = []
        
        # Check interaction patterns
        improvements = [
            {
                'skill': 'system_monitor',
                'description': 'Optimize app enumeration loop for better performance',
                'type': 'optimization'
            },
            {
                'skill': 'context_awareness',
                'description': 'Improve entity tracking accuracy with better heuristics',
                'type': 'improvement'
            },
            {
                'skill': 'greeting_skill',
                'description': 'Add multilingual greeting support',
                'type': 'improvement'
            },
        ]
        
        for improvement in improvements:
            proposal = self.code_evolution.propose_skill_improvement(
                skill_name=improvement['skill'],
                improvement_description=improvement['description']
            )
            proposals.append(proposal)
            logger.info(f"Proposed {improvement['type']}: {proposal['proposal_id']}")
        
        return proposals

    def setup_improvement_scheduler(self, interval_hours: int = 1):
        """
        Set up periodic improvement analysis cycle.
        """
        self.analysis_interval = interval_hours * 3600
        logger.info(f"Improvement scheduler configured: {interval_hours} hour interval")

    # ========== Monitoring and Audit Logging ==========
    
    def _log_audit(self, action: str, details: Dict[str, Any]):
        """
        Log all self-upgrade actions for audit trail.
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
        }
        
        self.improvement_history.append(audit_entry)
        
        # Persist to file
        try:
            existing = []
            if self.audit_log_path.exists():
                with open(self.audit_log_path, 'r') as f:
                    existing = json.load(f)
            
            existing.append(audit_entry)
            
            with open(self.audit_log_path, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_improvement_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent improvement history for monitoring.
        """
        return self.improvement_history[-limit:]

    def get_audit_log(self, action_filter: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve audit log with optional filtering.
        """
        try:
            if not self.audit_log_path.exists():
                return []
            
            with open(self.audit_log_path, 'r') as f:
                logs = json.load(f)
            
            if action_filter:
                logs = [log for log in logs if log.get('action') == action_filter]
            
            return logs[-limit:]
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            return []

    def get_improvement_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about self-upgrade activity.
        """
        audit_logs = self.get_audit_log(limit=1000)
        
        stats = {
            'total_actions': len(audit_logs),
            'by_action': {},
            'deployment_statistics': self.orchestrator.get_deployment_statistics(),
            'version_count': len(self.versioning.get_version_history('*') or []),
            'staging_status': self.staging.get_statistics(),
        }
        
        for log in audit_logs:
            action = log.get('action', 'unknown')
            stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
        
        return stats

    # ========== Status and Reporting ==========
    
    def get_status_report(self) -> str:
        """
        Generate human-readable status report for Jessica's self-upgrade system.
        """
        stats = self.get_improvement_statistics()
        
        report = f"""
JESSICA SELF-UPGRADE SYSTEM STATUS
{'='*50}

Total Self-Upgrade Actions: {stats['total_actions']}
Actions by Type: {json.dumps(stats['by_action'], indent=2)}

Deployment Statistics:
  - Total Proposals: {stats['deployment_statistics'].get('total_proposals', 0)}
  - Deployed: {stats['deployment_statistics'].get('deployed', 0)}
  - Failed: {stats['deployment_statistics'].get('failed', 0)}
  - Rolled Back: {stats['deployment_statistics'].get('rolled_back', 0)}

Staging Status:
  - Staged: {stats['staging_status']['staged_count']}
  - Testing: {stats['staging_status']['testing_count']}
  - Deployed: {stats['staging_status']['deployed_count']}
  - Rejected: {stats['staging_status']['rejected_count']}

Version History: {stats['version_count']} versions tracked

Recent History:
"""
        
        for entry in self.get_improvement_history(5):
            report += f"\n  [{entry['timestamp']}] {entry['action']}"
        
        return report
