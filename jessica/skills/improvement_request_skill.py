"""
Improvement Request Skill
Allows users to request specific improvements to Jessica's capabilities.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("jessica.skills.improvement_request_skill")


class ImprovementRequestSkill:
    """
    Skill for handling user requests to improve Jessica's capabilities.
    """

    def __init__(self, self_upgrade_manager=None):
        self.manager = self_upgrade_manager
        logger.info("ImprovementRequestSkill initialized")

    def handle_improvement_request(self, query: str) -> Dict[str, Any]:
        """
        Parse improvement request from user query.
        """
        if not self.manager:
            return {
                'status': 'error',
                'message': 'Self-upgrade manager not initialized'
            }

        # Extract module and improvement description
        improvement_info = self._parse_improvement_request(query)

        if not improvement_info:
            return {
                'status': 'error',
                'message': 'Could not parse improvement request. Try: "Improve [skill_name] by [description]"'
            }

        logger.info(f"User improvement request: {improvement_info}")

        # Request improvement through manager
        result = self.manager.request_improvement(
            target_module=improvement_info['module'],
            description=improvement_info['description'],
            approval_required=True
        )

        return result

    def get_improvement_status(self, proposal_id: str) -> Dict[str, Any]:
        """
        Get status of a specific improvement proposal.
        """
        if not self.manager:
            return {'status': 'error', 'message': 'Manager not initialized'}

        status = self.manager.orchestrator.get_deployment_status(proposal_id)
        history = self.manager.get_improvement_history()

        # Find matching entry
        for entry in history:
            if entry['details'].get('proposal_id') == proposal_id:
                return {
                    'proposal_id': proposal_id,
                    'status': status['status'],
                    'history': entry,
                }

        return {
            'proposal_id': proposal_id,
            'status': 'not_found',
        }

    def list_pending_improvements(self) -> Dict[str, Any]:
        """
        List all pending improvements awaiting approval.
        """
        if not self.manager:
            return {'status': 'error', 'message': 'Manager not initialized'}

        # Get staging statistics
        staging = self.manager.staging.get_statistics()

        pending = {
            'staged': staging['staged_count'],
            'testing': staging['testing_count'],
            'ready_for_deployment': staging['staged_count'] + staging['testing_count'],
            'total': staging['total_count'],
        }

        return pending

    def approve_improvement(self, proposal_id: str) -> Dict[str, Any]:
        """
        User approves an improvement for deployment.
        """
        if not self.manager:
            return {'status': 'error', 'message': 'Manager not initialized'}

        result = self.manager.approve_improvement(proposal_id)
        return result

    def reject_improvement(self, proposal_id: str) -> Dict[str, Any]:
        """
        User rejects an improvement.
        """
        if not self.manager:
            return {'status': 'error', 'message': 'Manager not initialized'}

        result = self.manager.reject_improvement(proposal_id)
        return result

    def view_improvement_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Show user's improvement history and statistics.
        """
        if not self.manager:
            return {'status': 'error', 'message': 'Manager not initialized'}

        history = self.manager.get_improvement_history(limit)
        stats = self.manager.get_improvement_statistics()

        return {
            'recent_actions': history,
            'statistics': stats,
            'status_report': self.manager.get_status_report(),
        }

    # ========== Private Methods ==========

    def _parse_improvement_request(self, query: str) -> Dict[str, str] | None:
        """
        Parse user query to extract module and improvement description.
        
        Expected formats:
        - "Improve [module] to [description]"
        - "Add [description] to [module]"
        - "Optimize [module] for [description]"
        """
        query_lower = query.lower()

        # Pattern: "improve X to Y" or "improve X by Y"
        if 'improve' in query_lower:
            parts = query.split('to' if ' to ' in query else ' by ')
            if len(parts) >= 2:
                module = parts[0].replace('improve', '').strip().replace('_skill', '') + '_skill'
                description = parts[1].strip()
                return {'module': module, 'description': description}

        # Pattern: "add X to Y"
        if 'add' in query_lower and ' to ' in query_lower:
            parts = query.split(' to ')
            if len(parts) == 2:
                description = parts[0].replace('add', '').strip()
                module = parts[1].strip().replace('_skill', '') + '_skill'
                return {'module': module, 'description': description}

        # Pattern: "optimize X for Y"
        if 'optimize' in query_lower and ' for ' in query_lower:
            parts = query.split(' for ')
            if len(parts) == 2:
                module = parts[0].replace('optimize', '').strip().replace('_skill', '') + '_skill'
                description = parts[1].strip()
                return {'module': module, 'description': description}

        return None
