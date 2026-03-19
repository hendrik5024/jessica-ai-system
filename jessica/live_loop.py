"""
Phase 9.2 — Live Conversational Loop

Runs Jessica in an interactive terminal session.
Human input → CognitiveKernel → response
"""

from jessica.core.cognitive_kernel import CognitiveKernel
from jessica.llm.llm_interface import LLMInterface


class JessicaLiveLoop:
    def __init__(self):
        self.llm = LLMInterface()
        self.kernel = CognitiveKernel(llm=self.llm)

    def run(self):
        print("Jessica is online. Type 'exit' to stop.")

        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ("exit", "quit"):
                print("Jessica: Shutting down.")
                break

            result = self.kernel.process(user_input)

            # Phase 92: Handle proposals
            if isinstance(result, dict) and result.get("type") == "proposal":
                print("\n⚠️ Jessica proposes an action:")
                print("Description:", result["description"])
                print("Reasoning:", result["reasoning"])
                print("Risk:", result["risk"])
                print("Actions:", result["actions"])

                decision = input("\nApprove? (yes/no): ")

                if decision.lower() == "yes":
                    proposal_id = result["proposal_id"]

                    proposal = self.kernel.autonomy.memory.get(proposal_id)

                    # Phase 93: Pass original user_input for context
                    execution_result = self.kernel.execute_proposal(proposal, user_input)

                    print("\n✅ Execution result:")
                    for r in execution_result:
                        print("-", r)

                else:
                    print("❌ Rejected")

                continue

            print("Jessica:", result)
