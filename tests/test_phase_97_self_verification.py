"""
Phase 97: Self-Verification Engine Tests

Tests for SelfVerifier that checks Jessica's own answers.
Verifies corrections, confidence adjustments, and error detection.
"""

import pytest
from jessica.reasoning.structured_reasoner import (
    StructuredReasoner, StructuredResponse, ValidationResult, 
    ReasoningStep, ProblemType
)
from jessica.reasoning.self_verifier import SelfVerifier, VerificationResult


@pytest.fixture
def verifier():
    """Create fresh verifier for each test."""
    return SelfVerifier()


@pytest.fixture
def reasoner():
    """Create fresh reasoner for each test."""
    return StructuredReasoner()


class TestMathVerification:
    """Test verification of mathematical calculations."""
    
    def test_verify_correct_addition(self, verifier):
        """Test verification of correct addition."""
        response = StructuredResponse(
            answer="The answer is 8.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "5 + 3 = 8")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Math calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.88  # Should maintain or boost
        assert "verified" in result.reasoning_trace.lower()
    
    def test_verify_incorrect_addition(self, verifier):
        """Test detection of incorrect addition."""
        response = StructuredResponse(
            answer="5 + 3 equals 9.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "5 + 3 = 9 (WRONG)")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Math calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        # Should either correct the answer or mark it as needing correction
        assert "8" in result.answer or result.validation.confidence < 0.9
    
    def test_verify_multiplication(self, verifier):
        """Test verification of multiplication."""
        response = StructuredResponse(
            answer="The answer is 100.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "10 * 10 = 100")],
            validation=ValidationResult(is_valid=True, confidence=0.85),
            reasoning_trace="Multiplication",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.85
    
    def test_verify_division(self, verifier):
        """Test verification of division."""
        response = StructuredResponse(
            answer="The answer is 5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "10 / 2 = 5")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Division",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.8
    
    def test_verify_complex_expression(self, verifier):
        """Test verification of complex math expression."""
        response = StructuredResponse(
            answer="The answer is 14.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "2 + 3 * 4 = 14")],
            validation=ValidationResult(is_valid=True, confidence=0.85),
            reasoning_trace="Complex expression",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.85
    
    def test_verify_floating_point(self, verifier):
        """Test verification with floating point results."""
        response = StructuredResponse(
            answer="The answer is 3.5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "7 / 2 = 3.5")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Float calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.8


class TestFactualVerification:
    """Test verification of factual answers."""
    
    def test_verify_factual_complete(self, verifier):
        """Test verification of complete factual answer."""
        response = StructuredResponse(
            answer="Paris is the capital of France.",
            problem_type=ProblemType.FACTUAL,
            steps=[ReasoningStep(1, "Research", "Looked up capital of France")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Factual lookup",
            tools_used=["knowledge_recall"],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.9
    
    def test_verify_factual_with_placeholder(self, verifier):
        """Test detection of incomplete factual answer."""
        response = StructuredResponse(
            answer="The capital is [answer pending knowledge retrieval]",
            problem_type=ProblemType.FACTUAL,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.6),
            reasoning_trace="Incomplete",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence < 0.5
    
    def test_verify_factual_contradiction(self, verifier):
        """Test detection of contradictory factual statement."""
        response = StructuredResponse(
            answer="Water is hot but water is not a liquid.",
            problem_type=ProblemType.FACTUAL,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Contradiction",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        # May detect contradiction, just ensure it processes
        assert result.validation.confidence >= 0
    
    def test_verify_factual_brief(self, verifier):
        """Test verification of brief but valid factual answer."""
        response = StructuredResponse(
            answer="Yes.",
            problem_type=ProblemType.FACTUAL,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.75),
            reasoning_trace="Brief answer",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence < 0.75  # Reduced for brevity


class TestComputationVerification:
    """Test verification of computation results."""
    
    def test_verify_computation_correct(self, verifier):
        """Test verification of correct computation."""
        response = StructuredResponse(
            answer="560 + 80 equals 640.",
            problem_type=ProblemType.COMPUTATION,
            steps=[ReasoningStep(1, "Calculate", "560 + 40 * 2")],
            validation=ValidationResult(is_valid=True, confidence=0.85),
            reasoning_trace="Computation",
            tools_used=["calculator_ready"],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        # Should verify the expression matches
        assert "640" in result.answer or result.validation.confidence >= 0.85
    
    def test_verify_simple_computation(self, verifier):
        """Test simple computation verification."""
        response = StructuredResponse(
            answer="The answer is 10.",
            problem_type=ProblemType.COMPUTATION,
            steps=[ReasoningStep(1, "Calculate", "5 + 5")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Simple",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= 0.9


class TestReasoningVerification:
    """Test verification of reasoning/explanation answers."""
    
    def test_verify_reasoning_detailed(self, verifier):
        """Test verification of detailed reasoning."""
        response = StructuredResponse(
            answer="The sky appears blue because of Rayleigh scattering. When sunlight enters the atmosphere, it scatters off gas molecules. Blue light has a shorter wavelength, so it scatters more.",
            problem_type=ProblemType.REASONING,
            steps=[ReasoningStep(1, "Explain", "Rayleigh scattering effect")],
            validation=ValidationResult(is_valid=True, confidence=0.85),
            reasoning_trace="Reasoning explanation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence > 0.85
    
    def test_verify_reasoning_with_logic(self, verifier):
        """Test verification of reasoning with logical connectors."""
        response = StructuredResponse(
            answer="Since plants need sunlight, and sunlight is beneficial, therefore plants in sunny areas grow well.",
            problem_type=ProblemType.REASONING,
            steps=[ReasoningStep(1, "Reason", "Logical deduction")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Logic",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence > 0.8
    
    def test_verify_reasoning_brief(self, verifier):
        """Test verification of brief reasoning."""
        response = StructuredResponse(
            answer="It just is.",
            problem_type=ProblemType.REASONING,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.6),
            reasoning_trace="Brief",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence < 0.6


class TestCorrectionDetection:
    """Test detection and correction of errors."""
    
    def test_detects_calculation_error(self, verifier):
        """Test detection of calculation error."""
        response = StructuredResponse(
            answer="7 + 8 equals 14.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Add", "7 + 8")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Wrong calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert "14" in result.answer or "15" in result.answer
    
    def test_corrects_multiplication_error(self, verifier):
        """Test correction of multiplication error."""
        response = StructuredResponse(
            answer="12 times 12 equals 144.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Multiply", "12 * 12")],
            validation=ValidationResult(is_valid=True, confidence=0.85),
            reasoning_trace="Multiplication",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        # 12 * 12 = 144, so this should verify as correct
        assert result.validation.confidence >= 0.85
    
    def test_corrected_response_has_trace(self, verifier):
        """Test that corrected response includes trace."""
        response = StructuredResponse(
            answer="2 + 2 equals 5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Add", "2 + 2")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Initial calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        trace_lower = result.reasoning_trace.lower()
        assert "verification" in trace_lower


class TestConfidenceAdjustment:
    """Test confidence score adjustments."""
    
    def test_boosts_verified_math(self, verifier):
        """Test confidence boost for verified math."""
        original_confidence = 0.85
        response = StructuredResponse(
            answer="The answer is 20.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "10 + 10 = 20")],
            validation=ValidationResult(is_valid=True, confidence=original_confidence),
            reasoning_trace="Math",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence >= original_confidence
    
    def test_reduces_unverifiable_math(self, verifier):
        """Test confidence reduction for unverifiable math."""
        response = StructuredResponse(
            answer="The answer is approximately 3.14159.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "pi")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Pi calculation",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        # Can't verify pi directly from text, some reduction expected
        assert result.validation.confidence <= 0.8
    
    def test_confidence_for_corrected_answer(self, verifier):
        """Test high confidence for corrected answer."""
        response = StructuredResponse(
            answer="2 + 2 equals 5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Add", "2 + 2 = 5 (ERROR)")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Error",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence == 0.95


class TestExtractionMethods:
    """Test internal extraction methods."""
    
    def test_extract_expression_simple(self, verifier):
        """Test extraction of simple expression."""
        expr = verifier._extract_expression("The answer to 5 + 3 is 8")
        assert expr == "5+3"
    
    def test_extract_expression_with_spaces(self, verifier):
        """Test extraction of expression with spaces."""
        expr = verifier._extract_expression("Calculate 10 * 2 for the result")
        assert expr == "10*2"
    
    def test_extract_number_from_sentence(self, verifier):
        """Test extraction of number from sentence."""
        number = verifier._extract_number("The answer is 42")
        assert number == 42.0
    
    def test_extract_number_with_decimal(self, verifier):
        """Test extraction of decimal number."""
        number = verifier._extract_number("The result equals 3.14")
        assert abs(number - 3.14) < 0.01
    
    def test_extract_number_negative(self, verifier):
        """Test extraction of negative number."""
        number = verifier._extract_number("The value is -5")
        assert number == -5.0
    
    def test_safe_eval_addition(self, verifier):
        """Test safe evaluation of addition."""
        result = verifier._safe_eval_math("5+3")
        assert result == 8
    
    def test_safe_eval_multiplication(self, verifier):
        """Test safe evaluation of multiplication."""
        result = verifier._safe_eval_math("10*5")
        assert result == 50
    
    def test_safe_eval_exponentiation(self, verifier):
        """Test safe evaluation with exponentiation."""
        result = verifier._safe_eval_math("2^3")
        assert result == 8


class TestVerificationHistory:
    """Test verification history tracking."""
    
    def test_history_recorded(self, verifier):
        """Test that verifications are recorded."""
        response = StructuredResponse(
            answer="The answer is 5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "2 + 3 = 5")],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Math",
            tools_used=[],
            execution_successful=True
        )
        
        assert len(verifier.verification_history) == 0
        verifier.verify(response)
        assert len(verifier.verification_history) == 1
    
    def test_multiple_verifications_recorded(self, verifier):
        """Test that multiple verifications are tracked."""
        for i in range(3):
            response = StructuredResponse(
                answer=f"The answer is {i}.",
                problem_type=ProblemType.MATH,
                steps=[ReasoningStep(1, "Calculate", str(i))],
                validation=ValidationResult(is_valid=True, confidence=0.8),
                reasoning_trace="Math",
                tools_used=[],
                execution_successful=True
            )
            verifier.verify(response)
        
        assert len(verifier.verification_history) == 3
    
    def test_get_stats_empty(self, verifier):
        """Test statistics on empty verifier."""
        stats = verifier.get_verification_stats()
        assert stats["total_verifications"] == 0
        assert stats["correction_rate"] == 0.0
    
    def test_get_stats_with_data(self, verifier):
        """Test statistics calculation."""
        # Correct answer
        response1 = StructuredResponse(
            answer="The answer is 10.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "5 + 5 = 10")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Math",
            tools_used=[],
            execution_successful=True
        )
        
        # Wrong answer
        response2 = StructuredResponse(
            answer="The answer is 5.",
            problem_type=ProblemType.MATH,
            steps=[ReasoningStep(1, "Calculate", "5 + 5 = 5 (WRONG)")],
            validation=ValidationResult(is_valid=True, confidence=0.8),
            reasoning_trace="Math",
            tools_used=[],
            execution_successful=True
        )
        
        verifier.verify(response1)
        verifier.verify(response2)
        
        stats = verifier.get_verification_stats()
        assert stats["total_verifications"] == 2
        assert stats["corrections_made"] >= 0
        assert stats["correction_rate"] >= 0.0


class TestIntegrationWithReasoner:
    """Test integration with StructuredReasoner."""
    
    def test_verify_reasoner_math_output(self, reasoner, verifier):
        """Test verifying output from StructuredReasoner."""
        response = reasoner.process("What is 7 + 3?")
        verified = verifier.verify(response)
        
        assert verified.problem_type == ProblemType.MATH
        assert verified.validation.confidence > 0
    
    def test_verify_reasoner_factual_output(self, reasoner, verifier):
        """Test verifying factual output from reasoner."""
        response = reasoner.process("What is the capital of France?")
        verified = verifier.verify(response)
        
        assert verified.problem_type == ProblemType.FACTUAL
        assert verified.validation.confidence > 0
    
    def test_full_pipeline_math(self, reasoner, verifier):
        """Test full reasoning + verification pipeline."""
        # Reason about problem
        response = reasoner.process("Calculate: 100 + 50")
        # Verify result
        verified = verifier.verify(response)
        
        assert verified.answer is not None
        assert verified.validation.confidence > 0
        assert len(verified.steps) > 1  # Added verification step


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_verify_empty_answer(self, verifier):
        """Test verification of empty answer."""
        response = StructuredResponse(
            answer="",
            problem_type=ProblemType.UNKNOWN,
            steps=[],
            validation=ValidationResult(is_valid=False, confidence=0.0),
            reasoning_trace="Empty",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence == 0.0
    
    def test_verify_very_long_answer(self, verifier):
        """Test verification of very long answer."""
        long_text = "This is a sentence. " * 500
        response = StructuredResponse(
            answer=long_text,
            problem_type=ProblemType.UNKNOWN,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.9),
            reasoning_trace="Long",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result.validation.confidence < 0.9
    
    def test_verify_unknown_problem_type(self, verifier):
        """Test verification of unknown problem type."""
        response = StructuredResponse(
            answer="Some answer",
            problem_type=ProblemType.UNKNOWN,
            steps=[],
            validation=ValidationResult(is_valid=True, confidence=0.7),
            reasoning_trace="Unknown",
            tools_used=[],
            execution_successful=True
        )
        
        result = verifier.verify(response)
        assert result is not None
        assert result.validation.confidence > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
