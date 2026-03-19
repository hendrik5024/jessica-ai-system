class CriticAgent:
    def __init__(self):
        self.name = "Critic"
        self.memory = {}
        self.actions = []
        self.rewards = []
        self.state = None

    def initialize(self, state):
        self.state = state
        self.memory[state] = 0
        self.actions.append(None)
        self.rewards.append(0)

    def execute(self, action):
        self.actions.append(action)
        self.rewards.append(0)
        self.state = self.transition(self.state, action)
        self.memory[self.state] = self.memory[self.state] + 1

    def report(self):
        return self.actions, self.rewards

    def transition(self, state, action):
        if action == "up":
            return state + 1
        elif action == "down":
            return state - 1
        else:
            return state
