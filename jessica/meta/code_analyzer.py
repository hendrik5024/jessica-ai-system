"""
Code Analysis System - Analyze Jessica's codebase for optimization opportunities.

Identifies:
- Inefficient algorithms (O(n²) where O(n) possible)
- Redundant computations or memory allocations
- Opportunities for parallelization
- Cache misses and data structure inefficiencies
- Dead code or unused branches
"""

import ast
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path
from enum import Enum


class OptimizationCategory(Enum):
    """Types of optimizations identified."""
    ALGORITHM = "algorithm"          # Improve algorithmic complexity
    CACHING = "caching"              # Add caching layer
    PARALLELIZATION = "parallel"     # Run in parallel
    MEMORY = "memory"                # Reduce memory usage
    BATCH_PROCESSING = "batch"       # Batch operations
    VECTORIZATION = "vectorization"  # Use numpy/torch vectors
    PRECOMPUTATION = "precompute"    # Pre-compute invariants
    INDEXING = "indexing"            # Add index/lookup table


@dataclass
class CodeIssue:
    """A potential optimization issue found in code."""
    file_path: str
    line_number: int
    category: OptimizationCategory
    severity: float          # 0.0-1.0, where 1.0 is critical
    description: str
    suggested_fix: str
    code_snippet: str = ""
    estimated_speedup: float = 1.0  # Expected speed improvement (e.g., 2.0 = 2x faster)


@dataclass
class AnalysisReport:
    """Complete code analysis results."""
    timestamp: str
    files_analyzed: int
    issues_found: List[CodeIssue]
    top_priorities: List[CodeIssue]
    total_estimated_speedup: float  # Product of speedups


class CodeAnalyzer:
    """Analyze Jessica's codebase for optimization opportunities."""
    
    def __init__(self, jessica_root: str):
        """Initialize analyzer with path to jessica codebase."""
        self.jessica_root = jessica_root
        self.issues: List[CodeIssue] = []
        
        # Performance-critical files to analyze (in order of importance)
        self.critical_paths = [
            'jessica/agent_loop.py',
            'jessica/lmm/model_orchestrator.py',
            'jessica/memory/episodic_memory.py',
            'jessica/memory/semantic_memory.py',
            'jessica/memory/rag_memory.py',
            'jessica/meta/causal_world_models.py',
            'jessica/meta/autodidactic_loop.py',
        ]
    
    def analyze(self) -> AnalysisReport:
        """Analyze codebase for optimization opportunities."""
        from datetime import datetime
        
        self.issues.clear()
        
        # Analyze critical paths
        files_analyzed = 0
        for rel_path in self.critical_paths:
            full_path = os.path.join(self.jessica_root, rel_path)
            if os.path.exists(full_path):
                self._analyze_file(full_path, rel_path)
                files_analyzed += 1
        
        # Sort by severity * estimated speedup
        self.issues.sort(
            key=lambda x: x.severity * (x.estimated_speedup - 1.0), 
            reverse=True
        )
        
        # Calculate total speedup (geometric mean of improvements)
        total_speedup = 1.0
        for issue in self.issues[:5]:  # Top 5 issues
            total_speedup *= issue.estimated_speedup
        
        # Get top priorities
        top_priorities = self.issues[:5]
        
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            files_analyzed=files_analyzed,
            issues_found=self.issues,
            top_priorities=top_priorities,
            total_estimated_speedup=total_speedup,
        )
    
    def _analyze_file(self, file_path: str, rel_path: str):
        """Analyze a single file for optimization opportunities."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Run various analysis passes
            self._find_inefficient_loops(tree, lines, rel_path)
            self._find_missing_cache(tree, lines, rel_path)
            self._find_sequential_operations(tree, lines, rel_path)
            self._find_memory_inefficiencies(tree, lines, rel_path)
            
        except Exception as e:
            # Skip files with parse errors
            pass
    
    def _find_inefficient_loops(self, tree: ast.AST, lines: List[str], rel_path: str):
        """Find nested loops or inefficient iterations."""
        
        class LoopFinder(ast.NodeVisitor):
            def __init__(self, analyzer, lines, rel_path):
                self.analyzer = analyzer
                self.lines = lines
                self.rel_path = rel_path
                self.loop_depth = 0
                self.in_list_comp = False
            
            def visit_For(self, node):
                self.loop_depth += 1
                if self.loop_depth >= 3:
                    # Triple nested loops are often optimizable
                    code = self._get_code_snippet(node)
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.rel_path,
                        line_number=node.lineno,
                        category=OptimizationCategory.ALGORITHM,
                        severity=0.7,
                        description=f"Triple-nested loop detected (depth={self.loop_depth})",
                        suggested_fix="Consider using numpy/torch for vectorization or restructuring algorithm",
                        code_snippet=code,
                        estimated_speedup=5.0,
                    ))
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_ListComp(self, node):
                self.in_list_comp = True
                self.generic_visit(node)
                self.in_list_comp = False
            
            def _get_code_snippet(self, node):
                try:
                    return '\n'.join(self.lines[node.lineno-1:min(node.lineno+3, len(self.lines))])
                except:
                    return ""
        
        finder = LoopFinder(self, lines, rel_path)
        finder.visit(tree)
    
    def _find_missing_cache(self, tree: ast.AST, lines: List[str], rel_path: str):
        """Find repeated expensive operations that should be cached."""
        
        class CallFinder(ast.NodeVisitor):
            def __init__(self, analyzer, lines, rel_path):
                self.analyzer = analyzer
                self.lines = lines
                self.rel_path = rel_path
                self.calls = []
            
            def visit_Call(self, node):
                # Look for expensive operations that might be repeated
                if isinstance(node.func, ast.Attribute):
                    method = node.func.attr
                    
                    # Expensive operations that appear multiple times
                    expensive = ['embedding', 'search', 'query', 'infer', 'retrieve']
                    if any(exp in method.lower() for exp in expensive):
                        self.calls.append((node.lineno, method))
                
                self.generic_visit(node)
        
        finder = CallFinder(self, lines, rel_path)
        finder.visit(tree)
        
        # Group calls by method name to find repeats
        from collections import Counter
        call_counts = Counter(method for _, method in finder.calls)
        
        for method, count in call_counts.items():
            if count >= 2:
                for line_no, m in finder.calls:
                    if m == method:
                        code = '\n'.join(lines[line_no-1:min(line_no+2, len(lines))])
                        self.issues.append(CodeIssue(
                            file_path=rel_path,
                            line_number=line_no,
                            category=OptimizationCategory.CACHING,
                            severity=0.5,
                            description=f"Expensive operation '{method}' called {count} times (potential caching opportunity)",
                            suggested_fix=f"Add @cache decorator or memoization for '{method}' results",
                            code_snippet=code,
                            estimated_speedup=2.0,
                        ))
                        break
    
    def _find_sequential_operations(self, tree: ast.AST, lines: List[str], rel_path: str):
        """Find operations that could be parallelized."""
        
        class SequenceChecker(ast.NodeVisitor):
            def __init__(self, analyzer, lines, rel_path):
                self.analyzer = analyzer
                self.lines = lines
                self.rel_path = rel_path
            
            def visit_For(self, node):
                # Look for independent iterations
                code = '\n'.join(self.lines[node.lineno-1:min(node.lineno+5, len(self.lines))])
                
                # If loop contains multiple independent operations
                if 'append' in code or 'extend' in code:
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.rel_path,
                        line_number=node.lineno,
                        category=OptimizationCategory.PARALLELIZATION,
                        severity=0.4,
                        description="Loop with independent iterations detected",
                        suggested_fix="Use multiprocessing.Pool or concurrent.futures for parallel processing",
                        code_snippet=code,
                        estimated_speedup=4.0,  # Assume 4-core system
                    ))
                
                self.generic_visit(node)
        
        checker = SequenceChecker(self, lines, rel_path)
        checker.visit(tree)
    
    def _find_memory_inefficiencies(self, tree: ast.AST, lines: List[str], rel_path: str):
        """Find memory allocation inefficiencies."""
        
        code_text = '\n'.join(lines)
        
        # Pattern: building large list in loop then converting
        if 'append' in code_text and 'np.array' in code_text:
            for i, line in enumerate(lines):
                if 'append' in line.lower():
                    snippet = '\n'.join(lines[max(0, i-2):min(i+3, len(lines))])
                    self.issues.append(CodeIssue(
                        file_path=rel_path,
                        line_number=i+1,
                        category=OptimizationCategory.MEMORY,
                        severity=0.3,
                        description="Building list with append then converting to numpy array",
                        suggested_fix="Pre-allocate numpy array or use np.concatenate for better memory efficiency",
                        code_snippet=snippet,
                        estimated_speedup=1.5,
                    ))
                    break


def analyze_jessica(jessica_root: Optional[str] = None) -> AnalysisReport:
    """Run complete code analysis on Jessica codebase.

    If `jessica_root` is not provided, derive it from the repository base directory.
    """
    if jessica_root is None:
        from jessica.config.paths import get_base_dir
        jessica_root = os.path.join(get_base_dir(), "jessica")

    analyzer = CodeAnalyzer(jessica_root)
    return analyzer.analyze()


if __name__ == "__main__":
    report = analyze_jessica()
    
    print(f"Code Analysis Report")
    print(f"=" * 60)
    print(f"Files analyzed: {report.files_analyzed}")
    print(f"Issues found: {len(report.issues_found)}")
    print(f"Total estimated speedup: {report.total_estimated_speedup:.2f}x")
    print()
    
    print("Top Optimization Priorities:")
    print("-" * 60)
    for i, issue in enumerate(report.top_priorities, 1):
        print(f"\n{i}. {issue.category.value.upper()}")
        print(f"   File: {issue.file_path}:{issue.line_number}")
        print(f"   Severity: {issue.severity:.1%} | Speedup: {issue.estimated_speedup:.1f}x")
        print(f"   Issue: {issue.description}")
        print(f"   Fix: {issue.suggested_fix}")
