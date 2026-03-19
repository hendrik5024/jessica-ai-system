import unittest
from datetime import datetime

from jessica.core.cognitive_kernel import CognitiveKernel


class TestPhase101KernelControls(unittest.TestCase):
    def setUp(self):
        self.kernel = CognitiveKernel()

    def test_split_questions(self):
        text = "What is my favorite color and what city do I live in?"
        parts = self.kernel._split_questions(text)
        self.assertEqual(parts, ["What is my favorite color", "what city do I live in"])

    def test_convert_model_to_jessica_blocks_identity_leaks(self):
        model_answer = "As an AI language model, I was trained by engineers."
        safe = self.kernel._convert_model_to_jessica(model_answer)
        self.assertEqual(safe, "I do not have enough information to answer that yet.")

    def test_convert_model_to_jessica_cleans_prefix(self):
        model_answer = "Assistant: The result is 42."
        safe = self.kernel._convert_model_to_jessica(model_answer)
        self.assertEqual(safe, "The result is 42.")

    def test_hypothetical_age_from_text(self):
        expected = datetime.now().year - 1975
        age = self.kernel._calculate_age_from_text("if i were born in 1975")
        self.assertEqual(age, expected)

    def test_process_hypothetical_age_response(self):
        expected = datetime.now().year - 1975
        response = self.kernel.process("If I were born in 1975, how old would I be?")
        self.assertEqual(response, f"You would be {expected} years old.")

    def test_process_multi_question_combines_responses(self):
        response = self.kernel.process("My favorite color is blue and I live in Cape Town?")
        self.assertIn("I will remember that your favorite color is blue.", response)
        self.assertIn("I will remember that you live in Cape Town.", response)

    def test_identity_block_before_model_fallback(self):
        self.kernel.memory_beliefs.set("creator", "Hendrik")
        response = self.kernel.process("Who created you?")
        self.assertIn("Hendrik", response)
        self.assertIn("created", response.lower())


if __name__ == "__main__":
    unittest.main()
