from jessica.planning.task_graph import TaskGraph, TaskNode


def build_python_project_graph():

    graph = TaskGraph()

    step1 = TaskNode(
        "create_project_directory",
        action="create_directory"
    )

    step2 = TaskNode(
        "generate_main_script",
        action="write_file"
    )

    step3 = TaskNode(
        "create_config_file",
        action="write_file"
    )

    graph.add_node(step1)
    graph.add_node(step2)
    graph.add_node(step3)

    graph.add_dependency(step2, step1)
    graph.add_dependency(step3, step1)

    return graph


def create_plan(user_input):
    """
    Basic task planning engine.
    Converts goals into step-by-step plans.
    """

    text = user_input.lower()

    if "create tool" in text:

        return [
            "Generate new tool",
            "Register tool",
            "Report results"
        ]

    if "python project" in text:
        return build_python_project_graph()

    if "analyze report" in text:

        return [
            "Load report data",
            "Extract key metrics",
            "Perform analysis",
            "Generate summary"
        ]

    return None
