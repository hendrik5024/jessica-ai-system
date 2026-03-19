class TaskPlanner:

    def __init__(self):
        pass

    def create_plan(self, request):

        text = request.lower()

        plan = []

        if "build" in text or "create" in text:

            plan = [
                "analyze_environment",
                "design_architecture",
                "generate_code",
                "install_dependencies",
                "run_project",
                "debug_errors"
            ]

        elif "analyze" in text:

            plan = [
                "scan_project",
                "analyze_structure",
                "report_findings"
            ]

        elif "debug" in text:

            plan = [
                "detect_errors",
                "trace_dependencies",
                "suggest_fixes"
            ]

        else:

            plan = ["general_reasoning"]

        return plan
