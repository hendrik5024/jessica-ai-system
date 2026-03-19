from intent_router import route_intent


class CognitivePipeline:

    def __init__(self, core):
        self.core = core

    def process(self, user_input):
        """
        Central cognitive pipeline: unified entry point for all requests.
        
        Flow:
        1. Intent detection
        2. Identity/safety checks
        3. Knowledge memory retrieval
        4. Workflow memory check
        5. Planning layer
        6. Model fallback
        """

        # Step 1 — Detect intent
        intent = route_intent(user_input)

        # Step 2 — Check identity rules (quick guards)
        identity_response = self.core.response_router.route_identity_layer(user_input.lower())
        if identity_response:
            return identity_response

        # Step 3 — Check knowledge memory for personal facts
        lowered = user_input.lower()
        if "where was i born" in lowered:
            birthplace = self.core.knowledge_memory.get_fact("birthplace")
            if birthplace:
                return f"You were born in {birthplace}."

        if "how old am i" in lowered:
            birth_year = self.core.knowledge_memory.get_fact("birth_year")
            if birth_year:
                from datetime import datetime
                age = datetime.now().year - int(birth_year)
                return f"You are {age} years old."

        # Step 4 — Check episodic memory for past conversations
        if any(word in lowered for word in ["earlier", "previous", "remember", "we talked"]):
            results = self.core.episodic_memory.search(user_input)
            if results:
                summary = "Earlier discussion:\n\n"
                for memory in results:
                    summary += f"You: {memory['user_input']}\n"
                    summary += f"Jessica: {memory['response']}\n\n"
                return summary

        # Step 5 — Check workflow memory for learned workflows
        workflow = self.core.workflow_memory.get_workflow(intent)
        if workflow:
            optimized = self.core.workflow_optimizer.optimize(workflow)
            self.core.workflow_memory.store_workflow(intent, optimized)
            return self.core.execute_workflow(optimized, intent)

        # Step 6 — Planning & execution fallback
        from jessica.cognition.task_planner import create_plan
        plan = create_plan(user_input)
        if plan:
            return self.core.execute_plan(plan, intent)

        # Step 7 — Model fallback for open-ended queries
        return None  # Signals to caller to invoke model layer
