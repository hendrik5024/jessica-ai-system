"""
Phase 7.3: Reflective Intelligence Layer — Reflection Analyzer

This module provides read-only analysis helpers for ReflectionRecords.

The analyzer is:
- Read-only (never modifies data)
- Advisory-only (outputs for human consumption)
- Stateless (no learning, no memory)
- Deterministic (same input → same output)

CRITICAL CONSTRAINTS:
- NO execution capability
- NO decision influence
- NO learning or adaptation
- NO state mutation
- NO feedback loops
"""

from typing import List, Dict, Optional, Tuple
from jessica.execution.reflection_record import (
    ReflectionRecord,
    SourceType,
    ConfidenceLevel,
)


class ReflectionAnalyzer:
    """
    Provides read-only analysis helpers for ReflectionRecords.
    
    This analyzer helps humans understand patterns, risks, and trends
    in reflections. It does NOT:
    - Modify behavior
    - Influence decisions
    - Trigger actions
    - Learn or adapt
    
    All methods are:
    - Read-only (no state changes)
    - Deterministic (same input → same output)
    - Advisory-only (human-consumable)
    
    Example:
        >>> analyzer = ReflectionAnalyzer()
        >>> 
        >>> # Analyze single reflection
        >>> summary = analyzer.analyze_single_reflection(reflection)
        >>> print(summary['risk_level'])
        'low'
        >>> 
        >>> # Aggregate multiple reflections
        >>> stats = analyzer.aggregate_reflections([r1, r2, r3])
        >>> print(stats['total_risks'])
        5
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize ReflectionAnalyzer.
        
        Args:
            enabled: Whether analyzer is enabled (default True)
        """
        self.enabled = enabled
    
    def analyze_single_reflection(
        self,
        reflection: ReflectionRecord,
    ) -> Dict[str, any]:
        """
        Analyze a single reflection and produce human-readable summary.
        
        This is read-only and deterministic.
        
        Args:
            reflection: ReflectionRecord to analyze
        
        Returns:
            Dictionary with analysis results:
            - risk_level: 'low', 'medium', 'high'
            - anomaly_level: 'none', 'low', 'medium', 'high'
            - confidence: confidence level value
            - source_type: source type value
            - has_issues: boolean indicating risks or anomalies
            - issue_count: total risks + anomalies
            - summary: human-readable summary
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> analysis = analyzer.analyze_single_reflection(reflection)
            >>> if analysis['has_issues']:
            ...     print(f"Issues found: {analysis['issue_count']}")
        """
        if not self.enabled:
            return {}
        
        if not reflection:
            return {}
        
        # Determine risk level
        risk_count = reflection.risk_count()
        if risk_count >= 3:
            risk_level = 'high'
        elif risk_count >= 1:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Determine anomaly level
        anomaly_count = reflection.anomaly_count()
        if anomaly_count >= 3:
            anomaly_level = 'high'
        elif anomaly_count >= 2:
            anomaly_level = 'medium'
        elif anomaly_count >= 1:
            anomaly_level = 'low'
        else:
            anomaly_level = 'none'
        
        # Calculate issue count
        issue_count = risk_count + anomaly_count
        has_issues = issue_count > 0
        
        # Generate summary
        summary_parts = [f"Reflection on {reflection.source_type.value}"]
        if has_issues:
            summary_parts.append(f"{issue_count} issue(s) identified")
        else:
            summary_parts.append("no issues")
        summary_parts.append(f"confidence: {reflection.confidence_level.value}")
        
        return {
            'risk_level': risk_level,
            'anomaly_level': anomaly_level,
            'confidence': reflection.confidence_level.value,
            'source_type': reflection.source_type.value,
            'has_issues': has_issues,
            'issue_count': issue_count,
            'risk_count': risk_count,
            'anomaly_count': anomaly_count,
            'summary': ', '.join(summary_parts),
        }
    
    def aggregate_reflections(
        self,
        reflections: List[ReflectionRecord],
    ) -> Dict[str, any]:
        """
        Aggregate statistics across multiple reflections.
        
        This is read-only and deterministic.
        
        Args:
            reflections: List of ReflectionRecords to aggregate
        
        Returns:
            Dictionary with aggregate statistics:
            - total_reflections: count of reflections
            - total_risks: sum of all risks
            - total_anomalies: sum of all anomalies
            - by_source_type: counts by source type
            - by_confidence: counts by confidence level
            - high_risk_count: reflections with 3+ risks
            - has_anomalies_count: reflections with anomalies
            - average_risk_per_reflection: float
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> stats = analyzer.aggregate_reflections([r1, r2, r3])
            >>> print(f"Total risks: {stats['total_risks']}")
            >>> print(f"Average: {stats['average_risk_per_reflection']:.2f}")
        """
        if not self.enabled:
            return {}
        
        if not reflections:
            return {
                'total_reflections': 0,
                'total_risks': 0,
                'total_anomalies': 0,
                'by_source_type': {},
                'by_confidence': {},
                'high_risk_count': 0,
                'has_anomalies_count': 0,
                'average_risk_per_reflection': 0.0,
            }
        
        # Count totals
        total_reflections = len(reflections)
        total_risks = sum(r.risk_count() for r in reflections)
        total_anomalies = sum(r.anomaly_count() for r in reflections)
        
        # Count by source type
        by_source_type = {}
        for reflection in reflections:
            source_key = reflection.source_type.value
            by_source_type[source_key] = by_source_type.get(source_key, 0) + 1
        
        # Count by confidence level
        by_confidence = {}
        for reflection in reflections:
            confidence_key = reflection.confidence_level.value
            by_confidence[confidence_key] = by_confidence.get(confidence_key, 0) + 1
        
        # Count high-risk reflections (3+ risks)
        high_risk_count = sum(1 for r in reflections if r.risk_count() >= 3)
        
        # Count reflections with anomalies
        has_anomalies_count = sum(1 for r in reflections if r.has_anomalies())
        
        # Calculate average
        average_risk_per_reflection = total_risks / total_reflections if total_reflections > 0 else 0.0
        
        return {
            'total_reflections': total_reflections,
            'total_risks': total_risks,
            'total_anomalies': total_anomalies,
            'by_source_type': by_source_type,
            'by_confidence': by_confidence,
            'high_risk_count': high_risk_count,
            'has_anomalies_count': has_anomalies_count,
            'average_risk_per_reflection': average_risk_per_reflection,
        }
    
    def filter_by_source_type(
        self,
        reflections: List[ReflectionRecord],
        source_type: SourceType,
    ) -> List[ReflectionRecord]:
        """
        Filter reflections by source type (read-only).
        
        Args:
            reflections: List of reflections
            source_type: SourceType to filter by
        
        Returns:
            Filtered list of reflections (new list, not original)
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> executions = analyzer.filter_by_source_type(
            ...     all_reflections,
            ...     SourceType.EXECUTION
            ... )
        """
        if not self.enabled:
            return []
        
        if not reflections:
            return []
        
        return [r for r in reflections if r.source_type == source_type]
    
    def filter_by_confidence(
        self,
        reflections: List[ReflectionRecord],
        confidence_level: ConfidenceLevel,
    ) -> List[ReflectionRecord]:
        """
        Filter reflections by confidence level (read-only).
        
        Args:
            reflections: List of reflections
            confidence_level: ConfidenceLevel to filter by
        
        Returns:
            Filtered list of reflections (new list, not original)
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> high_confidence = analyzer.filter_by_confidence(
            ...     all_reflections,
            ...     ConfidenceLevel.HIGH
            ... )
        """
        if not self.enabled:
            return []
        
        if not reflections:
            return []
        
        return [r for r in reflections if r.confidence_level == confidence_level]
    
    def filter_with_risks(
        self,
        reflections: List[ReflectionRecord],
    ) -> List[ReflectionRecord]:
        """
        Filter to reflections that have risks (read-only).
        
        Args:
            reflections: List of reflections
        
        Returns:
            Reflections with one or more risks
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> risky = analyzer.filter_with_risks(all_reflections)
            >>> for reflection in risky:
            ...     print(reflection.identified_risks)
        """
        if not self.enabled:
            return []
        
        if not reflections:
            return []
        
        return [r for r in reflections if r.has_risks()]
    
    def filter_with_anomalies(
        self,
        reflections: List[ReflectionRecord],
    ) -> List[ReflectionRecord]:
        """
        Filter to reflections that have anomalies (read-only).
        
        Args:
            reflections: List of reflections
        
        Returns:
            Reflections with one or more anomalies
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> anomalous = analyzer.filter_with_anomalies(all_reflections)
            >>> for reflection in anomalous:
            ...     print(reflection.anomalies)
        """
        if not self.enabled:
            return []
        
        if not reflections:
            return []
        
        return [r for r in reflections if r.has_anomalies()]
    
    def sort_by_risk_count(
        self,
        reflections: List[ReflectionRecord],
        descending: bool = True,
    ) -> List[ReflectionRecord]:
        """
        Sort reflections by risk count (read-only).
        
        Args:
            reflections: List of reflections
            descending: If True, highest risk first (default)
        
        Returns:
            Sorted list of reflections (new list, not original)
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> sorted_reflections = analyzer.sort_by_risk_count(
            ...     all_reflections,
            ...     descending=True
            ... )
            >>> # Highest risk first
            >>> print(sorted_reflections[0].risk_count())
        """
        if not self.enabled:
            return []
        
        if not reflections:
            return []
        
        return sorted(
            reflections,
            key=lambda r: r.risk_count(),
            reverse=descending,
        )
    
    def get_risk_summary(
        self,
        reflections: List[ReflectionRecord],
    ) -> Dict[str, any]:
        """
        Get summary of all risks across reflections (read-only).
        
        Args:
            reflections: List of reflections
        
        Returns:
            Dictionary with risk summary:
            - total_risks: total count
            - unique_risks: set of unique risk messages
            - risk_frequency: dict mapping risk to count
            - most_common_risk: most frequent risk message
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> risk_summary = analyzer.get_risk_summary(reflections)
            >>> print(f"Most common: {risk_summary['most_common_risk']}")
        """
        if not self.enabled:
            return {}
        
        if not reflections:
            return {
                'total_risks': 0,
                'unique_risks': set(),
                'risk_frequency': {},
                'most_common_risk': None,
            }
        
        # Collect all risks
        all_risks = []
        for reflection in reflections:
            all_risks.extend(reflection.identified_risks)
        
        total_risks = len(all_risks)
        unique_risks = set(all_risks)
        
        # Count frequency
        risk_frequency = {}
        for risk in all_risks:
            risk_frequency[risk] = risk_frequency.get(risk, 0) + 1
        
        # Find most common
        most_common_risk = None
        if risk_frequency:
            most_common_risk = max(risk_frequency, key=risk_frequency.get)
        
        return {
            'total_risks': total_risks,
            'unique_risks': unique_risks,
            'risk_frequency': risk_frequency,
            'most_common_risk': most_common_risk,
        }
    
    def get_anomaly_summary(
        self,
        reflections: List[ReflectionRecord],
    ) -> Dict[str, any]:
        """
        Get summary of all anomalies across reflections (read-only).
        
        Args:
            reflections: List of reflections
        
        Returns:
            Dictionary with anomaly summary:
            - total_anomalies: total count
            - unique_anomalies: set of unique anomaly messages
            - anomaly_frequency: dict mapping anomaly to count
            - most_common_anomaly: most frequent anomaly message
        
        Example:
            >>> analyzer = ReflectionAnalyzer()
            >>> anomaly_summary = analyzer.get_anomaly_summary(reflections)
            >>> print(f"Total: {anomaly_summary['total_anomalies']}")
        """
        if not self.enabled:
            return {}
        
        if not reflections:
            return {
                'total_anomalies': 0,
                'unique_anomalies': set(),
                'anomaly_frequency': {},
                'most_common_anomaly': None,
            }
        
        # Collect all anomalies
        all_anomalies = []
        for reflection in reflections:
            all_anomalies.extend(reflection.anomalies)
        
        total_anomalies = len(all_anomalies)
        unique_anomalies = set(all_anomalies)
        
        # Count frequency
        anomaly_frequency = {}
        for anomaly in all_anomalies:
            anomaly_frequency[anomaly] = anomaly_frequency.get(anomaly, 0) + 1
        
        # Find most common
        most_common_anomaly = None
        if anomaly_frequency:
            most_common_anomaly = max(anomaly_frequency, key=anomaly_frequency.get)
        
        return {
            'total_anomalies': total_anomalies,
            'unique_anomalies': unique_anomalies,
            'anomaly_frequency': anomaly_frequency,
            'most_common_anomaly': most_common_anomaly,
        }
    
    # ==================== Safety Switches ====================
    
    def disable(self):
        """Disable reflection analyzer (global safety switch)."""
        self.enabled = False
    
    def enable(self):
        """Enable reflection analyzer (reversible)."""
        self.enabled = True
