from jessica.gui.console_manager import ConsoleManager


class ActivityStream:
    """
    Transforms technical logs into natural narrative activity stream.
    Makes Jessica's operations feel intentional and thoughtful.
    """

    def thinking(self, message):
        """Log a thinking/analysis step."""
        ConsoleManager.log(f"Jessica is thinking: {message}")

    def action(self, message):
        """Log an action being taken."""
        ConsoleManager.log(f"Jessica is {message}...")

    def result(self, message):
        """Log a result completion."""
        ConsoleManager.log(f"Jessica finished: {message}")

    def found_workflow(self):
        """Special message for workflow discovery."""
        ConsoleManager.log("Jessica found a known workflow for this task.")

    def executing_plan(self):
        """Special message for plan execution."""
        ConsoleManager.log("Jessica is creating a new plan for this task.")

    def analyzing_request(self):
        """Special message for request analysis."""
        ConsoleManager.log("Jessica is analyzing your request...")
