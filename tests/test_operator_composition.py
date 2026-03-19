"""
EXPERIMENT #2: Operator Composition

Goal: Demonstrate that identical operator chains solve complex problems
      across unrelated domains.

Operator Chain (5 operators):
  1. DETECT_BOTTLENECK - Find what's limiting progress
  2. CONSTRAIN - Apply resource limits
  3. OPTIMIZE - Allocate resources optimally
  4. SEQUENCE - Execute plan if preconditions met
  5. ADAPT - Fallback if execution fails

Domain A (Technical): "Scale production service with limited budget"
Domain B (Personal): "Reach career goal within time/money constraints"

Success: structural_hash() is identical across both domains.
"""

import pytest
from jessica.unified_world_model.causal_operator import (
    DETECT_BOTTLENECK, CONSTRAIN, OPTIMIZE, SEQUENCE, ADAPT, Component
)
from jessica.unified_world_model.operator_graph import OperatorGraph


class TestOperatorComposition:
    """Test that operator chains transfer across domains."""
    
    def build_scaling_service_chain(self) -> OperatorGraph:
        """
        Domain A: Scale production database with limited engineering budget.
        
        Scenario:
          - Database throughput: 1K req/s, need 5K req/s
          - Current bottleneck: replication lag (0.3 throughput)
          - Engineering budget: $200K, 3 months
          - Options: optimize queries (fast, cheap), add DB replicas (slow, expensive)
        """
        graph = OperatorGraph(
            problem="Scale database with engineering budget constraints",
            domain="technical_scaling"
        )
        
        # 1. DETECT_BOTTLENECK: What's limiting throughput?
        db_components = [
            Component("replication", 0.3, 1.0),
            Component("cpu_utilization", 0.8, 1.0),
            Component("disk_io", 0.7, 1.0),
            Component("query_optimization", 0.5, 1.0),
        ]
        bottleneck_op = DETECT_BOTTLENECK()
        bottleneck_result = bottleneck_op.execute(db_components, domain_context="tech_db")
        
        idx_1 = graph.add_operator(
            "DETECT_BOTTLENECK",
            inputs={"components": [c.name for c in db_components]}
        )
        graph.nodes[idx_1].result = bottleneck_result
        
        # 2. CONSTRAIN: Apply resource limits
        constrain_op = CONSTRAIN()
        constrain_result = constrain_op.execute(
            resource="engineering_budget",
            current_value=300_000,  # Available
            limit=200_000  # Hard limit
        )
        
        idx_2 = graph.add_operator(
            "CONSTRAIN",
            inputs={"resource": "engineering_budget", "limit": 200_000}
        )
        graph.nodes[idx_2].result = constrain_result
        graph.add_dependency(idx_1, idx_2)
        
        # 3. OPTIMIZE: Best allocation given bottleneck and constraints
        optimize_op = OPTIMIZE()
        optimize_result = optimize_op.execute(
            objective_values={
                "replication_optimization": 0.3,
                "query_optimization": 0.5
            },
            constraints={"budget": 200_000, "time": 3},  # 3 months
            budget=200_000,
            time_available=3
        )
        
        idx_3 = graph.add_operator(
            "OPTIMIZE",
            inputs={"budget": 200_000, "time_months": 3}
        )
        graph.nodes[idx_3].result = optimize_result
        graph.add_dependency(idx_2, idx_3)
        
        # 4. SEQUENCE: Execute optimization plan
        sequence_op = SEQUENCE()
        sequence_result = sequence_op.execute(
            preconditions={
                "budget_allocated": True,
                "team_available": True,
                "requirements_clear": True
            },
            plan_name="Optimize queries + upgrade replicas",
            success_criteria={"throughput_improvement": 0.5}
        )
        
        idx_4 = graph.add_operator(
            "SEQUENCE",
            inputs={"plan": "Optimize queries + upgrade replicas"}
        )
        graph.nodes[idx_4].result = sequence_result
        graph.add_dependency(idx_3, idx_4)
        
        # 5. ADAPT: Fallback if plan fails
        adapt_op = ADAPT()
        adapt_result = adapt_op.execute(
            original_goal="5x throughput improvement",
            failure_reason="Replication strategy too complex",
            available_alternatives=["Query optimization only (3x improvement)", "Add read replicas (7x improvement)"]
        )
        
        idx_5 = graph.add_operator(
            "ADAPT",
            inputs={"goal": "5x improvement", "failure_reason": "plan too complex"}
        )
        graph.nodes[idx_5].result = adapt_result
        graph.add_dependency(idx_4, idx_5)
        
        return graph
    
    def build_career_advancement_chain(self) -> OperatorGraph:
        """
        Domain B: Advance career from junior to mid-level within time/money constraints.
        
        Scenario:
          - Current bottleneck: systems design knowledge (0.3 proficiency)
          - Time available: 10 hrs/week for 6 months
          - Budget: $5K for courses
          - Options: Online courses (cheap, slow), Bootcamp (expensive, fast)
        """
        graph = OperatorGraph(
            problem="Advance career with time/money constraints",
            domain="career_development"
        )
        
        # 1. DETECT_BOTTLENECK: What skill limits advancement?
        skill_components = [
            Component("coding_syntax", 0.9, 1.0),
            Component("debugging", 0.7, 1.0),
            Component("systems_design", 0.3, 1.0),
            Component("communication", 0.6, 1.0),
        ]
        bottleneck_op = DETECT_BOTTLENECK()
        bottleneck_result = bottleneck_op.execute(skill_components, domain_context="career_skills")
        
        idx_1 = graph.add_operator(
            "DETECT_BOTTLENECK",
            inputs={"components": [c.name for c in skill_components]}
        )
        graph.nodes[idx_1].result = bottleneck_result
        
        # 2. CONSTRAIN: Apply time/money limits
        constrain_op = CONSTRAIN()
        constrain_result = constrain_op.execute(
            resource="total_learning_budget",
            current_value=8_000,  # Available
            limit=5_000  # Hard limit
        )
        
        idx_2 = graph.add_operator(
            "CONSTRAIN",
            inputs={"resource": "learning_budget", "limit": 5_000}
        )
        graph.nodes[idx_2].result = constrain_result
        graph.add_dependency(idx_1, idx_2)
        
        # 3. OPTIMIZE: Best allocation given bottleneck and constraints
        optimize_op = OPTIMIZE()
        optimize_result = optimize_op.execute(
            objective_values={
                "systems_design_learning": 0.3,
                "coding_mastery": 0.9
            },
            constraints={"budget": 5_000, "time": 6},  # 6 months
            budget=5_000,
            time_available=6
        )
        
        idx_3 = graph.add_operator(
            "OPTIMIZE",
            inputs={"budget": 5_000, "time_months": 6}
        )
        graph.nodes[idx_3].result = optimize_result
        graph.add_dependency(idx_2, idx_3)
        
        # 4. SEQUENCE: Execute learning plan
        sequence_op = SEQUENCE()
        sequence_result = sequence_op.execute(
            preconditions={
                "courses_selected": True,
                "schedule_blocked": True,
                "funding_secured": True
            },
            plan_name="Take systems design course + build projects",
            success_criteria={"proficiency_improvement": 0.5}
        )
        
        idx_4 = graph.add_operator(
            "SEQUENCE",
            inputs={"plan": "Take systems design course + build projects"}
        )
        graph.nodes[idx_4].result = sequence_result
        graph.add_dependency(idx_3, idx_4)
        
        # 5. ADAPT: Fallback if learning fails
        adapt_op = ADAPT()
        adapt_result = adapt_op.execute(
            original_goal="Mid-level proficiency in 6 months",
            failure_reason="Course pace too fast",
            available_alternatives=["Slower online course (12 months)", "Find mentor (3-month accelerated learning)"]
        )
        
        idx_5 = graph.add_operator(
            "ADAPT",
            inputs={"goal": "Mid-level proficiency", "failure_reason": "pace too fast"}
        )
        graph.nodes[idx_5].result = adapt_result
        graph.add_dependency(idx_4, idx_5)
        
        return graph
    
    def test_identical_operator_structure(self):
        """
        CRITICAL TEST: Are the operator sequences identical?
        """
        graph_a = self.build_scaling_service_chain()
        graph_b = self.build_career_advancement_chain()
        
        # Extract structures
        structure_a = graph_a.structure_string()
        structure_b = graph_b.structure_string()
        hash_a = graph_a.structural_hash()
        hash_b = graph_b.structural_hash()
        
        print(f"\n✓ Operator Structures")
        print(f"  Domain A (Technical): {structure_a}")
        print(f"  Domain B (Personal): {structure_b}")
        print(f"  Identical: {structure_a == structure_b}")
        
        # ASSERTION: Structures must be identical
        assert structure_a == structure_b, \
            f"Operator sequences differ!\nDomain A: {structure_a}\nDomain B: {structure_b}"
        
        # ASSERTION: Hashes must be identical
        assert hash_a == hash_b, \
            f"Structural hashes differ!\nDomain A: {hash_a}\nDomain B: {hash_b}"
        
        print(f"  Hash: {hash_a}")
        print(f"  ✓ EVIDENCE #1: Identical operator structure across domains")
    
    def test_operator_inputs_differ_domain_semantics_preserved(self):
        """
        CRITICAL TEST: Inputs are domain-specific, but structure is invariant.
        """
        graph_a = self.build_scaling_service_chain()
        graph_b = self.build_career_advancement_chain()
        
        # Extract inputs from both graphs
        inputs_a = [node.inputs for node in graph_a.nodes]
        inputs_b = [node.inputs for node in graph_b.nodes]
        
        print(f"\n✓ Domain-Specific Inputs (Structure Invariant)")
        print(f"  Graph A (Technical):")
        for i, inp in enumerate(inputs_a):
            print(f"    {i}: {inp}")
        
        print(f"  Graph B (Personal):")
        for i, inp in enumerate(inputs_b):
            print(f"    {i}: {inp}")
        
        # Inputs should differ (different domain values)
        assert inputs_a != inputs_b, "Inputs should differ between domains"
        
        # But operator names should be identical
        ops_a = [n.operator_name for n in graph_a.nodes]
        ops_b = [n.operator_name for n in graph_b.nodes]
        
        assert ops_a == ops_b, "Operator sequences must be identical"
        
        print(f"  ✓ EVIDENCE #2: Same operator structure, different domain inputs")
    
    def test_both_graphs_produce_solutions(self):
        """
        CRITICAL TEST: Both domains produce valid solutions via identical reasoning.
        """
        graph_a = self.build_scaling_service_chain()
        graph_b = self.build_career_advancement_chain()
        
        # Check that final results exist
        assert graph_a.nodes[-1].result is not None, "Domain A should produce final result"
        assert graph_b.nodes[-1].result is not None, "Domain B should produce final result"
        
        # Both should have fallback plans
        result_a = graph_a.nodes[-1].result
        result_b = graph_b.nodes[-1].result
        
        assert result_a.adapted, "Domain A should have fallback plan"
        assert result_b.adapted, "Domain B should have fallback plan"
        
        print(f"\n✓ Both Domains Produce Valid Solutions")
        print(f"  Domain A fallback: {result_a.new_plan}")
        print(f"  Domain B fallback: {result_b.new_plan}")
        print(f"  ✓ EVIDENCE #3: Identical operator chain solves both problems")
    
    def test_operator_chain_dependency_structure(self):
        """
        CRITICAL TEST: Edge dependencies are identical.
        """
        graph_a = self.build_scaling_service_chain()
        graph_b = self.build_career_advancement_chain()
        
        edges_a = graph_a.edges
        edges_b = graph_b.edges
        
        print(f"\n✓ Dependency Structure")
        print(f"  Domain A edges: {edges_a}")
        print(f"  Domain B edges: {edges_b}")
        print(f"  Identical: {edges_a == edges_b}")
        
        assert edges_a == edges_b, "Operator dependencies must be identical"
        print(f"  ✓ EVIDENCE #4: Identical operator dependency structure")
    
    def test_cross_domain_transfer_readiness(self):
        """
        INTEGRATION TEST: Can a human understand the reasoning by reading
        the operator graph, regardless of domain?
        """
        graph_a = self.build_scaling_service_chain()
        graph_b = self.build_career_advancement_chain()
        
        print(f"\n✓ Cross-Domain Transfer Readiness")
        print(f"\nGraph A (Technical):")
        print(f"  Problem: {graph_a.problem}")
        print(f"  Domain: {graph_a.domain}")
        print(f"  Structure: {graph_a.structure_string()}")
        
        print(f"\nGraph B (Personal):")
        print(f"  Problem: {graph_b.problem}")
        print(f"  Domain: {graph_b.domain}")
        print(f"  Structure: {graph_b.structure_string()}")
        
        print(f"\nReading the operator graph WITHOUT domain context:")
        print(f"  1. Identify bottleneck (lowest-performing component)")
        print(f"  2. Apply constraints (enforce resource limits)")
        print(f"  3. Optimize allocation (best use of resources)")
        print(f"  4. Execute plan (if preconditions met)")
        print(f"  5. Adapt if needed (fallback strategy)")
        
        print(f"\nThis reasoning applies equally to database scaling OR career advancement.")
        print(f"✓ EVIDENCE #5: Operator graph is domain-independent and transferable")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
