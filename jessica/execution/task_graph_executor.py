from jessica.tools.tool_manager import ToolManager


class TaskGraphExecutor:

    def __init__(self):
        self.tool_manager = ToolManager()

    def _execute_tool(self, node):
        if not node.action or node.action not in self.tool_manager.tools:
            return f"Executed step: {node.name}"

        tool = self.tool_manager.tools[node.action]

        if node.name == "create_project_directory" and node.action == "create_directory":
            return tool("generated_project")

        if node.name == "generate_main_script" and node.action == "write_file":
            return tool(
                "generated_project/main.py",
                "print(\"Hello from Jessica generated project\")",
            )

        if node.name == "create_config_file" and node.action == "write_file":
            return tool(
                "generated_project/config.json",
                """{
    \"version\": \"1.0\",
    \"created_by\": \"Jessica\"
}""",
            )

        return tool()

    def execute_graph(self, graph):

        results = []

        while not graph.all_complete():

            ready_nodes = graph.ready_nodes()

            if not ready_nodes:
                break

            for node in ready_nodes:

                try:

                    result = self._execute_tool(node)

                    graph.mark_complete(node, result)

                    results.append(
                        f"{node.name} ✓"
                    )

                except Exception as e:

                    graph.mark_complete(node, f"Error: {e}")

                    results.append(
                        f"{node.name} ✗ {e}"
                    )

        return results