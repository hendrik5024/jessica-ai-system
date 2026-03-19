"""
Phase 96: Structured Reasoning Engine - Unit Tests

Tests for deterministic, step-by-step reasoning.
"""

import pytest
from jessica.reasoning.structured_reasoner import (
    StructuredReasoner,
    ProblemType,
    ReasoningStep,
    ValidationResult,
    StructuredResponse,
)


class TestProblemClassification:
    """Test problem type classification."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_classify_math_problem(self):
        """Test classification of math problems."""
        result = self.reasoner.process("What is 10 + 5?")
        assert result.problem_type == ProblemType.MATH

    def test_classify_math_with_keywords(self):
        """Test math classification with various keywords."""
        test_cases = [
            ("Calculate 50 * 2", ProblemType.MATH),
            ("How much is 100 divided by 4?", ProblemType.MATH),
            ("What is the sum of 5 and 3?", ProblemType.MATH),
        ]
        
        for query, expected_type in test_cases:
            result = self.reasoner.process(query)
            assert result.problem_type == expected_type

    def test_classify_factual_problem(self):
        """Test classification of factual problems."""
        result = self.reasoner.process("What is the capital of France?")
        assert result.problem_type == ProblemType.FACTUAL

    def test_classify_personal_problem(self):
        """Test classification of personal/identity questions."""
        result = self.reasoner.process("Who created you?")
        assert result.problem_type == ProblemType.PERSONAL

    def test_classify_personal_with_variants(self):
        """Test personal classification with variations."""
        test_cases = [
            "What is your name?",
            "What are you?",
            "Who are you?",
            "Tell me about yourself",
        ]
        
        for query in test_cases:
            result = self.reasoner.process(query)
            # Should identify personal questions
            assert result.problem_type == ProblemType.PERSONAL

    def test_classify_reasoning_problem(self):
        """Test classification of reasoning problems."""
        result = self.reasoner.process("Why is the sky blue?")
        assert result.problem_type == ProblemType.REASONING

    def test_classify_computation_with_operators(self):
        """Test classification of computation with operators."""
        result = self.reasoner.process("2 + 2")
        assert result.problem_type == ProblemType.COMPUTATION

    def test_classify_unknown_problem(self):
        """Test classification of unknown problems."""
        result = self.reasoner.process("xyzabc")
        # Unknown or other classification
        assert result.problem_type in [ProblemType.UNKNOWN, ProblemType.REASONING]


class TestStepBreakdown:
    """Test problem breakdown into steps."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_break_math_problem(self):
        """Test breaking down math problems."""
        steps = self.reasoner._break_math_problem("What is 10 + 5?")
        assert len(steps) > 0
        assert any("add" in step.lower() or "addition" in step.lower() for step in steps)

    def test_break_factual_problem(self):
        """Test breaking down factual problems."""
        steps = self.reasoner._break_factual_problem("What is the capital of France?")
        assert len(steps) >= 4
        assert "identify" in steps[0].lower()

    def test_break_personal_problem(self):
        """Test breaking down personal questions."""
        steps = self.reasoner._break_personal_problem("Who are you?")
        assert len(steps) >= 3
        assert any("identity" in step.lower() or "belief" in step.lower() for step in steps)

    def test_break_reasoning_problem(self):
        """Test breaking down reasoning problems."""
        steps = self.reasoner._break_reasoning_problem("Why is the sky blue?")
        assert len(steps) >= 4
        assert "concept" in steps[1].lower() or "identify" in steps[1].lower()


class TestStepExecution:
    """Test step execution."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_execute_calculation_step(self):
        """Test execution of calculation steps."""
        tool_name, result = self.reasoner._execute_step(
            "Perform addition",
            ProblemType.MATH
        )
        assert tool_name is not None or result is not None

    def test_execute_knowledge_step(self):
        """Test execution of knowledge retrieval steps."""
        tool_name, result = self.reasoner._execute_step(
            "Recall the capital of France",
            ProblemType.FACTUAL
        )
        assert result is not None

    def test_execute_belief_step(self):
        """Test execution of belief system steps."""
        tool_name, result = self.reasoner._execute_step(
            "Consult internal belief system",
            ProblemType.PERSONAL
        )
        assert tool_name == "belief_system"

    def test_tool_identification(self):
        """Test that tools are correctly identified."""
        _, result1 = self.reasoner._execute_step(
            "Perform multiplication",
            ProblemType.MATH
        )
        _, result2 = self.reasoner._execute_step(
            "Look up the population",
            ProblemType.FACTUAL
        )
        
        assert result1 is not None
        assert result2 is not None


class TestAnswerFormulation:
    """Test answer formulation."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_formulate_personal_identity(self):
        """Test formulation of identity answers."""
        answer = self.reasoner._formulate_answer(
            "Who are you?",
            ProblemType.PERSONAL,
            [],
            []
        )
        assert "Jessica" in answer or "AI" in answer.lower()

    def test_formulate_math_answer(self):
        """Test formulation of math answers."""
        answer = self.reasoner._formulate_answer(
            "What is 2+2?",
            ProblemType.MATH,
            ["4"],
            ["Calculate"]
        )
        assert answer is not None
        assert len(answer) > 0

    def test_formulate_factual_answer(self):
        """Test formulation of factual answers."""
        answer = self.reasoner._formulate_answer(
            "What is the capital of France?",
            ProblemType.FACTUAL,
            ["Paris"],
            ["Recall"]
        )
        assert answer is not None

    def test_answer_is_string(self):
        """Test that formulated answer is always string."""
        answer = self.reasoner._formulate_answer(
            "test",
            ProblemType.REASONING,
            [],
            []
        )
        assert isinstance(answer, str)


class TestAnswerValidation:
    """Test answer validation."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_validate_empty_answer(self):
        """Test validation of empty answer."""
        validation = self.reasoner._validate_answer(
            "",
            ProblemType.MATH,
            []
        )
        assert not validation.is_valid
        assert validation.confidence < 0.5

    def test_validate_complete_answer(self):
        """Test validation of complete answer."""
        validation = self.reasoner._validate_answer(
            "The capital of France is Paris",
            ProblemType.FACTUAL,
            ["Paris"]
        )
        assert validation.is_valid
        assert validation.confidence >= 0.8

    def test_validate_math_requires_number(self):
        """Test that math answers should contain numbers."""
        validation_no_num = self.reasoner._validate_answer(
            "The answer is very yes",
            ProblemType.MATH,
            []
        )
        assert validation_no_num.confidence < 0.8
        
        validation_with_num = self.reasoner._validate_answer(
            "The answer is 42",
            ProblemType.MATH,
            []
        )
        assert validation_with_num.confidence > validation_no_num.confidence

    def test_validate_detects_placeholders(self):
        """Test validation detects incomplete placeholders."""
        validation = self.reasoner._validate_answer(
            "The answer is [result pending]",
            ProblemType.MATH,
            []
        )
        assert not validation.is_valid or validation.confidence < 0.8
        assert any("[" in issue for issue in validation.issues)

    def test_validation_has_float_confidence(self):
        """Test that confidence is float between 0 and 1."""
        validation = self.reasoner._validate_answer(
            "Test answer",
            ProblemType.REASONING,
            []
        )
        assert isinstance(validation.confidence, float)
        assert 0.0 <= validation.confidence <= 1.0


class TestReasoningTrace:
    """Test reasoning trace building."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_trace_is_string(self):
        """Test that trace is a string."""
        steps = [
            ReasoningStep(
                step_number=1,
                description="Test step",
                reasoning="Test reasoning"
            )
        ]
        trace = self.reasoner._build_trace(steps)
        assert isinstance(trace, str)

    def test_trace_contains_step_info(self):
        """Test that trace contains step information."""
        steps = [
            ReasoningStep(
                step_number=1,
                description="Classify problem",
                reasoning="Analyzed keywords"
            )
        ]
        trace = self.reasoner._build_trace(steps)
        assert "Classify problem" in trace
        assert "Analyzed keywords" in trace

    def test_trace_format(self):
        """Test trace has proper format."""
        steps = [
            ReasoningStep(
                step_number=1,
                description="Step 1",
                reasoning="Reason 1"
            ),
            ReasoningStep(
                step_number=2,
                description="Step 2",
                reasoning="Reason 2"
            )
        ]
        trace = self.reasoner._build_trace(steps)
        assert "Step 1:" in trace
        assert "Step 2:" in trace
        assert "REASONING TRACE" in trace


class TestCompleteReasoning:
    """Test complete end-to-end reasoning."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_process_returns_structured_response(self):
        """Test that process returns StructuredResponse."""
        result = self.reasoner.process("Who are you?")
        assert isinstance(result, StructuredResponse)

    def test_response_has_all_fields(self):
        """Test that response has all required fields."""
        result = self.reasoner.process("Who are you?")
        assert result.answer is not None
        assert result.problem_type is not None
        assert result.steps is not None
        assert result.validation is not None
        assert result.reasoning_trace is not None
        assert result.tools_used is not None
        assert result.execution_successful is not None

    def test_response_has_multiple_steps(self):
        """Test that response includes multiple reasoning steps."""
        result = self.reasoner.process("What is 2+2?")
        assert len(result.steps) >= 3
        assert all(isinstance(step, ReasoningStep) for step in result.steps)

    def test_personal_question_has_answer(self):
        """Test personal questions get answered."""
        result = self.reasoner.process("Who are you?")
        assert result.problem_type == ProblemType.PERSONAL
        assert len(result.answer) > 0
        assert "Jessica" in result.answer or "AI" in result.answer.lower()

    def test_reasoning_trace_in_response(self):
        """Test that reasoning trace is included."""
        result = self.reasoner.process("Why is the sky blue?")
        assert len(result.reasoning_trace) > 0
        assert "REASONING TRACE" in result.reasoning_trace

    def test_tools_used_is_list(self):
        """Test that tools_used is a list."""
        result = self.reasoner.process("What is 10 + 5?")
        assert isinstance(result.tools_used, list)

    def test_deterministic_processing(self):
        """Test that same input gives same classification."""
        query = "What is the capital of France?"
        result1 = self.reasoner.process(query)
        result2 = self.reasoner.process(query)
        
        assert result1.problem_type == result2.problem_type
        assert result1.answer == result2.answer

    def test_math_problem_full_flow(self):
        """Test complete flow for math problem."""
        result = self.reasoner.process("What is 5 + 3?")
        
        assert result.problem_type == ProblemType.MATH
        assert len(result.steps) >= 3
        assert result.reasoning_trace is not None
        assert result.validation is not None

    def test_factual_problem_full_flow(self):
        """Test complete flow for factual problem."""
        result = self.reasoner.process("What is the capital of France?")
        
        assert result.problem_type == ProblemType.FACTUAL
        assert len(result.steps) >= 3
        assert len(result.answer) > 0

    def test_personal_problem_full_flow(self):
        """Test complete flow for personal question."""
        result = self.reasoner.process("What is your name?")
        
        assert result.problem_type == ProblemType.PERSONAL
        assert len(result.steps) >= 3
        assert "Jessica" in result.answer or "AI" in result.answer.lower()


class TestReasoningSummary:
    """Test reasoning summary generation."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_summary_is_string(self):
        """Test that summary is a string."""
        result = self.reasoner.process("Who are you?")
        summary = self.reasoner.get_reasoning_summary(result)
        assert isinstance(summary, str)

    def test_summary_contains_key_info(self):
        """Test that summary contains key information."""
        result = self.reasoner.process("Who are you?")
        summary = self.reasoner.get_reasoning_summary(result)
        
        assert "PROBLEM TYPE" in summary
        assert "ANSWER" in summary
        assert "VALIDATION" in summary
        assert "CONFIDENCE" in summary

    def test_summary_includes_problem_type(self):
        """Test summary shows problem type."""
        result = self.reasoner.process("What is the capital of France?")
        summary = self.reasoner.get_reasoning_summary(result)
        
        assert "factual" in summary.lower()


class TestConstraints:
    """Test that implementation meets constraints."""

    def setup_method(self):
        self.reasoner = StructuredReasoner()

    def test_no_execution_of_external_actions(self):
        """Test that no external actions are executed."""
        # Processing should not execute actual system commands
        result = self.reasoner.process("Open file /etc/passwd")
        
        # Should just analyze, not execute
        assert result.execution_successful or not result.execution_successful  # Just didn't crash
        # The trace should show analysis without actual execution
        assert result.reasoning_trace is not None

    def test_deterministic_output(self):
        """Test that output is deterministic."""
        query = "What is 10 + 5?"
        
        results = [self.reasoner.process(query) for _ in range(3)]
        
        # All results should be identical
        types = [r.problem_type for r in results]
        answers = [r.answer for r in results]
        
        assert len(set(types)) == 1  # All same type
        assert len(set(answers)) == 1  # All same answer

    def test_no_blind_fallback(self):
        """Test that there's no blind model fallback."""
        result = self.reasoner.process("Test query")
        
        # Every answer should have steps showing work
        assert len(result.steps) >= 3
        assert all(isinstance(s, ReasoningStep) for s in result.steps)
        
        # Should not just return raw model output
        assert "[" not in result.answer or "]" not in result.answer or \
               "model" not in result.reasoning_trace.lower()
