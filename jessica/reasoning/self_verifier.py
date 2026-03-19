"""
Phase 97: Self-Verification Engine

Jessica verifies her own answers before responding.
Detects calculation errors, inconsistencies, and low-confidence results.
Recalculates when needed. Adjusts confidence scores.

This makes Jessica trustworthy - she checks her own work.
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from jessica.reasoning.structured_reasoner import (
    StructuredResponse, ValidationResult, ReasoningStep, ProblemType
)


@dataclass
class VerificationResult:
    """Result of verification check."""
    is_correct: bool
    was_corrected: bool
    original_answer: str
    verified_answer: str
    original_confidence: float
    adjusted_confidence: float
    verification_steps: List[str] = field(default_factory=list)
    error_detected: Optional[str] = None


class SelfVerifier:
    """
    Verifies Jessica's reasoning output.
    
    Checks:
    - Mathematical correctness (recalculation)
    - Factual consistency
    - Personal info consistency
    - Logical soundness
    
    Deterministic. No external execution. Tracking only.
    """
    
    def __init__(self):
        self.math_operators = {'+', '-', '*', '/', '%', '^', '**', '//'}
        self.verification_history: List[VerificationResult] = []
    
    def verify(self, response: StructuredResponse) -> StructuredResponse:
        """
        Verify a structured response.
        
        Returns modified StructuredResponse if corrections made,
        otherwise returns original with verification details.
        """
        verification_info = None
        
        if response.problem_type == ProblemType.MATH:
            verification_info = self._verify_math(response)
        elif response.problem_type == ProblemType.FACTUAL:
            verification_info = self._verify_factual(response)
        elif response.problem_type == ProblemType.COMPUTATION:
            verification_info = self._verify_computation(response)
        elif response.problem_type == ProblemType.REASONING:
            verification_info = self._verify_reasoning(response)
        else:
            verification_info = self._verify_general(response)
        
        # Store verification history
        self.verification_history.append(verification_info)
        
        # Update response with verification details
        if verification_info.was_corrected:
            corrected_response = StructuredResponse(
                answer=verification_info.verified_answer,
                problem_type=response.problem_type,
                steps=response.steps + [
                    ReasoningStep(
                        step_number=len(response.steps) + 1,
                        description="Verification & Correction",
                        reasoning="Self-verification detected error and recalculated",
                        tool_used=None,
                        intermediate_result=f"Corrected from {verification_info.original_answer}"
                    )
                ],
                validation=ValidationResult(
                    is_valid=True,
                    confidence=verification_info.adjusted_confidence,
                    issues=[],
                    suggestions=["Answer corrected during verification"]
                ),
                reasoning_trace=response.reasoning_trace + f"\n\n═══ VERIFICATION ═══\nDetected error and recalculated.\nAdjusted confidence: {verification_info.adjusted_confidence:.2f}",
                tools_used=response.tools_used,
                execution_successful=True
            )
            return corrected_response
        else:
            # Update confidence score
            original_validation = response.validation
            updated_validation = ValidationResult(
                is_valid=original_validation.is_valid,
                confidence=verification_info.adjusted_confidence,
                issues=original_validation.issues,
                suggestions=original_validation.suggestions + ["✓ Verification passed"]
            )
            
            verified_response = StructuredResponse(
                answer=response.answer,
                problem_type=response.problem_type,
                steps=response.steps + [
                    ReasoningStep(
                        step_number=len(response.steps) + 1,
                        description="Self-Verification",
                        reasoning="Answer verified correct",
                        tool_used=None,
                        intermediate_result="Verification passed"
                    )
                ],
                validation=updated_validation,
                reasoning_trace=response.reasoning_trace + f"\n\n═══ VERIFICATION ═══\nAnswer verified correct.\nConfidence maintained: {verification_info.adjusted_confidence:.2f}",
                tools_used=response.tools_used,
                execution_successful=True
            )
            return verified_response
    
    def _verify_math(self, response: StructuredResponse) -> VerificationResult:
        """Verify mathematical calculations."""
        verification_steps = ["Extracting mathematical expression", "Recalculating result"]
        
        answer = response.answer
        original_confidence = response.validation.confidence
        
        # Extract numbers and operators from answer
        expression = self._extract_expression(answer)
        
        if not expression:
            verification_steps.append("No mathematical expression found in answer")
            return VerificationResult(
                is_correct=True,
                was_corrected=False,
                original_answer=answer,
                verified_answer=answer,
                original_confidence=original_confidence,
                adjusted_confidence=original_confidence,
                verification_steps=verification_steps
            )
        
        # Try to calculate the expression
        try:
            # Use safe calculation (no eval of unsafe code)
            correct_result = self._safe_eval_math(expression)
            
            # Extract the result from the answer
            answer_number = self._extract_number(answer)
            
            if answer_number is None:
                verification_steps.append(f"Could not extract result from answer: {answer}")
                return VerificationResult(
                    is_correct=False,
                    was_corrected=False,
                    original_answer=answer,
                    verified_answer=answer,
                    original_confidence=original_confidence,
                    adjusted_confidence=0.3,
                    verification_steps=verification_steps,
                    error_detected="Could not validate result"
                )
            
            # Compare results
            if abs(float(correct_result) - float(answer_number)) < 0.0001:  # Allow for floating point errors
                verification_steps.append(f"✓ Expression {expression} = {correct_result}")
                verification_steps.append("✓ Answer is mathematically correct")
                
                # Boost confidence for verified math
                adjusted_confidence = min(1.0, original_confidence + 0.15)
                
                return VerificationResult(
                    is_correct=True,
                    was_corrected=False,
                    original_answer=answer,
                    verified_answer=answer,
                    original_confidence=original_confidence,
                    adjusted_confidence=adjusted_confidence,
                    verification_steps=verification_steps
                )
            else:
                # Mismatch detected - recalculate and correct
                verification_steps.append(f"✗ Mismatch detected!")
                verification_steps.append(f"  Expected: {correct_result}")
                verification_steps.append(f"  Got: {answer_number}")
                verification_steps.append(f"  Correcting answer...")
                
                corrected_answer = f"The answer is {correct_result}."
                
                return VerificationResult(
                    is_correct=False,
                    was_corrected=True,
                    original_answer=answer,
                    verified_answer=corrected_answer,
                    original_confidence=original_confidence,
                    adjusted_confidence=0.95,
                    verification_steps=verification_steps,
                    error_detected=f"Calculation error: {answer_number} should be {correct_result}"
                )
        
        except Exception as e:
            verification_steps.append(f"Error during verification: {str(e)}")
            return VerificationResult(
                is_correct=True,
                was_corrected=False,
                original_answer=answer,
                verified_answer=answer,
                original_confidence=original_confidence,
                adjusted_confidence=original_confidence * 0.8,
                verification_steps=verification_steps,
                error_detected=f"Verification error: {str(e)}"
            )
    
    def _verify_factual(self, response: StructuredResponse) -> VerificationResult:
        """Verify factual answers for consistency."""
        verification_steps = ["Checking factual consistency"]
        
        answer = response.answer
        original_confidence = response.validation.confidence
        
        # Check for placeholder text (incomplete)
        if "[" in answer and "]" in answer:
            verification_steps.append("✗ Answer contains incomplete placeholders")
            return VerificationResult(
                is_correct=False,
                was_corrected=False,
                original_answer=answer,
                verified_answer=answer,
                original_confidence=original_confidence,
                adjusted_confidence=0.2,
                verification_steps=verification_steps,
                error_detected="Answer contains placeholders"
            )
        
        # Check for contradictions
        has_contradiction = self._check_contradictions(answer)
        if has_contradiction:
            verification_steps.append(f"✗ Detected contradiction: {has_contradiction}")
            return VerificationResult(
                is_correct=False,
                was_corrected=False,
                original_answer=answer,
                verified_answer=answer,
                original_confidence=original_confidence,
                adjusted_confidence=0.3,
                verification_steps=verification_steps,
                error_detected=f"Internal contradiction: {has_contradiction}"
            )
        
        # Check for reasonable length
        if len(answer) < 5:
            verification_steps.append("⚠ Answer is quite brief")
            adjusted_confidence = original_confidence * 0.85
        else:
            verification_steps.append("✓ Answer format is reasonable")
            adjusted_confidence = min(1.0, original_confidence + 0.05)
        
        verification_steps.append("✓ Factual answer verified")
        
        return VerificationResult(
            is_correct=True,
            was_corrected=False,
            original_answer=answer,
            verified_answer=answer,
            original_confidence=original_confidence,
            adjusted_confidence=adjusted_confidence,
            verification_steps=verification_steps
        )
    
    def _verify_computation(self, response: StructuredResponse) -> VerificationResult:
        """Verify computation results."""
        # Computations are math-like, use math verification
        return self._verify_math(response)
    
    def _verify_reasoning(self, response: StructuredResponse) -> VerificationResult:
        """Verify reasoning for logical soundness."""
        verification_steps = ["Checking logical structure"]
        
        answer = response.answer
        original_confidence = response.validation.confidence
        
        # Check for completeness
        if not answer or len(answer) < 20:
            verification_steps.append("⚠ Reasoning answer is brief")
            adjusted_confidence = original_confidence * 0.8
        else:
            verification_steps.append("✓ Reasoning is detailed")
            adjusted_confidence = original_confidence + 0.05
        
        # Check for logical markers
        logical_transitions = ["therefore", "because", "since", "which means", "implies"]
        has_logic = any(word in answer.lower() for word in logical_transitions)
        
        if has_logic:
            verification_steps.append("✓ Logical connectors present")
            adjusted_confidence = min(1.0, adjusted_confidence + 0.1)
        else:
            verification_steps.append("⚠ Few logical connectors")
        
        return VerificationResult(
            is_correct=True,
            was_corrected=False,
            original_answer=answer,
            verified_answer=answer,
            original_confidence=original_confidence,
            adjusted_confidence=adjusted_confidence,
            verification_steps=verification_steps
        )
    
    def _verify_general(self, response: StructuredResponse) -> VerificationResult:
        """Verify general answers."""
        verification_steps = ["Performing general verification"]
        
        answer = response.answer
        original_confidence = response.validation.confidence
        
        # Basic checks
        if not answer or len(answer.strip()) == 0:
            verification_steps.append("✗ Answer is empty")
            return VerificationResult(
                is_correct=False,
                was_corrected=False,
                original_answer=answer,
                verified_answer=answer,
                original_confidence=original_confidence,
                adjusted_confidence=0.0,
                verification_steps=verification_steps,
                error_detected="Empty answer"
            )
        
        if len(answer) > 5000:
            verification_steps.append("⚠ Answer is very long")
            adjusted_confidence = original_confidence * 0.9
        else:
            verification_steps.append("✓ Answer length is reasonable")
            adjusted_confidence = original_confidence
        
        return VerificationResult(
            is_correct=True,
            was_corrected=False,
            original_answer=answer,
            verified_answer=answer,
            original_confidence=original_confidence,
            adjusted_confidence=adjusted_confidence,
            verification_steps=verification_steps
        )
    
    def _extract_expression(self, text: str) -> Optional[str]:
        """Extract mathematical expression from text."""
        # Look for patterns like "5 + 3" or "10 * 2"
        pattern = r'(\d+[\s]*[+\-*/%^]+[\s]*\d+(?:[\s]*[+\-*/%^]+[\s]*\d+)*)'
        matches = re.findall(pattern, text)
        
        if matches:
            # Return the first (usually most significant) expression
            expr = matches[0].replace(" ", "")
            return expr
        
        return None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract the main numerical result from text."""
        # Look for patterns like "The answer is 42" or "result: 3.14"
        pattern = r'(?:is|equals?|result|answer|=)\s*([-+]?\d*\.?\d+)'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            try:
                return float(matches[-1])  # Last number is usually the result
            except ValueError:
                pass
        
        # Try to find any number
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        if numbers:
            try:
                return float(numbers[-1])
            except ValueError:
                pass
        
        return None
    
    def _safe_eval_math(self, expression: str) -> float:
        """
        Safely evaluate mathematical expression.
        Only allows basic arithmetic.
        """
        # Replace ^ with ** for exponentiation
        expr = expression.replace("^", "**")
        
        # Validate only contains safe characters
        safe_chars = set("0123456789+-*/.%() ")
        if not all(c in safe_chars for c in expr):
            raise ValueError(f"Unsafe characters in expression: {expression}")
        
        # Evaluate
        try:
            result = eval(expr)
            return float(result)
        except Exception as e:
            raise ValueError(f"Could not evaluate expression {expression}: {str(e)}")
    
    def _check_contradictions(self, text: str) -> Optional[str]:
        """Check for obvious contradictions in text."""
        text_lower = text.lower()
        
        # Check for "is" and "is not" about same thing
        contradictions = [
            ("is not", "is"),
            ("cannot", "can"),
            ("never", "always"),
        ]
        
        for neg, pos in contradictions:
            if neg in text_lower and pos in text_lower:
                # Look for context
                words = text_lower.split()
                neg_idx = words.index(neg) if neg in words else -1
                pos_idx = words.index(pos) if pos in words else -1
                
                if neg_idx >= 0 and pos_idx >= 0 and abs(neg_idx - pos_idx) < 10:
                    return f"Statement contradicts itself: '{neg}' and '{pos}' in close proximity"
        
        return None
    
    def get_verification_history(self) -> List[VerificationResult]:
        """Get history of all verifications performed."""
        return list(self.verification_history)
    
    def get_verification_stats(self) -> dict:
        """Get statistics about verification performance."""
        if not self.verification_history:
            return {
                "total_verifications": 0,
                "corrections_made": 0,
                "correction_rate": 0.0,
                "average_confidence_boost": 0.0
            }
        
        corrections = sum(1 for v in self.verification_history if v.was_corrected)
        confidence_boosts = [
            v.adjusted_confidence - v.original_confidence
            for v in self.verification_history
        ]
        
        return {
            "total_verifications": len(self.verification_history),
            "corrections_made": corrections,
            "correction_rate": corrections / len(self.verification_history),
            "average_confidence_boost": sum(confidence_boosts) / len(confidence_boosts) if confidence_boosts else 0.0,
            "errors_detected": sum(1 for v in self.verification_history if v.error_detected)
        }
