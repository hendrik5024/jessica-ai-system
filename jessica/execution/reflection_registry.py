"""
Phase 7.3: Reflective Intelligence Layer — Reflection Registry

This module provides append-only storage for ReflectionRecords.

The registry is:
- Append-only (add only, never modify/delete)
- Immutable (all records frozen)
- Chronological (order preserved)
- Queryable (by source_id, source_type, etc.)

CRITICAL CONSTRAINTS:
- NO deletion
- NO modification
- NO learning or adaptation
- NO execution capability
- NO decision influence
"""

from typing import List, Dict, Optional
from datetime import datetime
from jessica.execution.reflection_record import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
)


class ReflectionRegistry:
    """
    Append-only storage for ReflectionRecords.
    
    This registry maintains a complete, immutable history of all reflections.
    Records can be added but NEVER modified or deleted.
    
    All reflections are stored in chronological order and can be queried by:
    - Source ID (proposal_id or execution_id)
    - Source type (PROPOSAL or EXECUTION)
    - Confidence level
    
    These records do NOT influence decisions or trigger actions - they exist
    purely for human understanding and system transparency.
    
    Example:
        >>> registry = ReflectionRegistry()
        >>> 
        >>> # Add reflection
        >>> error = registry.add_reflection(reflection)
        >>> 
        >>> # Query by source
        >>> reflections = registry.get_reflections_by_source_id("exec_123")
        >>> 
        >>> # Get all reflections
        >>> all_reflections = registry.get_all_reflections()
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize ReflectionRegistry.
        
        Args:
            enabled: Whether registry is enabled (default True)
        """
        self.enabled = enabled
        self._reflections: List[ReflectionRecord] = []
        self._index_by_source_id: Dict[str, List[ReflectionRecord]] = {}
        self._index_by_reflection_id: Dict[str, ReflectionRecord] = {}
    
    def add_reflection(
        self,
        reflection: ReflectionRecord,
    ) -> Optional[str]:
        """
        Add a reflection to the registry (append-only).
        
        Once added, reflections can NEVER be modified or deleted.
        
        Args:
            reflection: ReflectionRecord to add
        
        Returns:
            None on success, error message on failure
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> reflection = create_reflection_record(...)
            >>> error = registry.add_reflection(reflection)
            >>> if error:
            ...     print(f"Failed: {error}")
        """
        if not self.enabled:
            return "ReflectionRegistry is disabled"
        
        if not reflection:
            return "Reflection is required"
        
        # Check for duplicate reflection_id
        if reflection.reflection_id in self._index_by_reflection_id:
            return f"Reflection {reflection.reflection_id} already exists"
        
        # Append to main list (chronological order)
        self._reflections.append(reflection)
        
        # Index by source_id
        source_id = reflection.source_id
        if source_id not in self._index_by_source_id:
            self._index_by_source_id[source_id] = []
        self._index_by_source_id[source_id].append(reflection)
        
        # Index by reflection_id
        self._index_by_reflection_id[reflection.reflection_id] = reflection
        
        return None
    
    def get_reflection_by_id(
        self,
        reflection_id: str,
    ) -> Optional[ReflectionRecord]:
        """
        Get a reflection by its reflection_id (read-only).
        
        Args:
            reflection_id: ID of reflection to retrieve
        
        Returns:
            ReflectionRecord if found, None otherwise
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> reflection = registry.get_reflection_by_id("refl_123")
            >>> if reflection:
            ...     print(reflection.summary)
        """
        if not self.enabled:
            return None
        
        return self._index_by_reflection_id.get(reflection_id)
    
    def get_reflections_by_source_id(
        self,
        source_id: str,
    ) -> List[ReflectionRecord]:
        """
        Get all reflections for a specific source (read-only).
        
        Args:
            source_id: Source ID (proposal_id or execution_id)
        
        Returns:
            List of reflections for that source (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> reflections = registry.get_reflections_by_source_id("exec_123")
            >>> for reflection in reflections:
            ...     print(reflection.summary)
        """
        if not self.enabled:
            return []
        
        return self._index_by_source_id.get(source_id, [])
    
    def get_reflections_by_source_type(
        self,
        source_type: SourceType,
    ) -> List[ReflectionRecord]:
        """
        Get all reflections for a specific source type (read-only).
        
        Args:
            source_type: SourceType (PROPOSAL or EXECUTION)
        
        Returns:
            List of reflections for that type (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> executions = registry.get_reflections_by_source_type(
            ...     SourceType.EXECUTION
            ... )
        """
        if not self.enabled:
            return []
        
        return [
            r for r in self._reflections
            if r.source_type == source_type
        ]
    
    def get_reflections_by_confidence(
        self,
        confidence_level: ConfidenceLevel,
    ) -> List[ReflectionRecord]:
        """
        Get all reflections with specific confidence level (read-only).
        
        Args:
            confidence_level: ConfidenceLevel (LOW/MEDIUM/HIGH)
        
        Returns:
            List of reflections with that confidence (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> high_confidence = registry.get_reflections_by_confidence(
            ...     ConfidenceLevel.HIGH
            ... )
        """
        if not self.enabled:
            return []
        
        return [
            r for r in self._reflections
            if r.confidence_level == confidence_level
        ]
    
    def get_reflections_with_risks(self) -> List[ReflectionRecord]:
        """
        Get all reflections that have identified risks (read-only).
        
        Returns:
            List of reflections with risks (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> risky = registry.get_reflections_with_risks()
            >>> for reflection in risky:
            ...     print(f"{reflection.source_id}: {len(reflection.identified_risks)} risks")
        """
        if not self.enabled:
            return []
        
        return [
            r for r in self._reflections
            if r.has_risks()
        ]
    
    def get_reflections_with_anomalies(self) -> List[ReflectionRecord]:
        """
        Get all reflections that have detected anomalies (read-only).
        
        Returns:
            List of reflections with anomalies (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> anomalous = registry.get_reflections_with_anomalies()
            >>> for reflection in anomalous:
            ...     print(f"{reflection.source_id}: {reflection.anomalies}")
        """
        if not self.enabled:
            return []
        
        return [
            r for r in self._reflections
            if r.has_anomalies()
        ]
    
    def get_all_reflections(self) -> List[ReflectionRecord]:
        """
        Get all reflections in chronological order (read-only).
        
        Returns:
            List of all reflections (chronological order)
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> all_reflections = registry.get_all_reflections()
            >>> print(f"Total: {len(all_reflections)}")
        """
        if not self.enabled:
            return []
        
        # Return copy to prevent external modification
        return list(self._reflections)
    
    def count_reflections(self) -> int:
        """
        Count total reflections in registry (read-only).
        
        Returns:
            Total number of reflections
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> count = registry.count_reflections()
            >>> print(f"Total reflections: {count}")
        """
        if not self.enabled:
            return 0
        
        return len(self._reflections)
    
    def count_by_source_type(self) -> Dict[str, int]:
        """
        Count reflections by source type (read-only).
        
        Returns:
            Dictionary mapping source type to count
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> counts = registry.count_by_source_type()
            >>> print(f"Executions: {counts.get('execution', 0)}")
        """
        if not self.enabled:
            return {}
        
        counts = {}
        for reflection in self._reflections:
            source_type = reflection.source_type.value
            counts[source_type] = counts.get(source_type, 0) + 1
        
        return counts
    
    def count_by_confidence(self) -> Dict[str, int]:
        """
        Count reflections by confidence level (read-only).
        
        Returns:
            Dictionary mapping confidence level to count
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> counts = registry.count_by_confidence()
            >>> print(f"High confidence: {counts.get('high', 0)}")
        """
        if not self.enabled:
            return {}
        
        counts = {}
        for reflection in self._reflections:
            confidence = reflection.confidence_level.value
            counts[confidence] = counts.get(confidence, 0) + 1
        
        return counts
    
    def has_reflection_for_source(self, source_id: str) -> bool:
        """
        Check if any reflections exist for a source (read-only).
        
        Args:
            source_id: Source ID to check
        
        Returns:
            True if reflections exist, False otherwise
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> if registry.has_reflection_for_source("exec_123"):
            ...     print("Reflections exist")
        """
        if not self.enabled:
            return False
        
        return source_id in self._index_by_source_id
    
    def get_registry_stats(self) -> Dict[str, any]:
        """
        Get comprehensive registry statistics (read-only).
        
        Returns:
            Dictionary with stats:
            - total_reflections: total count
            - by_source_type: counts by type
            - by_confidence: counts by confidence
            - with_risks: count with risks
            - with_anomalies: count with anomalies
            - total_risks: sum of all risks
            - total_anomalies: sum of all anomalies
        
        Example:
            >>> registry = ReflectionRegistry()
            >>> stats = registry.get_registry_stats()
            >>> print(f"Total: {stats['total_reflections']}")
            >>> print(f"With risks: {stats['with_risks']}")
        """
        if not self.enabled:
            return {}
        
        total_reflections = len(self._reflections)
        by_source_type = self.count_by_source_type()
        by_confidence = self.count_by_confidence()
        
        with_risks = sum(1 for r in self._reflections if r.has_risks())
        with_anomalies = sum(1 for r in self._reflections if r.has_anomalies())
        
        total_risks = sum(r.risk_count() for r in self._reflections)
        total_anomalies = sum(r.anomaly_count() for r in self._reflections)
        
        return {
            'total_reflections': total_reflections,
            'by_source_type': by_source_type,
            'by_confidence': by_confidence,
            'with_risks': with_risks,
            'with_anomalies': with_anomalies,
            'total_risks': total_risks,
            'total_anomalies': total_anomalies,
        }
    
    # ==================== Safety Switches ====================
    
    def disable(self):
        """Disable reflection registry (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable reflection registry (reversible)."""
        self.enabled = True
