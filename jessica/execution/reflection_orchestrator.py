"""
Phase 7.3: Reflective Intelligence Layer — Reflection Orchestrator

This module provides the single controlled entry point for reflection generation.

The orchestrator coordinates the complete reflection workflow:
1. Accept reflection request
2. Validate source exists (optional check)
3. Generate reflection via ReflectionFactory
4. Store reflection in ReflectionRegistry
5. Return reflection to human

CRITICAL CONSTRAINTS:
- NO automation (human-initiated only)
- NO background processing
- NO chaining (one request = one reflection)
- NO execution capability
- NO decision influence
- NO learning
"""

from typing import Optional, Tuple, Dict, List
from jessica.execution.reflection_record import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
)
from jessica.execution.reflection_factory import ReflectionFactory
from jessica.execution.reflection_registry import ReflectionRegistry


class ReflectionOrchestrator:
    """
    Single controlled entry point for reflection generation.
    
    This orchestrator coordinates the complete reflection workflow:
    - Factory creates reflections
    - Registry stores reflections
    - Human receives reflections
    
    All reflection is:
    - Human-initiated (NO automation)
    - One-time (NO background runs)
    - Non-chaining (one request = one reflection)
    - Advisory-only (NO influence on decisions)
    
    Example:
        >>> orchestrator = ReflectionOrchestrator()
        >>> 
        >>> # Reflect on execution
        >>> execution_data = {
        ...     'execution_id': 'exec_123',
        ...     'action': 'send_email',
        ...     'status': 'success',
        ... }
        >>> reflection, error = orchestrator.reflect_on_execution(execution_data)
        >>> if not error:
        ...     print(reflection.summary)
        'Execution exec_123 completed successfully: send_email'
    """
    
    def __init__(
        self,
        factory: Optional[ReflectionFactory] = None,
        registry: Optional[ReflectionRegistry] = None,
        enabled: bool = True,
    ):
        """
        Initialize ReflectionOrchestrator.
        
        Args:
            factory: ReflectionFactory instance (creates new if None)
            registry: ReflectionRegistry instance (creates new if None)
            enabled: Whether orchestrator is enabled (default True)
        """
        self.enabled = enabled
        self.factory = factory if factory else ReflectionFactory()
        self.registry = registry if registry else ReflectionRegistry()
    
    def reflect_on_execution(
        self,
        execution_data: dict,
        store_in_registry: bool = True,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Generate reflection on execution (single controlled entry point).
        
        Complete workflow:
        1. Validate orchestrator enabled
        2. Generate reflection via factory
        3. Store in registry (if requested)
        4. Return reflection to human
        
        Args:
            execution_data: Dictionary with execution information
                Required: execution_id, action, status
                Optional: parameters, result, error
            store_in_registry: Whether to store in registry (default True)
        
        Returns:
            Tuple of (ReflectionRecord, None) on success
            Tuple of (None, error_message) on failure
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> data = {
            ...     'execution_id': 'exec_123',
            ...     'action': 'click_button',
            ...     'status': 'success',
            ... }
            >>> reflection, error = orchestrator.reflect_on_execution(data)
            >>> if not error:
            ...     print(f"Reflection created: {reflection.reflection_id}")
        """
        if not self.enabled:
            return None, "ReflectionOrchestrator is disabled"
        
        # Step 1: Validate input
        if not execution_data:
            return None, "execution_data is required"
        
        # Step 2: Generate reflection via factory
        reflection, error = self.factory.reflect_on_execution(execution_data)
        if error:
            return None, f"Factory failed: {error}"
        
        if not reflection:
            return None, "Factory returned no reflection"
        
        # Step 3: Store in registry (if requested)
        if store_in_registry:
            registry_error = self.registry.add_reflection(reflection)
            if registry_error:
                # Reflection created but not stored - still return it
                # (Human can still see reflection even if storage failed)
                return reflection, f"Warning: Registry storage failed: {registry_error}"
        
        # Step 4: Return reflection to human
        return reflection, None
    
    def reflect_on_proposal(
        self,
        proposal_data: dict,
        store_in_registry: bool = True,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Generate reflection on proposal (single controlled entry point).
        
        Complete workflow:
        1. Validate orchestrator enabled
        2. Generate reflection via factory
        3. Store in registry (if requested)
        4. Return reflection to human
        
        Args:
            proposal_data: Dictionary with proposal information
                Required: proposal_id, requested_action, approval_status
                Optional: approved_actions, denial_reason, risk_level
            store_in_registry: Whether to store in registry (default True)
        
        Returns:
            Tuple of (ReflectionRecord, None) on success
            Tuple of (None, error_message) on failure
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> data = {
            ...     'proposal_id': 'prop_456',
            ...     'requested_action': 'delete_file',
            ...     'approval_status': 'denied',
            ...     'denial_reason': 'High risk',
            ... }
            >>> reflection, error = orchestrator.reflect_on_proposal(data)
            >>> if not error:
            ...     print(f"Risks: {reflection.identified_risks}")
        """
        if not self.enabled:
            return None, "ReflectionOrchestrator is disabled"
        
        # Step 1: Validate input
        if not proposal_data:
            return None, "proposal_data is required"
        
        # Step 2: Generate reflection via factory
        reflection, error = self.factory.reflect_on_proposal(proposal_data)
        if error:
            return None, f"Factory failed: {error}"
        
        if not reflection:
            return None, "Factory returned no reflection"
        
        # Step 3: Store in registry (if requested)
        if store_in_registry:
            registry_error = self.registry.add_reflection(reflection)
            if registry_error:
                # Reflection created but not stored - still return it
                return reflection, f"Warning: Registry storage failed: {registry_error}"
        
        # Step 4: Return reflection to human
        return reflection, None
    
    def get_reflection_by_id(
        self,
        reflection_id: str,
    ) -> Optional[ReflectionRecord]:
        """
        Retrieve reflection from registry by ID (read-only).
        
        Args:
            reflection_id: ID of reflection to retrieve
        
        Returns:
            ReflectionRecord if found, None otherwise
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> reflection = orchestrator.get_reflection_by_id("refl_123")
        """
        if not self.enabled:
            return None
        
        return self.registry.get_reflection_by_id(reflection_id)
    
    def get_reflections_for_source(
        self,
        source_id: str,
    ) -> List[ReflectionRecord]:
        """
        Get all reflections for a specific source (read-only).
        
        Args:
            source_id: Source ID (execution_id or proposal_id)
        
        Returns:
            List of reflections for that source
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> reflections = orchestrator.get_reflections_for_source("exec_123")
            >>> for reflection in reflections:
            ...     print(reflection.summary)
        """
        if not self.enabled:
            return []
        
        return self.registry.get_reflections_by_source_id(source_id)
    
    def has_reflection_for_source(
        self,
        source_id: str,
    ) -> bool:
        """
        Check if any reflections exist for a source (read-only).
        
        Args:
            source_id: Source ID to check
        
        Returns:
            True if reflections exist, False otherwise
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> if orchestrator.has_reflection_for_source("exec_123"):
            ...     print("Reflections exist")
        """
        if not self.enabled:
            return False
        
        return self.registry.has_reflection_for_source(source_id)
    
    def get_all_reflections(self) -> List[ReflectionRecord]:
        """
        Get all reflections from registry (read-only).
        
        Returns:
            List of all reflections in chronological order
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> all_reflections = orchestrator.get_all_reflections()
            >>> print(f"Total: {len(all_reflections)}")
        """
        if not self.enabled:
            return []
        
        return self.registry.get_all_reflections()
    
    def get_reflections_by_type(
        self,
        source_type: SourceType,
    ) -> List[ReflectionRecord]:
        """
        Get reflections filtered by source type (read-only).
        
        Args:
            source_type: SourceType (PROPOSAL or EXECUTION)
        
        Returns:
            List of reflections for that type
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> executions = orchestrator.get_reflections_by_type(
            ...     SourceType.EXECUTION
            ... )
        """
        if not self.enabled:
            return []
        
        return self.registry.get_reflections_by_source_type(source_type)
    
    def get_reflections_with_risks(self) -> List[ReflectionRecord]:
        """
        Get all reflections that have identified risks (read-only).
        
        Returns:
            List of reflections with risks
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> risky = orchestrator.get_reflections_with_risks()
            >>> for reflection in risky:
            ...     print(f"{reflection.source_id}: {reflection.identified_risks}")
        """
        if not self.enabled:
            return []
        
        return self.registry.get_reflections_with_risks()
    
    def get_reflections_with_anomalies(self) -> List[ReflectionRecord]:
        """
        Get all reflections that have detected anomalies (read-only).
        
        Returns:
            List of reflections with anomalies
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> anomalous = orchestrator.get_reflections_with_anomalies()
            >>> for reflection in anomalous:
            ...     print(f"{reflection.source_id}: {reflection.anomalies}")
        """
        if not self.enabled:
            return []
        
        return self.registry.get_reflections_with_anomalies()
    
    def get_reflection_stats(self) -> Dict[str, any]:
        """
        Get comprehensive statistics from registry (read-only).
        
        Returns:
            Dictionary with statistics:
            - total_reflections
            - by_source_type
            - by_confidence
            - with_risks
            - with_anomalies
            - total_risks
            - total_anomalies
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> stats = orchestrator.get_reflection_stats()
            >>> print(f"Total: {stats['total_reflections']}")
            >>> print(f"With risks: {stats['with_risks']}")
        """
        if not self.enabled:
            return {}
        
        return self.registry.get_registry_stats()
    
    def count_reflections(self) -> int:
        """
        Count total reflections in registry (read-only).
        
        Returns:
            Total number of reflections
        
        Example:
            >>> orchestrator = ReflectionOrchestrator()
            >>> count = orchestrator.count_reflections()
            >>> print(f"Total reflections: {count}")
        """
        if not self.enabled:
            return 0
        
        return self.registry.count_reflections()
    
    # ==================== Safety Switches ====================
    
    def disable(self):
        """Disable reflection orchestrator (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable reflection orchestrator (reversible)."""
        self.enabled = True
