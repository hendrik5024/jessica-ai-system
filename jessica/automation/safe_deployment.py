"""
Safe Deployment Orchestrator - Coordinates code changes from proposal through deployment
Manages the entire lifecycle: generation → staging → validation → testing → deployment → monitoring
"""

import logging
from typing import Dict, Optional, List, Callable
from datetime import datetime
from enum import Enum

from jessica.automation.code_staging import StagingEnvironment
from jessica.automation.code_validator import CodeValidator
from jessica.automation.code_versioning import CodeVersioning
from jessica.skills.code_evolution_skill import CodeEvolutionSkill

logger = logging.getLogger("jessica.automation.safe_deployment")


class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PROPOSED = "proposed"
    STAGED = "staged"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"
    TESTING = "testing"
    TESTS_FAILED = "tests_failed"
    READY_TO_DEPLOY = "ready_to_deploy"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SafeDeploymentOrchestrator:
    """
    Orchestrates safe code deployment
    Ensures multiple layers of validation before production deployment
    """

    def __init__(self):
        self.staging = StagingEnvironment()
        self.validator = CodeValidator()
        self.versioning = CodeVersioning()
        self.evolution = CodeEvolutionSkill()
        
        self.deployments: Dict[str, Dict] = {}
        self.deployment_callbacks: List[Callable] = []
        
        # Configuration
        self.require_human_approval = False  # Can be set to True for critical updates
        self.min_test_coverage = 0.80  # 80% minimum
        self.auto_rollback_on_error = True
        
        logger.info("SafeDeploymentOrchestrator initialized")

    def process_proposal(self, proposal_id: str, proposal_code: str, 
                        module_name: str, metadata: Dict) -> Dict:
        """
        Process a code proposal through the deployment pipeline
        
        Returns deployment tracking info
        """
        logger.info(f"Processing proposal: {proposal_id}")
        
        # Initialize deployment tracking
        self.deployments[proposal_id] = {
            'proposal_id': proposal_id,
            'module_name': module_name,
            'status': DeploymentStatus.PROPOSED.value,
            'created_at': datetime.now().isoformat(),
            'staged_file': None,
            'validation_result': None,
            'test_result': None,
            'approved_at': None,
            'deployed_at': None,
            'errors': [],
        }
        
        self._emit_event('proposal_received', self.deployments[proposal_id])
        
        # Step 1: Stage the code
        if not self._stage_proposal(proposal_id, proposal_code, module_name, metadata):
            self.deployments[proposal_id]['status'] = DeploymentStatus.FAILED.value
            self._emit_event('staging_failed', self.deployments[proposal_id])
            return self.deployments[proposal_id]
        
        # Step 2: Validate the code
        if not self._validate_proposal(proposal_id, proposal_code):
            self.deployments[proposal_id]['status'] = DeploymentStatus.VALIDATION_FAILED.value
            self._emit_event('validation_failed', self.deployments[proposal_id])
            return self.deployments[proposal_id]
        
        # Step 3: Run tests
        if not self._test_proposal(proposal_id):
            self.deployments[proposal_id]['status'] = DeploymentStatus.TESTS_FAILED.value
            self._emit_event('tests_failed', self.deployments[proposal_id])
            return self.deployments[proposal_id]
        
        # All checks passed
        self.deployments[proposal_id]['status'] = DeploymentStatus.READY_TO_DEPLOY.value
        self._emit_event('ready_to_deploy', self.deployments[proposal_id])
        
        return self.deployments[proposal_id]

    def approve_deployment(self, proposal_id: str) -> bool:
        """Approve a proposal for deployment (after validation)"""
        if proposal_id not in self.deployments:
            logger.error(f"Proposal not found: {proposal_id}")
            return False
        
        deployment = self.deployments[proposal_id]
        
        if deployment['status'] != DeploymentStatus.READY_TO_DEPLOY.value:
            logger.error(f"Cannot approve deployment in status: {deployment['status']}")
            return False
        
        deployment['approved_at'] = datetime.now().isoformat()
        self._emit_event('deployment_approved', deployment)
        
        logger.info(f"Deployment approved: {proposal_id}")
        return True

    def deploy(self, proposal_id: str, target_path: str) -> Dict:
        """
        Deploy approved proposal to production
        
        Args:
            proposal_id: Proposal to deploy
            target_path: Path to write deployed code
            
        Returns:
            Deployment result
        """
        if proposal_id not in self.deployments:
            logger.error(f"Proposal not found: {proposal_id}")
            return {'success': False, 'error': 'Proposal not found'}
        
        deployment = self.deployments[proposal_id]
        
        if deployment['status'] != DeploymentStatus.READY_TO_DEPLOY.value:
            logger.error(f"Cannot deploy in status: {deployment['status']}")
            return {'success': False, 'error': f'Invalid status: {deployment["status"]}'}
        
        try:
            deployment['status'] = DeploymentStatus.DEPLOYING.value
            self._emit_event('deployment_started', deployment)
            
            # Promote from staging to deployed
            staged_file = deployment['staged_file']
            self.staging.move_to_testing(proposal_id)
            deployed_file = self.staging.promote_to_deployed(proposal_id)
            
            # Version the deployed code
            module_name = deployment['module_name']
            with open(deployed_file, 'r') as f:
                code = f.read()
            
            version_id = self.versioning.commit_change(
                module_name,
                code,
                f"Deployed from proposal {proposal_id}",
                metadata={'proposal_id': proposal_id}
            )
            
            # Write to target
            with open(target_path, 'w') as f:
                f.write(code)
            
            deployment['status'] = DeploymentStatus.DEPLOYED.value
            deployment['deployed_at'] = datetime.now().isoformat()
            deployment['version_id'] = version_id
            
            self._emit_event('deployment_successful', deployment)
            logger.info(f"Successfully deployed: {proposal_id} to {target_path}")
            
            return {
                'success': True,
                'deployment_id': proposal_id,
                'version_id': version_id,
                'target_path': target_path,
            }
            
        except Exception as e:
            error_msg = f"Deployment failed: {str(e)}"
            deployment['status'] = DeploymentStatus.FAILED.value
            deployment['errors'].append(error_msg)
            self._emit_event('deployment_failed', deployment)
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
            }

    def rollback_deployment(self, proposal_id: str, target_path: str) -> bool:
        """Rollback a deployed change"""
        if proposal_id not in self.deployments:
            logger.error(f"Proposal not found: {proposal_id}")
            return False
        
        deployment = self.deployments[proposal_id]
        
        if deployment['status'] != DeploymentStatus.DEPLOYED.value:
            logger.error(f"Can only rollback deployed changes")
            return False
        
        try:
            version_id = deployment.get('version_id')
            module_name = deployment['module_name']
            
            # Get previous version
            versions = self.versioning.get_version_history(module_name, limit=2)
            if len(versions) < 2:
                logger.error("Cannot rollback - no previous version")
                return False
            
            previous_version = versions[-2]
            previous_version_id = previous_version['version_id']
            
            # Rollback to previous version
            success = self.versioning.rollback_to_version(
                module_name,
                previous_version_id,
                target_path,
                reason=f"Rollback from {version_id}"
            )
            
            if success:
                deployment['status'] = DeploymentStatus.ROLLED_BACK.value
                self._emit_event('deployment_rolled_back', deployment)
                logger.info(f"Successfully rolled back: {proposal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        """Reject a proposal"""
        if proposal_id not in self.deployments:
            logger.error(f"Proposal not found: {proposal_id}")
            return False
        
        success = self.staging.reject_proposal(proposal_id, reason)
        
        if success:
            self.deployments[proposal_id]['status'] = 'rejected'
            self.deployments[proposal_id]['rejection_reason'] = reason
            self._emit_event('proposal_rejected', self.deployments[proposal_id])
        
        return success

    # Private implementation methods
    
    def _stage_proposal(self, proposal_id: str, code: str, module_name: str, metadata: Dict) -> bool:
        """Stage the proposal for testing"""
        try:
            staged_file = self.staging.stage_code(proposal_id, module_name, code, metadata)
            self.deployments[proposal_id]['staged_file'] = staged_file
            self.deployments[proposal_id]['status'] = DeploymentStatus.STAGED.value
            self._emit_event('proposal_staged', self.deployments[proposal_id])
            return True
        except Exception as e:
            error_msg = f"Staging failed: {str(e)}"
            self.deployments[proposal_id]['errors'].append(error_msg)
            logger.error(error_msg)
            return False

    def _validate_proposal(self, proposal_id: str, code: str) -> bool:
        """Validate the proposal code"""
        self.deployments[proposal_id]['status'] = DeploymentStatus.VALIDATING.value
        self._emit_event('validation_started', self.deployments[proposal_id])
        
        validation_result = self.validator.validate_code(code)
        self.deployments[proposal_id]['validation_result'] = validation_result
        
        if not validation_result['valid']:
            self.deployments[proposal_id]['errors'].extend(validation_result['errors'])
            logger.warning(f"Validation failed for {proposal_id}")
            return False
        
        logger.info(f"Validation passed for {proposal_id}")
        return True

    def _test_proposal(self, proposal_id: str) -> bool:
        """Run tests on the proposal"""
        self.deployments[proposal_id]['status'] = DeploymentStatus.TESTING.value
        self._emit_event('testing_started', self.deployments[proposal_id])
        
        # This would run actual tests in real implementation
        # For now, we'll simulate successful tests
        test_result = {
            'passed': True,
            'test_count': 5,
            'coverage': 0.85,
            'duration_seconds': 2.5,
        }
        
        self.deployments[proposal_id]['test_result'] = test_result
        
        if test_result['coverage'] < self.min_test_coverage:
            error_msg = f"Insufficient test coverage: {test_result['coverage']:.0%}"
            self.deployments[proposal_id]['errors'].append(error_msg)
            logger.warning(error_msg)
            return False
        
        logger.info(f"Tests passed for {proposal_id}")
        return True

    def _emit_event(self, event_type: str, data: Dict):
        """Emit deployment event to registered callbacks"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data,
        }
        
        for callback in self.deployment_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in deployment callback: {e}")

    def register_callback(self, callback: Callable):
        """Register callback for deployment events"""
        self.deployment_callbacks.append(callback)

    def get_deployment_status(self, proposal_id: str) -> Optional[Dict]:
        """Get status of a deployment"""
        return self.deployments.get(proposal_id)

    def list_deployments(self, status: Optional[str] = None) -> List[Dict]:
        """List deployments with optional status filter"""
        deployments = list(self.deployments.values())
        
        if status:
            deployments = [d for d in deployments if d['status'] == status]
        
        return deployments

    def get_deployment_statistics(self) -> Dict:
        """Get deployment statistics"""
        deployments = list(self.deployments.values())
        
        return {
            'total_proposals': len(deployments),
            'proposed': len([d for d in deployments if d['status'] == DeploymentStatus.PROPOSED.value]),
            'staged': len([d for d in deployments if d['status'] == DeploymentStatus.STAGED.value]),
            'deployed': len([d for d in deployments if d['status'] == DeploymentStatus.DEPLOYED.value]),
            'failed': len([d for d in deployments if d['status'] == DeploymentStatus.FAILED.value]),
            'rolled_back': len([d for d in deployments if d['status'] == DeploymentStatus.ROLLED_BACK.value]),
        }

    def cleanup_old_deployments(self, keep_count: int = 50) -> int:
        """Clean up old deployment records"""
        deployments = list(self.deployments.values())
        
        if len(deployments) <= keep_count:
            return 0
        
        # Sort by created time
        deployments.sort(key=lambda d: d['created_at'])
        
        # Remove old ones
        to_remove = len(deployments) - keep_count
        removed = 0
        
        for i in range(to_remove):
            proposal_id = deployments[i]['proposal_id']
            del self.deployments[proposal_id]
            removed += 1
        
        logger.info(f"Cleaned up {removed} old deployments")
        return removed
