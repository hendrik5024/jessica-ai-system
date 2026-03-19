import asyncio

from config import load_settings
from jessica.cognition.task_planner import create_plan
from jessica.core.jessica_core import JessicaCore
from jessica.execution.task_graph_executor import TaskGraphExecutor
from jessica.planning.task_graph import TaskGraph, TaskNode
from logger import get_internal_logger


def test_python_project_plan_returns_task_graph():
    plan = create_plan("Create a Python project")

    assert isinstance(plan, TaskGraph)
    assert len(plan.nodes) == 3


def test_task_graph_executor_dependency_order():
    graph = TaskGraph()

    first = TaskNode("first")
    second = TaskNode("second")

    graph.add_node(first)
    graph.add_node(second)
    graph.add_dependency(second, first)

    executor = TaskGraphExecutor()
    results = executor.execute_graph(graph)

    assert results[0].startswith("first")
    assert results[1].startswith("second")
    assert graph.all_complete()


def test_core_create_python_project_uses_task_graph_execution():
    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    response = asyncio.run(core.handle_input("Create a Python project"))

    assert "Task Graph Execution:" in response
    assert "create_project_directory ✓" in response
    assert "generate_main_script ✓" in response
    assert "create_config_file ✓" in response
