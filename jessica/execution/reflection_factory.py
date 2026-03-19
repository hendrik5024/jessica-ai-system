"""
Phase 7.3: Reflective Intelligence Layer — Reflection Factory

This module provides the ReflectionFactory for creating ReflectionRecords from
completed proposals and executions.

The factory is:
- Deterministic (same input → same reflection)
- Stateless (no learning, no memory)
- Advisory-only (no execution, no influence)
- Read-only (never modifies inputs)

CRITICAL CONSTRAINTS:
- NO randomness
- NO state mutation
- NO learning
- NO execution capability
- NO decision influence
"""

from datetime import datetime
from typing import List, Optional, Tuple
from jessica.execution.reflection_record import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
    create_reflection_record,
)


class ReflectionFactory:
    """
    Factory for creating ReflectionRecords from proposals and executions.
    
    This factory is:
    - Deterministic: Same input always produces same reflection
    - Stateless: No learning or memory between calls
    - Advisory-only: Outputs are for human consumption only
    - Read-only: Never modifies input data
    
    The factory analyzes completed actions and produces human-readable
    reflections that identify risks, anomalies, and summarize outcomes.
    
    These reflections do NOT:
    - Influence future decisions
    - Trigger actions
    - Modify behavior
    - Learn or adapt
    
    Example:
        >>> factory = ReflectionFactory()
        >>> 
        >>> # Reflect on execution
        >>> execution_data = {
        ...     'execution_id': 'exec_123',
        ...     'action': 'send_email',
        ...     'status': 'success',
        ...     'parameters': {'to': 'user@example.com'}
        ... }
        >>> reflection, error = factory.reflect_on_execution(execution_data)
        >>> if not error:
        ...     print(reflection.summary)
        'Execution exec_123 completed with status: success'
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize ReflectionFactory.
        
        Args:
            enabled: Whether factory is enabled (default True)
        """
        self.enabled = enabled
    
    def reflect_on_execution(
        self,
        execution_data: dict,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Create a reflection on a completed execution.
        
        This is deterministic: same execution_data produces same reflection.
        
        Args:
            execution_data: Dictionary containing execution information
                Required keys:
                - execution_id (str): ID of execution
                - action (str): Action that was executed
                - status (str): Execution status
                Optional keys:
                - parameters (dict): Execution parameters
                - result (dict): Execution result
                - error (str): Error message if failed
        
        Returns:
            Tuple of (ReflectionRecord, None) on success
            Tuple of (None, error_message) on failure
        
        Example:
            >>> factory = ReflectionFactory()
            >>> data = {
            ...     'execution_id': 'exec_123',
            ...     'action': 'click_button',
            ...     'status': 'success',
            ... }
            >>> reflection, error = factory.reflect_on_execution(data)
            >>> reflection.source_type
            <SourceType.EXECUTION: 'execution'>
        """
        if not self.enabled:
            return None, "ReflectionFactory is disabled"
        
        # Validate required fields
        if not execution_data:
            return None, "execution_data is required"
        
        required_fields = ['execution_id', 'action', 'status']
        for field in required_fields:
            if field not in execution_data:
                return None, f"Missing required field: {field}"
        
        execution_id = execution_data['execution_id']
        action = execution_data['action']
        status = execution_data['status']
        parameters = execution_data.get('parameters', {})
        result = execution_data.get('result', {})
        error_msg = execution_data.get('error')
        
        # Generate deterministic summary
        summary = self._generate_execution_summary(
            execution_id, action, status, error_msg
        )
        
        # Identify risks (deterministic)
        risks = self._identify_execution_risks(
            action, status, parameters, error_msg
        )
        
        # Detect anomalies (deterministic)
        anomalies = self._detect_execution_anomalies(
            action, status, result, error_msg
        )
        
        # Determine confidence level (deterministic)
        confidence = self._determine_confidence(status, risks, anomalies)
        
        # Generate notes (deterministic)
        notes = self._generate_execution_notes(
            action, status, parameters, error_msg
        )
        
        # Create reflection record
        try:
            reflection = create_reflection_record(
                source_type=SourceType.EXECUTION,
                source_id=execution_id,
                summary=summary,
                identified_risks=risks,
                anomalies=anomalies,
                confidence_level=confidence,
                notes=notes,
            )
            return reflection, None
        except Exception as e:
            return None, f"Failed to create reflection: {str(e)}"
    
    def reflect_on_proposal(
        self,
        proposal_data: dict,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Create a reflection on a completed proposal.
        
        This is deterministic: same proposal_data produces same reflection.
        
        Args:
            proposal_data: Dictionary containing proposal information
                Required keys:
                - proposal_id (str): ID of proposal
                - requested_action (str): Action requested
                - approval_status (str): Status of approval
                Optional keys:
                - approved_actions (list): Actions approved
                - denial_reason (str): Reason if denied
                - risk_level (str): Risk level
        
        Returns:
            Tuple of (ReflectionRecord, None) on success
            Tuple of (None, error_message) on failure
        
        Example:
            >>> factory = ReflectionFactory()
            >>> data = {
            ...     'proposal_id': 'prop_123',
            ...     'requested_action': 'delete_file',
            ...     'approval_status': 'denied',
            ...     'denial_reason': 'High risk action',
            ... }
            >>> reflection, error = factory.reflect_on_proposal(data)
            >>> reflection.source_type
            <SourceType.PROPOSAL: 'proposal'>
        """
        if not self.enabled:
            return None, "ReflectionFactory is disabled"
        
        # Validate required fields
        if not proposal_data:
            return None, "proposal_data is required"
        
        required_fields = ['proposal_id', 'requested_action', 'approval_status']
        for field in required_fields:
            if field not in proposal_data:
                return None, f"Missing required field: {field}"
        
        proposal_id = proposal_data['proposal_id']
        requested_action = proposal_data['requested_action']
        approval_status = proposal_data['approval_status']
        approved_actions = proposal_data.get('approved_actions', [])
        denial_reason = proposal_data.get('denial_reason')
        risk_level = proposal_data.get('risk_level')
        
        # Generate deterministic summary
        summary = self._generate_proposal_summary(
            proposal_id, requested_action, approval_status, denial_reason
        )
        
        # Identify risks (deterministic)
        risks = self._identify_proposal_risks(
            requested_action, approval_status, risk_level, denial_reason
        )
        
        # Detect anomalies (deterministic)
        anomalies = self._detect_proposal_anomalies(
            requested_action, approval_status, approved_actions
        )
        
        # Determine confidence level (deterministic)
        confidence = self._determine_confidence(
            approval_status, risks, anomalies
        )
        
        # Generate notes (deterministic)
        notes = self._generate_proposal_notes(
            requested_action, approval_status, denial_reason
        )
        
        # Create reflection record
        try:
            reflection = create_reflection_record(
                source_type=SourceType.PROPOSAL,
                source_id=proposal_id,
                summary=summary,
                identified_risks=risks,
                anomalies=anomalies,
                confidence_level=confidence,
                notes=notes,
            )
            return reflection, None
        except Exception as e:
            return None, f"Failed to create reflection: {str(e)}"
    
    # ==================== Deterministic Helper Methods ====================
    
    def _generate_execution_summary(
        self,
        execution_id: str,
        action: str,
        status: str,
        error_msg: Optional[str],
    ) -> str:
        """Generate deterministic summary for execution."""
        if status.lower() in ['success', 'succeeded']:
            return f"Execution {execution_id} completed successfully: {action}"
        elif status.lower() in ['failed', 'error']:
            if error_msg:
                return f"Execution {execution_id} failed: {action} - {error_msg}"
            return f"Execution {execution_id} failed: {action}"
        elif status.lower() in ['rejected', 'denied']:
            return f"Execution {execution_id} was rejected: {action}"
        elif status.lower() == 'expired':
            return f"Execution {execution_id} expired before completion: {action}"
        else:
            return f"Execution {execution_id} completed with status '{status}': {action}"
    
    def _generate_proposal_summary(
        self,
        proposal_id: str,
        requested_action: str,
        approval_status: str,
        denial_reason: Optional[str],
    ) -> str:
        """Generate deterministic summary for proposal."""
        if approval_status.lower() == 'approved':
            return f"Proposal {proposal_id} was approved: {requested_action}"
        elif approval_status.lower() in ['denied', 'rejected']:
            if denial_reason:
                return f"Proposal {proposal_id} was denied: {requested_action} - {denial_reason}"
            return f"Proposal {proposal_id} was denied: {requested_action}"
        elif approval_status.lower() == 'pending':
            return f"Proposal {proposal_id} is pending approval: {requested_action}"
        else:
            return f"Proposal {proposal_id} has status '{approval_status}': {requested_action}"
    
    def _identify_execution_risks(
        self,
        action: str,
        status: str,
        parameters: dict,
        error_msg: Optional[str],
    ) -> List[str]:
        """Identify risks in execution (deterministic)."""
        risks = []
        
        # Risk: Failed execution
        if status.lower() in ['failed', 'error']:
            risks.append("Execution failed - may indicate system issue")
        
        # Risk: No parameters validation
        if not parameters:
            risks.append("No parameters provided - potential configuration issue")
        
        # Risk: Error messages indicate security issues
        if error_msg and any(keyword in error_msg.lower() for keyword in ['permission', 'access', 'unauthorized']):
            risks.append("Security-related error detected")
        
        # Risk: Dangerous action types
        if any(keyword in action.lower() for keyword in ['delete', 'remove', 'destroy', 'drop']):
            risks.append("Destructive action executed - verify intended behavior")
        
        return risks
    
    def _identify_proposal_risks(
        self,
        requested_action: str,
        approval_status: str,
        risk_level: Optional[str],
        denial_reason: Optional[str],
    ) -> List[str]:
        """Identify risks in proposal (deterministic)."""
        risks = []
        
        # Risk: Denied due to high risk
        if approval_status.lower() in ['denied', 'rejected'] and risk_level:
            if risk_level.lower() in ['high', 'critical']:
                risks.append(f"Proposal denied due to {risk_level} risk level")
        
        # Risk: Denial reason indicates security
        if denial_reason and any(keyword in denial_reason.lower() for keyword in ['security', 'unsafe', 'dangerous']):
            risks.append("Security concerns identified in proposal")
        
        # Risk: Dangerous action requested
        if any(keyword in requested_action.lower() for keyword in ['delete', 'remove', 'destroy', 'drop', 'erase']):
            risks.append("Destructive action requested")
        
        return risks
    
    def _detect_execution_anomalies(
        self,
        action: str,
        status: str,
        result: dict,
        error_msg: Optional[str],
    ) -> List[str]:
        """Detect anomalies in execution (deterministic)."""
        anomalies = []
        
        # Anomaly: Success but error message present
        if status.lower() == 'success' and error_msg:
            anomalies.append("Execution marked as success but error message present")
        
        # Anomaly: Failed but no error message
        if status.lower() in ['failed', 'error'] and not error_msg:
            anomalies.append("Execution failed but no error message provided")
        
        # Anomaly: Result indicates different status
        if result and 'status' in result:
            result_status = result['status']
            if result_status.lower() != status.lower():
                anomalies.append(f"Status mismatch: execution status '{status}' vs result status '{result_status}'")
        
        return anomalies
    
    def _detect_proposal_anomalies(
        self,
        requested_action: str,
        approval_status: str,
        approved_actions: List[str],
    ) -> List[str]:
        """Detect anomalies in proposal (deterministic)."""
        anomalies = []
        
        # Anomaly: Approved but no actions
        if approval_status.lower() == 'approved' and not approved_actions:
            anomalies.append("Proposal approved but no actions specified")
        
        # Anomaly: Denied but actions present
        if approval_status.lower() in ['denied', 'rejected'] and approved_actions:
            anomalies.append("Proposal denied but approved_actions list is not empty")
        
        return anomalies
    
    def _determine_confidence(
        self,
        status: str,
        risks: List[str],
        anomalies: List[str],
    ) -> ConfidenceLevel:
        """Determine confidence level (deterministic)."""
        # Low confidence if anomalies detected
        if len(anomalies) > 0:
            return ConfidenceLevel.LOW
        
        # Low confidence if multiple risks
        if len(risks) >= 3:
            return ConfidenceLevel.LOW
        
        # Medium confidence if some risks
        if len(risks) >= 1:
            return ConfidenceLevel.MEDIUM
        
        # High confidence if successful/approved with no issues
        if status.lower() in ['success', 'approved']:
            return ConfidenceLevel.HIGH
        
        # Medium confidence otherwise
        return ConfidenceLevel.MEDIUM
    
    def _generate_execution_notes(
        self,
        action: str,
        status: str,
        parameters: dict,
        error_msg: Optional[str],
    ) -> Optional[str]:
        """Generate notes for execution (deterministic)."""
        notes_parts = []
        
        if status.lower() in ['failed', 'error'] and error_msg:
            notes_parts.append(f"Error details: {error_msg}")
        
        if parameters and len(parameters) > 5:
            notes_parts.append("Large parameter set detected - review for complexity")
        
        if notes_parts:
            return " | ".join(notes_parts)
        
        return None
    
    def _generate_proposal_notes(
        self,
        requested_action: str,
        approval_status: str,
        denial_reason: Optional[str],
    ) -> Optional[str]:
        """Generate notes for proposal (deterministic)."""
        notes_parts = []
        
        if approval_status.lower() in ['denied', 'rejected'] and denial_reason:
            notes_parts.append(f"Denial reason: {denial_reason}")
        
        if notes_parts:
            return " | ".join(notes_parts)
        
        return None
    
    # ==================== Safety Switches ====================
    
    def disable(self):
        """Disable reflection factory (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable reflection factory (reversible)."""
        self.enabled = True
