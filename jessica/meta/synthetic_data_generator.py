"""
Synthetic Data Generator for Autodidactic Loop

Generates training data for skills that need improvement.
"""

import os
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime


class SyntheticDataGenerator:
    """
    Generates synthetic training data for weak skills.
    
    Usage:
        gen = SyntheticDataGenerator()
        
        # Generate training data for a skill
        data = gen.generate_training_data(
            skill="programming",
            failure_patterns={...},
            target_count=50
        )
        
        # Export to JSONL for fine-tuning
        gen.export_to_jsonl(data, "training_data.jsonl")
    """
    
    def __init__(self, templates_dir: str = "datasets/autodidactic"):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """Load skill-specific templates."""
        # Default templates for common skills
        return {
            "programming": [
                {
                    "pattern": "syntax_error",
                    "prompt": "Write a Python function that {task}",
                    "completion": "```python\n{code}\n```\n\nThis function {explanation}",
                    "tasks": [
                        "calculates the sum of a list",
                        "finds the maximum element in an array",
                        "reverses a string",
                        "checks if a number is prime",
                        "implements binary search"
                    ]
                },
                {
                    "pattern": "logic_error",
                    "prompt": "Fix the bug in this code:\n```python\n{buggy_code}\n```",
                    "completion": "The bug is {bug_explanation}. Here's the corrected code:\n```python\n{fixed_code}\n```"
                }
            ],
            "advice": [
                {
                    "pattern": "low_quality",
                    "prompt": "I'm feeling {emotion} because {reason}. What should I do?",
                    "completion": "I understand you're feeling {emotion}. {empathy_response}\n\n{structured_advice}",
                    "emotions": ["stressed", "anxious", "overwhelmed", "frustrated", "stuck"],
                    "reasons": [
                        "I have too much work",
                        "I'm not making progress",
                        "I don't know where to start",
                        "nothing is working out"
                    ]
                }
            ],
            "chess": [
                {
                    "pattern": "illegal_move",
                    "prompt": "What's the best move in this position? FEN: {fen}",
                    "completion": "The best move is {move} because {reasoning}."
                }
            ],
            "math": [
                {
                    "pattern": "calculation_error",
                    "prompt": "Solve: {problem}",
                    "completion": "Step 1: {step1}\nStep 2: {step2}\nAnswer: {answer}"
                }
            ]
        }
    
    def generate_training_data(self, skill: str, 
                              failure_patterns: Dict[str, Any],
                              target_count: int = 50) -> List[Dict[str, str]]:
        """
        Generate synthetic training data for a skill.
        
        Args:
            skill: Skill to generate data for
            failure_patterns: Output from FailureTracker.get_failure_patterns()
            target_count: How many examples to generate
            
        Returns:
            List of {"prompt": str, "completion": str} dicts
        """
        if skill not in self.templates:
            return self._generate_generic_data(skill, failure_patterns, target_count)
        
        templates = self.templates[skill]
        common_errors = [cat for cat, _ in failure_patterns.get("common_errors", [])]
        
        # Filter templates by common error patterns
        relevant_templates = [
            t for t in templates
            if t.get("pattern") in common_errors or not common_errors
        ]
        
        if not relevant_templates:
            relevant_templates = templates
        
        # Generate examples
        examples = []
        for i in range(target_count):
            template = random.choice(relevant_templates)
            example = self._instantiate_template(skill, template)
            if example:
                examples.append(example)
        
        return examples
    
    def _instantiate_template(self, skill: str, template: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Create a concrete example from a template."""
        try:
            if skill == "programming":
                return self._instantiate_programming_template(template)
            elif skill == "advice":
                return self._instantiate_advice_template(template)
            elif skill == "chess":
                return self._instantiate_chess_template(template)
            elif skill == "math":
                return self._instantiate_math_template(template)
            else:
                return None
        except Exception as e:
            print(f"Warning: Could not instantiate template: {e}")
            return None
    
    def _instantiate_programming_template(self, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate programming example."""
        pattern = template.get("pattern")
        
        if pattern == "syntax_error":
            task = random.choice(template.get("tasks", ["processes data"]))
            
            # Generate simple code based on task
            if "sum" in task:
                code = "def calculate_sum(numbers):\n    return sum(numbers)"
                explanation = "takes a list and returns the sum using Python's built-in sum() function"
            elif "maximum" in task:
                code = "def find_maximum(arr):\n    return max(arr)"
                explanation = "finds the largest element using max()"
            elif "reverse" in task:
                code = "def reverse_string(s):\n    return s[::-1]"
                explanation = "reverses the string using slicing"
            elif "prime" in task:
                code = "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True"
                explanation = "checks divisibility up to the square root of n"
            else:
                code = "def process_data(data):\n    return data"
                explanation = "processes the input data"
            
            prompt = template["prompt"].format(task=task)
            completion = template["completion"].format(code=code, explanation=explanation)
            
            return {"prompt": prompt, "completion": completion}
        
        return None
    
    def _instantiate_advice_template(self, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate advice example."""
        emotion = random.choice(template.get("emotions", ["stressed"]))
        reason = random.choice(template.get("reasons", ["I have challenges"]))
        
        empathy_responses = [
            "It's completely normal to feel this way when facing challenges.",
            "I hear you, and it's understandable to have these feelings.",
            "That sounds really difficult. Let's work through this together."
        ]
        
        advice_templates = [
            "Here are three steps to help:\n1. Break down the problem into smaller parts\n2. Prioritize what's most important\n3. Take action on one small thing today",
            "Let's use the Eisenhower Matrix to organize your priorities:\n- Urgent & Important: Do first\n- Important but not urgent: Schedule\n- Urgent but not important: Delegate\n- Neither: Eliminate",
            "Try this 5-minute breathing exercise:\n1. Breathe in for 4 counts\n2. Hold for 4 counts\n3. Breathe out for 6 counts\n4. Repeat 5 times\n\nThen, write down three specific actions you can take."
        ]
        
        prompt = template["prompt"].format(emotion=emotion, reason=reason)
        completion = template["completion"].format(
            emotion=emotion,
            empathy_response=random.choice(empathy_responses),
            structured_advice=random.choice(advice_templates)
        )
        
        return {"prompt": prompt, "completion": completion}
    
    def _instantiate_chess_template(self, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate chess example."""
        # Use starting position for simplicity
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        move = "e4"
        reasoning = "it controls the center and opens lines for the bishop and queen"
        
        prompt = template["prompt"].format(fen=fen)
        completion = template["completion"].format(move=move, reasoning=reasoning)
        
        return {"prompt": prompt, "completion": completion}
    
    def _instantiate_math_template(self, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate math example."""
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        problem = f"{a} + {b}"
        answer = a + b
        
        prompt = template["prompt"].format(problem=problem)
        completion = template["completion"].format(
            step1=f"Add the ones place: {a%10} + {b%10} = {(a%10)+(b%10)}",
            step2=f"Add the tens place: {a//10} + {b//10} = {(a//10)+(b//10)}",
            answer=answer
        )
        
        return {"prompt": prompt, "completion": completion}
    
    def _generate_generic_data(self, skill: str, failure_patterns: Dict[str, Any],
                               target_count: int) -> List[Dict[str, str]]:
        """Generate generic training data when no templates exist."""
        examples = []
        
        # Extract example failures
        example_failures = failure_patterns.get("example_failures", [])
        
        for i in range(min(target_count, len(example_failures))):
            failure = example_failures[i]
            context = failure.get("context", {})
            
            # Use the failed query as a prompt
            prompt = context.get("query", f"Example task for {skill}")
            
            # Generate a correction instruction
            completion = f"[This is a synthetic example for {skill} improvement]\n\nTo handle this correctly, I should:\n1. Analyze the request carefully\n2. Apply {skill} best practices\n3. Provide a clear, accurate response"
            
            examples.append({"prompt": prompt, "completion": completion})
        
        # Fill remaining with generic examples
        while len(examples) < target_count:
            examples.append({
                "prompt": f"Generic {skill} task {len(examples)}",
                "completion": f"Generic {skill} response {len(examples)}"
            })
        
        return examples
    
    def export_to_jsonl(self, examples: List[Dict[str, str]], output_path: str) -> None:
        """
        Export training data to JSONL format for fine-tuning.
        
        Args:
            examples: List of {"prompt": str, "completion": str}
            output_path: Where to save the JSONL file
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                # Format as conversational exchange
                entry = {
                    "messages": [
                        {"role": "user", "content": example["prompt"]},
                        {"role": "assistant", "content": example["completion"]}
                    ]
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def export_to_csv(self, examples: List[Dict[str, str]], output_path: str) -> None:
        """
        Export training data to CSV format.
        
        Args:
            examples: List of {"prompt": str, "completion": str}
            output_path: Where to save the CSV file
        """
        import csv
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["prompt", "completion"])
            writer.writeheader()
            writer.writerows(examples)
    
    def augment_with_variations(self, examples: List[Dict[str, str]],
                                variations: int = 3) -> List[Dict[str, str]]:
        """
        Create variations of existing examples.
        
        Args:
            examples: Original examples
            variations: How many variations per example
            
        Returns:
            Original + augmented examples
        """
        augmented = list(examples)  # Copy originals
        
        for example in examples:
            for _ in range(variations):
                # Simple augmentation: rephrase prompt slightly
                varied = {
                    "prompt": self._vary_text(example["prompt"]),
                    "completion": example["completion"]
                }
                augmented.append(varied)
        
        return augmented
    
    def _vary_text(self, text: str) -> str:
        """Create a slight variation of text."""
        # Simple variations: add/remove filler words
        variations = [
            ("Write", random.choice(["Create", "Write", "Implement"])),
            ("Find", random.choice(["Find", "Locate", "Get"])),
            ("please", ""),
            ("could you", ""),
            ("Can you", "")
        ]
        
        result = text
        for old, new in variations:
            if old in result:
                result = result.replace(old, new, 1)
        
        return result.strip()
    
    def get_stats(self, examples: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get statistics about generated data."""
        if not examples:
            return {"count": 0}
        
        prompt_lengths = [len(e["prompt"]) for e in examples]
        completion_lengths = [len(e["completion"]) for e in examples]
        
        return {
            "count": len(examples),
            "avg_prompt_length": sum(prompt_lengths) / len(prompt_lengths),
            "avg_completion_length": sum(completion_lengths) / len(completion_lengths),
            "total_tokens_estimate": sum(prompt_lengths + completion_lengths) // 4  # ~4 chars per token
        }
