import unittest

from jessica.core.cognitive_kernel import CognitiveKernel
from jessica.memory.conversation_memory import ConversationMemory


class TestConversationMemoryUnit(unittest.TestCase):
    def test_add_and_retrieve_turns(self):
        memory = ConversationMemory(max_turns=3)
        memory.add_turn("Hi", "Hello")
        memory.add_turn("How are you?", "I am good")

        recent = memory.get_recent()
        self.assertEqual(len(recent), 2)
        self.assertEqual(memory.get_last_user_input(), "How are you?")
        self.assertEqual(memory.get_last_response(), "I am good")

    def test_max_turns_limit(self):
        memory = ConversationMemory(max_turns=2)
        memory.add_turn("u1", "j1")
        memory.add_turn("u2", "j2")
        memory.add_turn("u3", "j3")

        recent = memory.get_recent()
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0].user, "u2")
        self.assertEqual(recent[1].user, "u3")


class TestPhase102KernelConversationFlow(unittest.TestCase):
    def setUp(self):
        self.kernel = CognitiveKernel()

    def test_process_updates_working_memory(self):
        response = self.kernel.process("My favorite color is blue")

        self.assertIn("favorite color", response.lower())
        self.assertEqual(self.kernel.conversation_memory.get_last_user_input(), "My favorite color is blue")
        self.assertEqual(self.kernel.conversation_memory.get_last_response(), response)

    def test_incorrect_response_uses_last_response_context(self):
        self.kernel.process("My favorite color is blue")
        response = self.kernel.process("That is incorrect")

        self.assertEqual(
            response,
            "I understand that my previous answer may be incorrect. Let me review it.",
        )

    def test_identity_continuity_name(self):
        self.kernel.memory_beliefs.set("user_name", "Hendrik")
        response = self.kernel.process("What is my name?")

        self.assertEqual(response, "Your name is Hendrik.")

    def test_identity_continuity_favorite_color(self):
        self.kernel.memory_beliefs.set_fact("favorite_color", "blue")
        response = self.kernel.process("What is my favorite color?")

        self.assertEqual(response, "Your favorite color is blue.")

    def test_identity_continuity_creator(self):
        self.kernel.memory_beliefs.set("creator", "Hendrik")
        response = self.kernel.process("Who created you?")

        self.assertIn("Hendrik", response)
        self.assertIn("created", response.lower())

    def test_follow_up_that_uses_previous_user_input(self):
        self.kernel.memory_beliefs.set_fact("favorite_color", "blue")
        self.kernel.process("What is my favorite color?")

        response = self.kernel.process("What about that?")
        self.assertIn("favorite color", response.lower())


if __name__ == "__main__":
    unittest.main()
