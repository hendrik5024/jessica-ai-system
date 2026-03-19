class CognitiveScheduler:

    def __init__(self, router):
        self.router = router

    def schedule(self, task):

        if task["type"] == "user_query":
            return self.router.route("conversation_agent", task)

        elif task["type"] == "engineering":
            return self.router.route("agent_generator", task)

        elif task["type"] == "analysis":
            return self.router.route("critic_agent", task)

        else:
            return {"status": "unknown task"}
