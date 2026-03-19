from collections import defaultdict


class PatternEngine:

    def __init__(self):
        self.pattern_counts = defaultdict(int)

    def record(self, action):

        self.pattern_counts[action] += 1

    def detect(self):

        suggestions = []

        for action, count in self.pattern_counts.items():

            threshold = self.get_threshold(action)

            if count >= threshold:
                suggestions.append((action, count))

        return suggestions

    def get_threshold(self, action):

        action = action.lower()

        if "create" in action or "generate" in action:
            return 5

        if "analyze" in action:
            return 3

        if "refactor" in action:
            return 10

        return 7