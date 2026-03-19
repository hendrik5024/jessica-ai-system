class ToolAdvisor:

    def __init__(self):
        self.pending_tool = None

    def create_suggestion(self, insight):
        insight_text = (insight or "")
        lowered = insight_text.lower()

        if "csv" in lowered or "data analysis" in lowered:
            self.pending_tool = {
                "tool_name": "csv_analysis_tool",
                "description": "Analyze CSV data files",
                "intent": "ANALYZE_DATA"
            }

        elif "python projects" in lowered:
            self.pending_tool = {
                "tool_name": "project_generator",
                "description": "Generate Python project templates",
                "intent": "CREATE_PROJECT"
            }

        else:
            return None

        return (
            f"Insight:\n{insight_text}\n\n"
            f"Would you like me to generate {self.pending_tool['tool_name']}?"
        )

    def approve_tool(self):
        tool = self.pending_tool
        self.pending_tool = None
        return tool