"""
OperatorGraph: Compose multiple operators into a reasoning chain.

This class demonstrates that operators can be sequenced to solve complex problems,
and that the SAME operator graph structure applies across different domains.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import hashlib


@dataclass
class OperatorNode:
    """Single operator in the computation graph."""
    operator_name: str  # e.g., "DETECT_BOTTLENECK", "CONSTRAIN", "OPTIMIZE"
    inputs: Dict[str, Any]  # Domain-specific input values
    result: Any = None  # Output after execution
    domain_context: str = "unknown"


class OperatorGraph:
    """DAG of operators representing a complete reasoning process."""
    
    def __init__(self, problem: str, domain: str):
        self.problem = problem
        self.domain = domain
        self.nodes: List[OperatorNode] = []
        self.edges: List[Tuple[int, int]] = []  # (source_idx, target_idx)
        self.execution_log: List[str] = []
    
    def add_operator(self, operator_name: str, inputs: Dict[str, Any], 
                     domain_context: str = None) -> int:
        """Add operator node, return index."""
        node = OperatorNode(
            operator_name=operator_name,
            inputs=inputs,
            domain_context=domain_context or self.domain
        )
        self.nodes.append(node)
        return len(self.nodes) - 1
    
    def add_dependency(self, source_idx: int, target_idx: int):
        """Mark that target depends on source."""
        self.edges.append((source_idx, target_idx))
    
    def structural_hash(self) -> str:
        """
        Return hash of operator sequence (ignoring domain-specific input values).
        
        This is the CRITICAL test: if two operator graphs solving different domain
        problems have the same structural_hash(), they use identical reasoning structure.
        """
        operator_sequence = " → ".join(n.operator_name for n in self.nodes)
        return hashlib.md5(operator_sequence.encode()).hexdigest()
    
    def structure_string(self) -> str:
        """Human-readable operator sequence."""
        return " → ".join(n.operator_name for n in self.nodes)
    
    def to_dict(self) -> Dict:
        """Serialize for human review."""
        return {
            "problem": self.problem,
            "domain": self.domain,
            "operator_sequence": self.structure_string(),
            "structural_hash": self.structural_hash(),
            "nodes": [
                {
                    "index": i,
                    "operator": n.operator_name,
                    "inputs": {k: str(v) if not isinstance(v, (int, float, bool, str)) else v 
                               for k, v in n.inputs.items()},
                }
                for i, n in enumerate(self.nodes)
            ],
            "edges": self.edges,
        }
    
    def log(self, message: str):
        """Add to execution log."""
        self.execution_log.append(message)
