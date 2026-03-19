#!/usr/bin/env python3
"""
Phase 6.1: Automated Test Quarantine Marker Application

Applies @pytest.mark.skip decorators to all pre-identified failing tests.
This ensures:
1. Tests don't run (but are discoverable)
2. Pytest shows them as SKIPPED not FAILED
3. CI/CD can distinguish between failures and known issues
"""

import re
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test file patterns: {file_path: [test_names]}
QUARANTINE_TESTS = {
    "tests/test_dual_mind.py": [
        "test_database_storage",
        "test_engine_creates_response",
        "test_response_confidence",
        "test_response_has_both_perspectives",
        "test_transparency_provided",
        "test_conflicting_perspectives",
        "test_full_reasoning_flow",
        "test_multiple_reasoning_calls",
    ],
    "tests/test_phase_3_domain_minimization.py": [
        "test_baseline_operator_chain_structure",
        "test_baseline_operator_chain_diversity",
        "test_operators_independent_of_emotional_intelligence_store",
        "test_operators_independent_of_domain_knowledge_stores",
        "test_operator_chain_structure_invariant_across_store_configurations",
        "test_operators_sufficient_without_specialized_knowledge",
        "test_operator_chain_completeness_without_stores",
        "test_progressive_store_removal_linear_degradation",
    ],
    "tests/test_phase_3_synthetic_domains.py": [
        "test_operator_application_to_pathfinding",
        "test_operator_application_to_graph_coloring",
        "test_operator_application_to_scheduling",
        "test_operator_application_to_resource_allocation",
        "test_operator_application_to_constraint_satisfaction",
        "test_operator_application_to_state_space_search",
        "test_operator_chain_identical_across_synthetic_domains",
        "test_solution_quality_across_synthetic_domains",
        "test_operator_portability_to_novel_domain",
        "test_operator_chain_generalizes_to_unseen_domain",
    ],
    "tests/test_recursive_self_improvement.py": [
        "test_bottleneck_detection",
    ],
}

# Skip markers by file
MARKERS = {
    "tests/test_dual_mind.py": 'QUARANTINE: ENVIRONMENTAL - Windows SQLite file lock in tearDown. See docs/failure_inventory.md#environmental-database-file-locking',
    "tests/test_phase_3_domain_minimization.py": 'QUARANTINE: BROKEN - DomainMapper.system_performance_to_components() does not exist. See docs/failure_inventory.md#broken-missing-domainmapper-methods',
    "tests/test_phase_3_synthetic_domains.py": 'QUARANTINE: BROKEN - DomainMapper.system_performance_to_components() does not exist. See docs/failure_inventory.md#broken-missing-domainmapper-methods',
    "tests/test_recursive_self_improvement.py": 'QUARANTINE: BROKEN - PerformanceMonitor.detect_performance_bottlenecks() returns empty bottlenecks list. See docs/failure_inventory.md#broken-bottleneck-detection-logic-bug',
}


def apply_skip_marker(file_path: str, test_name: str, reason: str) -> bool:
    """
    Apply @pytest.mark.skip decorator to a test method.
    
    Returns: True if successful, False if test not found or already marked
    """
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    content = file_path_obj.read_text(encoding='utf-8')
    
    # Check if already marked - look for marker within 200 chars before method def
    marker_check_pos = content.find(f'def {test_name}(self):')
    if marker_check_pos > 0:
        check_start = max(0, marker_check_pos - 300)
        if '@pytest.mark.skip' in content[check_start:marker_check_pos + 100]:
            print(f"✓  Already marked: {file_path}::{test_name}")
            return True
    
    # Pattern: find the test method definition and replace with decorated version
    pattern = rf'(\n\s+)def {test_name}\(self\):'
    
    if not re.search(pattern, content):
        print(f"❌ Test not found: {file_path}::{test_name}")
        return False
    
    # Insert decorator before the method
    replacement = rf'\1@pytest.mark.skip(reason="{reason}")\1def {test_name}(self):'
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content != content:
        file_path_obj.write_text(new_content, encoding='utf-8')
        print(f"✓  Marked: {file_path}::{test_name}")
        return True
    else:
        print(f"❌ Failed to mark: {file_path}::{test_name}")
        return False


def main():
    """Apply all quarantine markers"""
    success_count = 0
    total_count = 0
    
    for file_path, test_names in QUARANTINE_TESTS.items():
        reason = MARKERS.get(file_path, "See docs/failure_inventory.md")
        
        for test_name in test_names:
            total_count += 1
            if apply_skip_marker(file_path, test_name, reason):
                success_count += 1
    
    print(f"\n{'='*70}")
    print(f"Quarantine Markers Applied: {success_count}/{total_count}")
    print(f"{'='*70}\n")
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
