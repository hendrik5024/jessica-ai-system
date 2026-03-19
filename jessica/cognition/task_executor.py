from jessica.cognition.code_generator import generate_tool
from jessica.tools.load_generated_tools import load_generated_tools
from jessica.tools.tool_manager import execute_tool


def execute_plan(plan, user_input):

    results = []

    for step in plan:

        if step == "Create project directory":
            results.append(execute_tool("create_directory", "generated_project"))

        elif step == "Generate main Python script":

            path = "generated_project/main.py"

            code = """print("Hello from Jessica generated project")"""
            results.append(execute_tool("write_file", path, code))

        elif step == "Add configuration file":

            path = "generated_project/config.json"

            config = """{
    "version": "1.0",
    "created_by": "Jessica"
}"""
            results.append(execute_tool("write_file", path, config))

        elif step == "Test script execution":

            results.append("Execution test placeholder.")

        elif step == "Report results":

            results.append("Project generation complete.")

        elif step == "Generate new tool":

            tool_name, filename = generate_tool(user_input)

            results.append(f"Tool created: {filename}")

            load_generated_tools()

            results.append(f"Generated tool loaded: {tool_name}")

        elif step == "Register tool":

            load_generated_tools()
            results.append("Generated tools registered.")

        else:

            results.append(f"Step skipped: {step}")

    return results
