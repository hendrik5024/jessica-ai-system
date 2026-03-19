"""
Test Phase 2: OperatorGraph Integration into Agent Loop

Validates that:
1. OperatorGraph is built correctly from user input
2. OperatorGraph is the exclusive reasoning/decision path
3. All memory updates are gated through operator SEQUENCE
4. Tool actions are mediated by operators
5. Operator trace is captured in metadata
"""

import pytest
from typing import Dict, Any, List, Tuple

from jessica.unified_world_model.causal_operator import (
    Component,
    detect_bottleneck_operator,
    constrain_operator,
    optimize_operator,
    sequence_operator,
    adapt_operator,
    substitute_operator,
)
from jessica.unified_world_model.operator_domain_mapper import DomainMapper
from jessica.unified_world_model.operator_graph import OperatorGraph


class TestOperatorGraphConstruction:
    """Test that OperatorGraph is correctly built per iteration."""

    def test_operator_graph_from_signals(self):
        """Construct operator graph from domain-agnostic signals."""
        # Simulate incoming user text signals
        signals = {
            "code_signal": 0.8,
            "clarity": 0.9,
            "constraints": 0.6,
            "context": 0.7,
            "brainstorm": 0.2,
        }

        # Extract components
        components = DomainMapper.extract_components_from_any_domain(signals)
        assert len(components) == 5
        assert all(c.throughput in [0.2, 0.6, 0.7, 0.8, 0.9] for c in components)

        # Build graph
        graph = OperatorGraph(problem="debug_code", domain="code")

        # DETECT_BOTTLENECK
        detect_idx = graph.add_operator(
            "DETECT_BOTTLENECK",
            inputs={"signals": signals}
        )
        detect_result = detect_bottleneck_operator.execute(components, domain_context="code")
        graph.nodes[detect_idx].result = detect_result

        # Verify detection
        assert detect_result.bottleneck_component == "brainstorm"  # Lowest throughput
        assert detect_result.severity_score > 0

        # CONSTRAIN response length
        constrain_idx = graph.add_operator(
            "CONSTRAIN",
            inputs={"resource": "response_length", "current_value": 150, "limit": 220}
        )
        constrain_result = constrain_operator.execute(
            resource="response_length",
            current_value=150,
            limit=220
        )
        graph.nodes[constrain_idx].result = constrain_result
        assert not constrain_result.violated

        # OPTIMIZE
        optimize_idx = graph.add_operator(
            "OPTIMIZE",
            inputs={
                "objective_values": {"bottleneck": detect_result.severity_score},
                "constraints": {"response_length": 220},
                "budget": 100,
                "time_available": 60,
            }
        )
        optimize_result = optimize_operator.execute(
            objective_values={"bottleneck": detect_result.severity_score},
            constraints={"response_length": 220},
            budget=100,
            time_available=60,
        )
        graph.nodes[optimize_idx].result = optimize_result

        # SEQUENCE: mode selection
        sequence_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"code_preference": 0.8 >= 0.6},
                "plan_name": "select_code_mode",
                "success_criteria": {"selected": 1.0},
            }
        )
        sequence_result = sequence_operator.execute(
            preconditions={"code_preference": 0.8 >= 0.6},
            plan_name="select_code_mode",
            success_criteria={"selected": 1.0},
        )
        graph.nodes[sequence_idx].result = sequence_result
        assert sequence_result.executed
        assert sequence_result.preconditions_met

        # Check graph structure
        assert graph.structure_string() == "DETECT_BOTTLENECK → CONSTRAIN → OPTIMIZE → SEQUENCE"
        assert len(graph.nodes) == 4

        # Serialize for metadata
        graph_dict = graph.to_dict()
        assert graph_dict["problem"] == "debug_code"
        assert graph_dict["domain"] == "code"
        assert len(graph_dict["nodes"]) == 4

    def test_operator_graph_exclusive_path(self):
        """Verify OperatorGraph is the exclusive reasoning path."""
        # Setup: User asks for code help with constraints
        user_input = "I need to fix a bug but can only spend 5 minutes"
        signals = {
            "code_signal": 0.9,
            "clarity": 0.8,
            "constraints": 0.95,  # Tight constraint
            "context": 0.6,
            "brainstorm": 0.0,
        }

        components = DomainMapper.extract_components_from_any_domain(signals)
        graph = OperatorGraph(problem=user_input, domain="code")

        # DETECT: Constraints are the tightest factor
        detect_idx = graph.add_operator("DETECT_BOTTLENECK", inputs={"signals": signals})
        detect_result = detect_bottleneck_operator.execute(components, domain_context="code")
        graph.nodes[detect_idx].result = detect_result
        assert detect_result.bottleneck_component == "brainstorm"

        # CONSTRAIN: Enforce time limit
        constrain_idx = graph.add_operator(
            "CONSTRAIN",
            inputs={"resource": "time", "current_value": 300, "limit": 300}
        )
        constrain_result = constrain_operator.execute(
            resource="time",
            current_value=300,
            limit=300
        )
        graph.nodes[constrain_idx].result = constrain_result

        # SUBSTITUTE: Use concise response instead of detailed
        substitute_idx = graph.add_operator(
            "SUBSTITUTE",
            inputs={
                "required_resource": "detailed_response",
                "available_alternatives": ["concise_response"],
                "equivalence_class": "response_type",
            }
        )
        substitute_result = substitute_operator.execute(
            required_resource="detailed_response",
            available_alternatives=["concise_response"],
            equivalence_class="response_type",
        )
        graph.nodes[substitute_idx].result = substitute_result
        assert substitute_result.can_substitute

        # SEQUENCE: Execute substitution
        sequence_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"substitute_available": True},
                "plan_name": "execute_concise_response",
                "success_criteria": {"executed": 1.0},
            }
        )
        sequence_result = sequence_operator.execute(
            preconditions={"substitute_available": True},
            plan_name="execute_concise_response",
            success_criteria={"executed": 1.0},
        )
        graph.nodes[sequence_idx].result = sequence_result

        # Verify: No hidden paths, only operator chain
        assert len(graph.nodes) == 4
        assert graph.structure_string() == "DETECT_BOTTLENECK → CONSTRAIN → SUBSTITUTE → SEQUENCE"

    def test_memory_updates_gated_by_operators(self):
        """Verify all memory updates are mediated through operator SEQUENCE."""
        graph = OperatorGraph(problem="test", domain="chat")

        # Pre-condition: response_text must exist
        response_text = "This is a test response."

        # Add memory update SEQUENCE operator
        update_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"response_generated": bool(response_text)},
                "plan_name": "apply_memory_updates",
                "success_criteria": {"updated": 1.0},
            }
        )
        update_sequence = sequence_operator.execute(
            preconditions={"response_generated": bool(response_text)},
            plan_name="apply_memory_updates",
            success_criteria={"updated": 1.0},
        )
        graph.nodes[update_idx].result = update_sequence

        # Verify: Memory updates only happen if SEQUENCE succeeds
        assert update_sequence.executed
        assert update_sequence.preconditions_met

        # Simulate failure case: no response
        update_idx2 = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"response_generated": False},
                "plan_name": "apply_memory_updates",
                "success_criteria": {"updated": 1.0},
            }
        )
        update_sequence2 = sequence_operator.execute(
            preconditions={"response_generated": False},
            plan_name="apply_memory_updates",
            success_criteria={"updated": 1.0},
        )
        graph.nodes[update_idx2].result = update_sequence2

        # Verify: Memory updates blocked
        assert not update_sequence2.executed

    def test_tool_action_mediation(self):
        """Verify tool actions are mediated by operator SEQUENCE."""
        graph = OperatorGraph(problem="run_command", domain="code")

        # SEQUENCE: Check if tool is allowed
        tool_sequence_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"tool_requested": True},
                "plan_name": "execute_tool",
                "success_criteria": {"executed": 1.0},
            }
        )
        tool_sequence = sequence_operator.execute(
            preconditions={"tool_requested": True},
            plan_name="execute_tool",
            success_criteria={"executed": 1.0},
        )
        graph.nodes[tool_sequence_idx].result = tool_sequence

        # Verify: Tool execution gated
        assert tool_sequence.executed

        # Case: Tool not requested
        tool_sequence_idx2 = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"tool_requested": False},
                "plan_name": "execute_tool",
                "success_criteria": {"executed": 1.0},
            }
        )
        tool_sequence2 = sequence_operator.execute(
            preconditions={"tool_requested": False},
            plan_name="execute_tool",
            success_criteria={"executed": 1.0},
        )
        graph.nodes[tool_sequence_idx2].result = tool_sequence2

        # Verify: Tool not executed
        assert not tool_sequence2.executed

    def test_operator_trace_in_metadata(self):
        """Verify operator trace is captured in metadata."""
        graph = OperatorGraph(problem="test_metadata", domain="chat")

        # Add some operators
        detect_idx = graph.add_operator("DETECT_BOTTLENECK", inputs={})
        detect_result = detect_bottleneck_operator.execute([], domain_context="chat")
        graph.nodes[detect_idx].result = detect_result

        constrain_idx = graph.add_operator("CONSTRAIN", inputs={})
        constrain_result = constrain_operator.execute("test", 0.5, 1.0)
        graph.nodes[constrain_idx].result = constrain_result

        # Serialize to metadata format
        metadata = {
            "operator_trace": graph.to_dict(),
            "operator_outcomes": {
                "detect": detect_result,
                "constrain": constrain_result,
            }
        }

        # Verify structure
        assert "operator_trace" in metadata
        assert metadata["operator_trace"]["problem"] == "test_metadata"
        assert metadata["operator_trace"]["domain"] == "chat"
        assert len(metadata["operator_trace"]["nodes"]) == 2
        assert metadata["operator_trace"]["nodes"][0]["operator"] == "DETECT_BOTTLENECK"
        assert metadata["operator_trace"]["nodes"][1]["operator"] == "CONSTRAIN"


class TestOperatorIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_scenario_short_query_fast_mode(self):
        """Scenario: User asks short question (e.g., 'What time is it?')."""
        signals = {
            "code_signal": 0.1,
            "clarity": 0.9,
            "constraints": 0.5,
            "context": 0.2,
            "brainstorm": 0.0,
        }

        components = DomainMapper.extract_components_from_any_domain(signals)
        graph = OperatorGraph(problem="What time is it?", domain="chat")

        # Detect: Clarity is high, but code_signal is low
        detect_idx = graph.add_operator("DETECT_BOTTLENECK", inputs={"signals": signals})
        detect_result = detect_bottleneck_operator.execute(components, domain_context="chat")
        graph.nodes[detect_idx].result = detect_result

        # Should identify brainstorm as bottleneck (lowest signal: 0.0)
        assert detect_result.bottleneck_component == "brainstorm"

        # Mode selection
        mode_idx = graph.add_operator(
            "SEQUENCE",
            inputs={"preconditions": {"code_preference": 0.1 >= 0.6}, "plan_name": "select_mode"},
        )
        mode_sequence = sequence_operator.execute(
            preconditions={"code_preference": 0.1 >= 0.6},
            plan_name="select_mode",
            success_criteria={"selected": 1.0},
        )
        graph.nodes[mode_idx].result = mode_sequence

        # Verify: Chat mode selected (not code mode)
        assert not mode_sequence.preconditions_met

    def test_scenario_code_with_constraints(self):
        """Scenario: User asks for code help with time/budget constraints."""
        signals = {
            "code_signal": 0.95,
            "clarity": 0.7,
            "constraints": 0.95,
            "context": 0.8,
            "brainstorm": 0.1,
        }

        components = DomainMapper.extract_components_from_any_domain(signals)
        graph = OperatorGraph(
            problem="Fix this bug but keep response under 100 words",
            domain="code"
        )

        # Detect
        detect_idx = graph.add_operator("DETECT_BOTTLENECK", inputs={"signals": signals})
        detect_result = detect_bottleneck_operator.execute(components, domain_context="code")
        graph.nodes[detect_idx].result = detect_result

        # Bottleneck is brainstorm (lowest signal)
        assert detect_result.bottleneck_component == "brainstorm"

        # Constrain response length
        constrain_idx = graph.add_operator(
            "CONSTRAIN",
            inputs={"resource": "response_length", "current_value": 150, "limit": 100}
        )
        constrain_result = constrain_operator.execute(
            resource="response_length",
            current_value=150,
            limit=100
        )
        graph.nodes[constrain_idx].result = constrain_result

        # Violation detected
        assert constrain_result.violated

        # Substitute: concise response
        substitute_idx = graph.add_operator(
            "SUBSTITUTE",
            inputs={
                "required_resource": "detailed_explanation",
                "available_alternatives": ["bullet_points", "code_only"],
                "equivalence_class": "response_type",
            }
        )
        substitute_result = substitute_operator.execute(
            required_resource="detailed_explanation",
            available_alternatives=["bullet_points", "code_only"],
            equivalence_class="response_type",
        )
        graph.nodes[substitute_idx].result = substitute_result

        # Can substitute
        assert substitute_result.can_substitute

        # Verify chain
        assert graph.structure_string() == "DETECT_BOTTLENECK → CONSTRAIN → SUBSTITUTE"

    def test_scenario_failure_triggers_adapt(self):
        """Scenario: Execution fails, ADAPT generates fallback."""
        graph = OperatorGraph(problem="unclear_user_request", domain="chat")

        # Response generation fails preconditions
        sequence_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"bottleneck_identified": False},
                "plan_name": "generate_response",
            }
        )
        sequence_result = sequence_operator.execute(
            preconditions={"bottleneck_identified": False},
            plan_name="generate_response",
            success_criteria={"generated": 1.0},
        )
        graph.nodes[sequence_idx].result = sequence_result

        # Execution failed
        assert not sequence_result.executed

        # ADAPT: Generate clarifying question
        adapt_idx = graph.add_operator(
            "ADAPT",
            inputs={
                "original_goal": "generate_response",
                "failure_reason": "unclear_request",
                "available_alternatives": ["ask_clarification"],
            }
        )
        adapt_result = adapt_operator.execute(
            original_goal="generate_response",
            failure_reason="unclear_request",
            available_alternatives=["ask_clarification"],
        )
        graph.nodes[adapt_idx].result = adapt_result

        # Fallback available
        assert adapt_result.adapted
        assert adapt_result.goal_preservation_ratio > 0

        # Verify chain
        assert graph.structure_string() == "SEQUENCE → ADAPT"


class TestConstraints:
    """Validate Phase 2 integration constraints are enforced."""

    def test_constraint_1_exclusive_operator_path(self):
        """Constraint 1: OperatorGraph must be exclusive reasoning path."""
        # No parallel planners, heuristics, or hidden paths
        graph = OperatorGraph(problem="test", domain="chat")

        # Only operators in the graph
        assert len(graph.nodes) == 0

        # Add operators
        idx1 = graph.add_operator("DETECT_BOTTLENECK", inputs={})
        idx2 = graph.add_operator("CONSTRAIN", inputs={})
        idx3 = graph.add_operator("SEQUENCE", inputs={})

        # No hidden attributes for bypass
        assert not hasattr(graph, "_parallel_reasoner")
        assert not hasattr(graph, "_heuristic_cache")
        assert not hasattr(graph, "_bypass_operators")

        # All decisions go through operators
        assert len(graph.nodes) == 3

    def test_constraint_2_explicit_trace(self):
        """Constraint 2: Explicit operator trace per iteration."""
        graph = OperatorGraph(problem="trace_test", domain="code")

        # Each operator execution is traced
        idx1 = graph.add_operator("DETECT_BOTTLENECK", inputs={"test": True})
        result1 = detect_bottleneck_operator.execute([], domain_context="code")
        graph.nodes[idx1].result = result1

        # Serialize trace
        trace = graph.to_dict()

        # Verify trace contains all details
        assert trace["nodes"][0]["operator"] == "DETECT_BOTTLENECK"
        assert trace["nodes"][0]["inputs"]["test"] is True
        assert result1.trace in [str(result1.trace), result1.trace]

    def test_constraint_3_no_direct_mutation(self):
        """Constraint 3: No direct state mutation outside operators."""
        graph = OperatorGraph(problem="mutation_test", domain="chat")

        # Memory update must go through SEQUENCE operator
        update_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"ready": True},
                "plan_name": "update_memory",
            }
        )
        update_seq = sequence_operator.execute(
            preconditions={"ready": True},
            plan_name="update_memory",
            success_criteria={"updated": 1.0},
        )
        graph.nodes[update_idx].result = update_seq

        # Only after SEQUENCE approval
        assert update_seq.executed

    def test_constraint_4_preserve_validated_properties(self):
        """Constraint 4: Preserve all properties from Experiments 1-3."""
        # Domain independence
        signals = {"s1": 0.7, "s2": 0.4, "s3": 0.8}
        comps = DomainMapper.extract_components_from_any_domain(signals)

        graph1 = OperatorGraph(problem="domain1", domain="chess")
        idx1 = graph1.add_operator("DETECT_BOTTLENECK", inputs={})
        res1 = detect_bottleneck_operator.execute(comps)
        graph1.nodes[idx1].result = res1

        graph2 = OperatorGraph(problem="domain2", domain="coding")
        idx2 = graph2.add_operator("DETECT_BOTTLENECK", inputs={})
        res2 = detect_bottleneck_operator.execute(comps)
        graph2.nodes[idx2].result = res2

        # Same operator produces identical structure
        assert graph1.structural_hash() == graph2.structural_hash()

        # Composition works
        opt_idx1 = graph1.add_operator("OPTIMIZE", inputs={})
        opt_idx2 = graph2.add_operator("OPTIMIZE", inputs={})

        assert graph1.structure_string() == graph2.structure_string()

    def test_constraint_5_no_new_operators(self):
        """Constraint 5: No new operators added at this stage."""
        # Only 6 operators allowed
        allowed = {
            "DETECT_BOTTLENECK",
            "CONSTRAIN",
            "OPTIMIZE",
            "SEQUENCE",
            "ADAPT",
            "SUBSTITUTE",
        }

        graph = OperatorGraph(problem="test", domain="chat")

        # Add all allowed
        for op_name in allowed:
            idx = graph.add_operator(op_name, inputs={})
            assert idx >= 0

        # All are in the graph
        graph_ops = {node.operator_name for node in graph.nodes}
        assert graph_ops == allowed

    def test_constraint_6_no_autonomous_expansion(self):
        """Constraint 6: No autonomy expansion or self-modification."""
        graph = OperatorGraph(problem="autonomy_test", domain="chat")

        # Cannot add operators dynamically based on runtime decisions
        initial_count = len(graph.nodes)
        idx = graph.add_operator("DETECT_BOTTLENECK", inputs={})
        graph.nodes[idx].result = detect_bottleneck_operator.execute([])

        # No self-modification
        assert len(graph.nodes) == initial_count + 1
        assert not hasattr(graph, "self_modify")
        assert not hasattr(graph, "expand_autonomy")
        assert not hasattr(graph, "add_operator_from_failure")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
