class PatchQueue:

    def __init__(self):
        self.queue = []

    def add(self, patch):
        self.queue.append(patch)

    def next(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def has_items(self):
        return len(self.queue) > 0