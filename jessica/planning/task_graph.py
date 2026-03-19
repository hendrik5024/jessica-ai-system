class TaskNode:

    def __init__(self, name, action=None):
        self.name = name
        self.action = action
        self.dependencies = []
        self.completed = False
        self.result = None


class TaskGraph:

    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_dependency(self, node, dependency):
        node.dependencies.append(dependency)

    def ready_nodes(self):
        """
        Return nodes ready to execute.
        """
        return [
            node for node in self.nodes
            if not node.completed
            and all(dep.completed for dep in node.dependencies)
        ]

    def mark_complete(self, node, result=None):
        node.completed = True
        node.result = result

    def all_complete(self):
        return all(node.completed for node in self.nodes)