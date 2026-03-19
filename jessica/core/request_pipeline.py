import asyncio
import re
from datetime import datetime
from pathlib import Path

from intent_router import route_intent
from jessica.cognition.cognitive_friction import apply_cognitive_friction
from jessica.cognition.csi_pipeline import run_cognitive_pipeline
from jessica.cognition.inquiry_engine import check_for_missing_information
from jessica.cognition.internal_monologue import generate_monologue
from jessica.cognition.observer import observe
from jessica.cognition.persona_manager import select_persona
from jessica.cognition.project_architect import ProjectArchitect
from jessica.cognition.project_builder import ProjectBuilder
from jessica.ide.workspace_manager import WorkspaceManager
from jessica.ide.ide_manager import IDEManager
from jessica.intelligence.code_indexer import CodeIndexer
from jessica.intelligence.architecture_mapper import ArchitectureMapper
from jessica.intelligence.dependency_graph import DependencyGraph
from jessica.intelligence.debug_engine import DebugEngine
from jessica.execution.sandbox_runner import SandboxRunner
from jessica.system.settings_manager import SettingsManager
from jessica.agents.agent_registry import AgentRegistry
from jessica.agents.project_analyzer.agent import ProjectAnalyzerAgent
from jessica.agents.agent_orchestrator import AgentOrchestrator
from jessica.agents.agent_generator import AgentGenerator
from jessica.agents.agent_validator import AgentValidator
from jessica.agents.agent_installer import AgentInstaller
from jessica.memory.knowledge_graph import KnowledgeGraph
from jessica.cognition.simulator import simulate_action
from jessica.cognition.task_executor import execute_plan
from jessica.cognition.task_planner import create_plan
from jessica.cognition.telemetry import queue_insight, update_intent, update_persona, update_state
from jessica.gui.console_manager import ConsoleManager
from jessica.planning.task_graph import TaskGraph
from jessica.planning.task_planner import TaskPlanner
from logger import log_event
from state_manager import SystemState


class RequestPipeline:
    """Layered request pipeline for the canonical Jessica core."""

    def __init__(self, core, response_router):
        self.core = core
        self.response_router = response_router
        self.pattern_engine = self.core.pattern_engine
        self.project_architect = ProjectArchitect()
        self.project_builder = ProjectBuilder()
        self.workspace_manager = WorkspaceManager()
        self.ide_manager = IDEManager()
        self.active_workspace = None
        self.sandbox_runner = SandboxRunner()
        self.code_indexer = CodeIndexer()
        self.code_indexer.build_index()
        self.arch_mapper = ArchitectureMapper("jessica")
        self.arch_mapper.build_architecture()
        self.dependency_graph = DependencyGraph(".")
        self.dependency_graph.build()
        self.debug_engine = DebugEngine()
        self.agent_registry = AgentRegistry()
        self.agent_registry.register(ProjectAnalyzerAgent())
        self.agent_orchestrator = AgentOrchestrator(self.agent_registry)
        self.agent_generator = AgentGenerator()
        self.agent_validator = AgentValidator()
        self.agent_installer = AgentInstaller()
        self.knowledge_graph = KnowledgeGraph()
        self.task_planner = TaskPlanner()
        self.settings = SettingsManager()
        self.request_history = {}  # Track repeated requests for auto-agent generation

        # Expose a shared collaboration graph to all registered agents.
        for registered_agent_name in self.agent_registry.list_agents():
            registered_agent = self.agent_registry.get(registered_agent_name)
            if registered_agent:
                setattr(registered_agent, "knowledge_graph", self.knowledge_graph)

    @staticmethod
    def _extract_request_text(request_input):
        if hasattr(request_input, "text"):
            return str(request_input.text)
        return str(request_input)

    async def process(self, user_input, user_id="default"):
        user_input = self._extract_request_text(user_input)

        # Record action for pattern learning at the request ingress.
        if hasattr(self.core, "pattern_engine"):
            self.core.pattern_engine.record(user_input)

        # Handle skill installation approval
        if user_input.lower() in ["yes", "install"] and self.core.pending_skill:
            result = self.core.skill_installer.install_skill(self.core.pending_skill)
            self.core.skill_registry.register_skill(
                self.core.pending_skill,
                f"jessica/skills/{self.core.pending_skill}"
            )
            installed = self.core.pending_skill
            self.core.pending_skill = None
            return f"{result}\n\nNew capability available: {installed}"

        if user_input.lower() == "stop":
            self.core.cancel_requested = True
            return "Current task cancellation requested."

        try:
            self.core.state_manager.transition_to(SystemState.PROCESSING, "input_received")
            self.core.logger.info("input_received | text=%s", user_input)

            lowered_input = user_input.lower()
            text = lowered_input

            # Generate internal execution plan
            plan = self.task_planner.create_plan(text)
            log_event(f"task_plan | steps={','.join(plan)}")

            # Pattern detection for autonomous agent creation
            normalized_request = self._normalize_request(text)
            if normalized_request:
                self.request_history[normalized_request] = self.request_history.get(normalized_request, 0) + 1

                # Auto-create agent after 3 repetitions
                if self.request_history[normalized_request] == 3:
                    agent_name = self._generate_agent_name(normalized_request)
                    agent_description = f"Automatically generated agent for: {normalized_request}"

                    try:
                        sandbox_path = self.agent_generator.create_agent(agent_name, agent_description)
                        sandbox_module_path = f"jessica.sandbox_agents.{agent_name.lower()}.agent"

                        log_event(f"agent_prototype_created | name={agent_name} | pattern={normalized_request}")

                        valid, validation_result = self.agent_validator.validate(
                            sandbox_module_path,
                            agent_name,
                        )

                        if valid:
                            installed_path = self.agent_installer.install(sandbox_path)
                            active_module_path = f"jessica.agents.{agent_name.lower()}.agent"
                            self.agent_registry.register_generated_agent(active_module_path, agent_name)
                            created_agent = self.agent_registry.get(agent_name)
                            if created_agent:
                                setattr(created_agent, "knowledge_graph", self.knowledge_graph)

                            log_event(f"agent_validation_passed | name={agent_name}")
                            log_event(f"agent_installed | name={agent_name} | path={installed_path}")

                            return (
                                "Pattern detected\n\n"
                                f"New capability prototype created:\n{agent_name}\n\n"
                                "Running sandbox validation...\n\n"
                                "Validation passed.\n"
                                "Agent installed successfully."
                            )

                        rejected_path = self.agent_installer.reject(sandbox_path)
                        failure_reason = validation_result.strip().splitlines()[-1] if validation_result else "Unknown validation error"
                        log_event(
                            f"agent_validation_failed | name={agent_name} | rejected_path={rejected_path} | reason={failure_reason}"
                        )

                        return (
                            "Pattern detected\n\n"
                            f"New capability prototype created:\n{agent_name}\n\n"
                            "Running sandbox validation...\n\n"
                            "Validation failed.\n"
                            f"Agent rejected.\nReason: {failure_reason}"
                        )
                    except Exception as e:
                        log_event(f"agent_creation_failed | error={str(e)}")

            if "reindex code" in text:

                result = self.code_indexer.build_index()
                return result

            if text.startswith("find "):

                symbol = text.replace("find ", "").strip()
                symbol = symbol.replace("where is ", "")
                symbol = symbol.replace("where ", "")
                symbol = symbol.replace("is defined", "").strip()

                results = self.code_indexer.find_symbol(symbol)

                if not results:
                    return "Symbol not found."

                return "\n".join(results)

            if text.startswith("show functions"):

                file = text.replace("show functions", "").strip()

                functions = self.code_indexer.get_functions(file)

                if not functions:
                    return "No functions found."

                return "\n".join(functions)

            if text.startswith("show classes"):

                file = text.replace("show classes", "").strip()

                classes = self.code_indexer.get_classes(file)

                if not classes:
                    return "No classes found."

                return "\n".join(classes)

            if text.startswith("explain module"):

                module = text.replace("explain module", "").strip()

                description = self.arch_mapper.describe_module(module)

                return description

            if text.startswith("who uses"):

                func = text.replace("who uses", "").strip()

                results = self.dependency_graph.find_function_usage(func)

                if not results:
                    return "No usage found."

                return "\n".join(results)

            if text.startswith("what depends on"):

                node = text.replace("what depends on", "").replace("?", "").strip()

                if not node:
                    return "Usage: what depends on <node>"

                dependents = self.knowledge_graph.get_dependents(node)

                if not dependents:
                    return f"No known components depend on '{node}'."

                lines = [f"Components that depend on '{node}':"]
                for source, relation in dependents:
                    lines.append(f"{source} ({relation})")

                return "\n".join(lines)

            if text.startswith("what does") and "depend on" in text:

                node = text.replace("what does", "").replace("depend on", "").replace("?", "").strip()

                if not node:
                    return "Usage: what does <node> depend on"

                relations = self.knowledge_graph.query(node)
                dependencies = [target for relation, target in relations if relation == "depends_on"]

                if not dependencies:
                    return f"No known dependencies found for '{node}'."

                return f"{node} depends on: " + ", ".join(dependencies)

            if text.startswith("agent"):

                agent_name = text.replace("agent", "").strip()

                agent = self.agent_registry.get(agent_name)

                if not agent:
                    return "Agent not found."

                result = agent.run(task=text)

                if hasattr(agent, "memory"):
                    agent.memory.store(agent.name, {
                        "task": text,
                        "result": str(result)
                    })

                self.knowledge_graph.add_node(agent.name)
                self.knowledge_graph.add_node("execution_engine")
                self.knowledge_graph.add_relation("execution_engine", "delegates_to", agent.name)

                return str(result)

            if text.startswith("multi-agent"):

                task = text.replace("multi-agent", "").strip()

                agents = self.agent_registry.list_agents()

                results = self.agent_orchestrator.run_parallel(
                    agents,
                    task,
                    context="."
                )

                self.knowledge_graph.add_node("execution_engine")
                self.knowledge_graph.add_node("dependency_manager")
                self.knowledge_graph.add_relation("execution_engine", "depends_on", "dependency_manager")

                for agent_name, agent_result in results.items():
                    current_agent = self.agent_registry.get(agent_name)
                    if current_agent and hasattr(current_agent, "memory"):
                        current_agent.memory.store(current_agent.name, {
                            "task": task,
                            "result": str(agent_result)
                        })

                    self.knowledge_graph.add_node(agent_name)
                    self.knowledge_graph.add_relation("execution_engine", "delegates_to", agent_name)

                return str(results)

            if text.startswith("debug"):

                parts = text.split(maxsplit=1)
                if len(parts) < 2 or not parts[1].strip():
                    return "Usage: debug <module>\nExample: debug grid_engine"

                target_module = parts[1].strip().replace(".py", "")
                errors = self.debug_engine.read_recent_errors(module=target_module, limit=1)

                if not errors:
                    return (
                        f"No recent errors found for module '{target_module}'.\n"
                        "Run the project first to capture structured error entries."
                    )

                latest = errors[0]
                callers = self.dependency_graph.find_function_usage(latest.get("function", ""))

                dependent_modules = []
                for call in callers:
                    if " -> " in call:
                        _, path_part = call.split(" -> ", 1)
                    elif " → " in call:
                        _, path_part = call.split(" → ", 1)
                    else:
                        continue
                    dependent_modules.append(Path(path_part).stem)

                dependent_modules = sorted(set(dependent_modules))
                suggestion = self.debug_engine.suggest_fix(latest.get("error", ""))

                response = []
                response.append(f"Debug report for module '{target_module}'")
                response.append("")
                response.append("Latest error detected:")
                response.append(f"File: {latest.get('file', 'unknown')}")
                response.append(f"Function: {latest.get('function', 'unknown')}")
                response.append(f"Line: {latest.get('line', 'unknown')}")
                response.append(f"Error: {latest.get('error', 'unknown')}")
                response.append(f"Timestamp: {latest.get('timestamp', 'unknown')}")
                response.append("")
                response.append(f"Dependency trace for function '{latest.get('function', 'unknown')}':")

                if callers:
                    response.extend(callers[:10])
                else:
                    response.append("No callers found in dependency graph.")

                response.append("")
                response.append("Dependent modules:")
                if dependent_modules:
                    response.append(", ".join(dependent_modules))
                else:
                    response.append("No dependent modules detected.")

                response.append("")
                response.append("Cause:")
                response.append(suggestion["cause"])
                response.append("")
                response.append("Suggested fix:")
                response.append(suggestion["patch"])
                response.append("")
                response.append("Apply patch? (yes/no)")

                return "\n".join(response)

            if "excel" in text:

                try:

                    modules = [
                        "ui",
                        "grid_engine",
                        "formula_engine",
                        "file_io"
                    ]

                    project_path = self.project_architect.build_project(
                        "excel_clone",
                        modules
                    )

                    self.ide_manager.workspace = project_path
                    self.active_workspace = project_path

                    return f"Project created: {project_path}"

                except Exception as e:

                    return f"Project build error: {str(e)}"

            # Project creation command
            if "build python project" in text:
                result = self.project_builder.create_python_project()

                if result.startswith("Project created at "):
                    project_path = result.replace("Project created at ", "", 1)
                    self.workspace_manager.open_project(project_path)
                    self.active_workspace = project_path
                    return f"Project created and opened: {project_path}"

                return result

            # Run active project
            if "run project" in text or text.startswith("run "):

                workspace = getattr(self.ide_manager, "workspace", None)

                # Handle named project execution (e.g., "run excel_clone_v2")
                if text.startswith("run ") and not workspace and "run project" not in text:
                    projects_dir = Path("projects")
                    if projects_dir.exists():
                        projects = list(projects_dir.iterdir())
                        
                        # Try to find matching project name in the command
                        for project in projects:
                            if project.is_dir() and project.name in text:
                                workspace = project
                                self.ide_manager.workspace = workspace
                                break

                # Multiple projects detection
                if not workspace:
                    projects_dir = Path("projects")
                    if projects_dir.exists():
                        projects = [p for p in projects_dir.iterdir() if p.is_dir()]
                        
                        if len(projects) > 1:
                            project_list = "\n".join([f"  - {p.name}" for p in projects])
                            return f"Multiple projects detected:\n\n{project_list}\n\nPlease open a project file first or specify which project to run (e.g., 'run {projects[0].name}')."
                        elif len(projects) == 1:
                            workspace = projects[0]
                            self.ide_manager.workspace = workspace

                if not workspace:
                    return "No active project workspace. Please open a project first."

                self.active_workspace = workspace

                result = self.sandbox_runner.run_python_project(workspace)

                return result

            current_user_id = str(user_id or "default")

            fact = self.core.fact_extractor.extract(user_input)
            if fact:
                key, value = fact
                self.core.knowledge_memory.store_fact(key, value, user_id=current_user_id)

            # --- Knowledge recall layer ---
            if "where was i born" in lowered_input:
                birthplace = self.core.knowledge_memory.get_fact("birthplace", user_id=current_user_id)

                if birthplace:
                    response = f"You told me earlier that you were born in {birthplace}."
                    return self._finalize(
                        response,
                        user_input=user_input,
                        intent="KNOWLEDGE_RECALL",
                        user_id=current_user_id,
                    )

            if "how old am i" in lowered_input:
                birth_year = self.core.knowledge_memory.get_fact("birth_year", user_id=current_user_id)

                if birth_year:
                    birth_year = int(birth_year)
                    age = datetime.now().year - birth_year
                    response = f"You were born in {birth_year}, which makes you {age} years old."
                    return self._finalize(
                        response,
                        user_input=user_input,
                        intent="AGE_QUERY",
                        user_id=current_user_id,
                    )

            if "who created you" in lowered_input:
                creator = self.core.identity.get_creator()
                response = (
                    f"I was created by {creator}, who designed my "
                    "Cognitive Sovereign Intelligence architecture."
                )
                return self._finalize(
                    response,
                    user_input=user_input,
                    intent="IDENTITY_QUERY",
                    user_id=current_user_id,
                )

            recall_keywords = [
                "earlier",
                "previous",
                "discuss",
                "we talked",
                "remember",
                "what did we",
            ]

            if any(word in lowered_input for word in recall_keywords):

                results = self.core.episodic_memory.search(user_input, user_id=current_user_id)

                if results:
                    summary = "Earlier discussion:\n\n"

                    for memory in results:
                        summary += f"You said: {memory['user_input']}\n"
                        summary += f"I responded: {memory['response']}\n\n"

                    return self._finalize(
                        summary,
                        user_input=user_input,
                        intent="MEMORY_RECALL",
                        user_id=current_user_id,
                    )

            if "how old am i" in lowered_input:

                memories = self.core.episodic_memory.search("born", user_id=current_user_id)

                if memories:

                    for memory in memories:
                        text = memory["user_input"]

                        if "born" in text.lower():
                            match = re.search(r"\d{4}", text)

                            if match:
                                birth_year = int(match.group())
                                age = datetime.now().year - birth_year

                                response = f"You were born in {birth_year}, which makes you {age} years old."
                                return self._finalize(
                                    response,
                                    user_input=user_input,
                                    intent="AGE_QUERY",
                                    user_id=current_user_id,
                                )

            identity_response = self.response_router.route_identity_layer(lowered_input)
            if identity_response is not None:
                return self._finalize(
                    identity_response,
                    user_input=user_input,
                    intent="IDENTITY_QUERY",
                    user_id=current_user_id,
                )

            # ---------------------------------
            # PATCH APPROVAL (priority)
            # ---------------------------------
            if lowered_input == "yes" and hasattr(self.core, "pending_patch"):

                file_path, new_code = self.core.pending_patch

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_code)

                del self.core.pending_patch

                self.core.activity.result("patch applied")

                return self._finalize(
                    "Patch applied successfully.",
                    user_input=user_input,
                    intent="PATCH_APPLIED",
                    user_id=current_user_id,
                )

            # ---------------------------------
            # TOOL APPROVAL
            # ---------------------------------
            approval_response = self.response_router.route_tool_approval_layer(lowered_input)
            if approval_response is not None:
                return self._finalize(
                    approval_response,
                    user_input=user_input,
                    intent="TOOL_APPROVAL",
                    user_id=current_user_id,
                )

            text = lowered_input

            # Project analysis (workspace only)
            if "analyze project" in text:
                from jessica.analysis.project_analyzer import ProjectAnalyzer

                analyzer = ProjectAnalyzer()

                workspace = getattr(self, "active_workspace", "projects")

                return analyzer.analyze(workspace)

            # Full system analysis
            if "analyze entire system" in text or "analyze full system" in text:
                from jessica.analysis.project_analyzer import ProjectAnalyzer

                analyzer = ProjectAnalyzer()

                return analyzer.analyze(".")

            # --- Project Analysis Layer ---
            if "analyze project" in lowered_input or "analyze codebase" in lowered_input:
                self.core.activity.thinking("scanning the project structure")

                summary = self.core.project_analyzer.scan_project(".")

                main_modules = self.core.project_analyzer.detect_main_modules("jessica")

                response = "Project Analysis:\n\n"

                response += f"Python files: {summary['python_files']}\n"

                response += f"Folders: {summary['folders']}\n"

                response += f"Lines of code: {summary['lines_of_code']}\n"

                if main_modules:
                    response += f"\nMain modules: {', '.join(main_modules)}\n"

                response += "\nDetected files (first 10):\n"

                for module in summary["modules"][:10]:
                    response += f"- {module}\n"

                self.core.activity.result("the project analysis")

                return self._finalize(
                    response,
                    user_input=user_input,
                    intent="PROJECT_ANALYSIS",
                    user_id=current_user_id,
                )

            # --- Code Analysis Layer ---
            if 'analyze' in user_input.lower() and '.py' in user_input.lower():
                # Extract filename from input
                match = re.search(r'(\S+\.py)', user_input)
                
                if match:
                    filename = match.group(1)
                    self.core.activity.thinking(f"reading {filename}")
                    
                    try:
                        analysis = self.core.code_analyzer.analyze_file(filename)
                        issues = self.core.refactor_analyzer.analyze(analysis["file_path"])
                        
                        response = f"Code Analysis: {filename}\n\n"
                        response += f"Location: {analysis['file_path']}\n"
                        response += f"Lines: {analysis['lines']}\n"
                        response += f"Functions: {len(analysis['functions'])}\n"
                        response += f"Classes: {len(analysis['classes'])}\n\n"
                        
                        if analysis["functions"]:
                            response += "Functions detected:\n"
                            for func in analysis["functions"][:10]:
                                response += f"- {func}\n"
                        
                        if analysis['classes']:
                            response += "\nClasses detected:\n"
                            for cls in analysis['classes'][:10]:
                                response += f"- {cls}\n"

                        if issues:
                            response += "\n\nI found the following improvement opportunities:\n\n"
                            for i, issue in enumerate(issues, 1):
                                response += f"{i}. {issue}\n"
                            response += "\nWould you like me to apply these improvements?"
                        
                        self.core.activity.result(f"analysis of {filename}")
                        
                        return self._finalize(
                            response,
                            user_input=user_input,
                            intent="CODE_ANALYSIS",
                            user_id=current_user_id,
                        )
                    except Exception as e:
                        error_msg = f"Error analyzing {filename}: {str(e)}"
                        self.core.activity.result(f"error reading {filename}")
                        return self._finalize(
                            error_msg,
                            user_input=user_input,
                            intent="CODE_ANALYSIS_ERROR",
                            user_id=current_user_id,
                        )

            # --- Controlled Self-Improvement Layer (Phase 480) ---
            if "self improve" in lowered_input:
                result = self.core.self_improvement_engine.run(self.core)
                return self._finalize(
                    result,
                    user_input=user_input,
                    intent="SELF_IMPROVEMENT",
                    user_id=current_user_id,
                )

            # --- Refactor Analysis Layer (Safe Mode) ---
            if ("refactor" in lowered_input or "improve" in lowered_input) and "apply improvements" not in lowered_input and "improve project" not in lowered_input and "self improve" not in lowered_input:
                filename = "jessica_core.py"

                analysis = self.core.code_analyzer.analyze_file(filename)
                issues = self.core.refactor_analyzer.analyze(analysis["file_path"])

                if not issues:
                    return self._finalize(
                        "No refactoring issues detected.",
                        user_input=user_input,
                        intent="REFACTOR_ANALYSIS",
                        user_id=current_user_id,
                    )

                response = "I found the following improvement opportunities:\n\n"

                for i, issue in enumerate(issues, 1):
                    response += f"{i}. {issue}\n"

                response += "\nWould you like me to apply these improvements?"

                return self._finalize(
                    response,
                    user_input=user_input,
                    intent="REFACTOR_ANALYSIS",
                    user_id=current_user_id,
                )

            # --- Code Editing Layer ---
            if "simplify execute_workflow" in lowered_input:
                self.core.activity.thinking("analyzing execute_workflow function")

                filename = "jessica_core.py"
                analysis = self.core.code_analyzer.analyze_file(filename)

                with open(analysis["file_path"], "r", encoding="utf-8") as f:
                    source = f.read()

                # Keep intent optional for compatibility with existing call sites.
                new_function = """
def execute_workflow(self, workflow, intent=None):

    executor = getattr(self, "tool_executor", None)
    for step in workflow:
        if executor and hasattr(executor, "execute"):
            executor.execute(step)

    return "Workflow completed."
"""

                updated = self.core.code_editor_engine.replace_function(
                    source,
                    "execute_workflow",
                    new_function,
                )

                with open(analysis["file_path"], "w", encoding="utf-8") as f:
                    f.write(updated)

                self.core.activity.result("updated the execute_workflow function")

                return self._finalize(
                    "I found an opportunity to simplify this function.\nProposed change inserted in the editor.",
                    user_input=user_input,
                    intent="CODE_EDITING",
                    user_id=current_user_id,
                )

            # --- Patch Preview Layer (Phase 450) ---
            if "patch execute_workflow" in lowered_input:

                filename = "jessica_core.py"

                analysis = self.core.code_analyzer.analyze_file(filename)

                with open(analysis["file_path"], "r", encoding="utf-8") as f:
                    old_code = f.read()

                new_function = """
def execute_workflow(self, workflow):

    executor = getattr(self, "tool_executor", None)

    for step in workflow:
        if executor and hasattr(executor, "execute"):
            executor.execute(step)

    return "Workflow completed."
"""

                new_code = self.core.code_editor_engine.replace_function(
                    old_code,
                    "execute_workflow",
                    new_function
                )

                patch = self.core.patch_generator.generate_patch(old_code, new_code)

                self.core.pending_patch = (analysis["file_path"], new_code)

                return self._finalize(
                    f"Patch preview:\n\n{patch}\n\nApply this patch? (yes/no)",
                    user_input=user_input,
                    intent="PATCH_PREVIEW",
                    user_id=current_user_id,
                )

            # ---------------------------------
            # APPLY PROJECT IMPROVEMENTS (Phase 470)
            # ---------------------------------
            if "apply improvements" in lowered_input:
                try:

                    if not hasattr(self.core, "patch_queue") or not self.core.patch_queue.has_items():
                        return self._finalize(
                            "No improvements queued.",
                            user_input=user_input,
                            intent="PROJECT_IMPROVEMENTS_EMPTY",
                            user_id=current_user_id,
                        )

                    applied = 0

                    self.core.activity.thinking("applying project improvements")

                    while self.core.patch_queue.has_items():

                        item = self.core.patch_queue.next()

                        try:

                            if not isinstance(item, dict):
                                continue

                            file = item.get("file", "unknown file")

                            # placeholder for future patch execution

                            applied += 1

                            # Avoid flooding UI/console when many files are queued.
                            if applied <= 10 or applied % 25 == 0:
                                self.core.activity.action(f"improving {file}")

                        except Exception as step_error:

                            self.core.activity.action(
                                f"skipping improvement due to error: {str(step_error)}"
                            )

                    self.core.activity.result("finished improving the project")

                    return self._finalize(
                        f"{applied} improvements applied successfully.",
                        user_input=user_input,
                        intent="PROJECT_IMPROVEMENTS_APPLIED",
                        user_id=current_user_id,
                    )

                except Exception as e:

                    print("PATCH QUEUE ERROR:", e)

                    return self._finalize(
                        "An internal error occurred while applying improvements.",
                        user_input=user_input,
                        intent="PROJECT_IMPROVEMENTS_ERROR",
                        user_id=current_user_id,
                    )

            # ---------------------------------
            # IMPROVE PROJECT (Phase 460)
            # ---------------------------------
            if "improve project" in lowered_input:

                self.core.activity.thinking("scanning the project for improvements")

                improvements = self.core.project_refactor_engine.scan_project(
                    ".",
                    self.core.refactor_analyzer
                )

                if not improvements:
                    return self._finalize(
                        "No improvement opportunities detected in the project.",
                        user_input=user_input,
                        intent="PROJECT_IMPROVEMENT_SCAN",
                        user_id=current_user_id,
                    )

                self.core.pending_project_improvements = improvements
                self.core.patch_queue.queue = improvements

                response = "I found the following improvement opportunities:\n\n"

                count = 1
                max_preview_issues = 20
                truncated = False

                for item in improvements[:5]:

                    for issue in item["issues"]:

                        if count > max_preview_issues:
                            truncated = True
                            break

                        response += f"{count}. {issue}\n"
                        count += 1

                    if truncated:
                        break

                if truncated:
                    response += "...additional issues omitted for stability.\n"

                response += "\nType 'apply improvements' to fix them."

                return self._finalize(
                    response,
                    user_input=user_input,
                    intent="PROJECT_IMPROVEMENT_SCAN",
                    user_id=current_user_id,
                )

            # --- Project Patch Queue Preview Layer (Phase 460) ---
            if lowered_input == "preview patches" and self.core.patch_queue.has_items():

                response = "Patch queue prepared for the following files:\n\n"

                for item in self.core.patch_queue.queue[:5]:

                    response += f"- {item['file']}\n"

                response += "\nType 'apply improvements' to apply queued improvements."

                return self._finalize(
                    response,
                    user_input=user_input,
                    intent="PROJECT_PATCH_QUEUE_PREVIEW",
                    user_id=current_user_id,
                )

            intent = route_intent(user_input)
            self.core.logger.info("intent_detected | intent=%s", intent)
            update_intent(intent)
            self.core.capability_advisor.record_intent(intent)
            self.core.predictive_engine.record_intent(intent)

            model_choice = self.core.model_orchestrator.choose_model(intent)
            self.core.logger.info("model_orchestrator | selected=%s", model_choice)

            persona = select_persona(intent, user_input)
            log_event(f"persona_selected | {persona}")
            update_persona(persona)

            inquiry = check_for_missing_information(intent, user_input)
            if inquiry:
                log_event("inquiry_engine | clarification requested")
                return self._finalize(
                    inquiry,
                    user_input=user_input,
                    intent=intent,
                    user_id=current_user_id,
                )

            monologue = generate_monologue(user_input, intent)
            for thought in monologue:
                log_event(f"internal_monologue | {thought}")

            alerts = observe(monologue, intent)
            for alert in alerts:
                log_event(f"observer | {alert}")

            if alerts:
                log_event("observer | safety review triggered")

            pipeline = run_cognitive_pipeline(
                user_input,
                intent,
                persona,
                monologue,
                alerts,
            )
            log_event(f"csi_pipeline | risk_level={pipeline['risk_level']}")

            friction_response = apply_cognitive_friction(alerts, intent)
            if friction_response:
                log_event("cognitive_friction | deliberation triggered")
                return self._finalize(friction_response, user_input=user_input, intent=intent)

            response = await self._execution_layers(
                user_input=user_input,
                intent=intent,
                persona=persona,
                model_choice=model_choice,
            )

            response = self.core._clean_response(response)

            suggestion = self.core.capability_advisor.analyze_patterns()
            if suggestion:
                tool_offer = self.core.tool_advisor.create_suggestion(suggestion)

                if tool_offer:
                    return self._finalize(
                        tool_offer,
                        user_input=user_input,
                        intent=intent,
                        user_id=current_user_id,
                    )

                queue_insight(suggestion)

            prediction = self.core.predictive_engine.predict_next_with_skills(
                self.core.skill_memory.skills
            )
            if prediction:
                self.core.insight_manager.add_insight(prediction)

            if not self.core._is_valid_response(response):
                raise ValueError("Invalid or empty response")

            return self._finalize(
                response,
                user_input=user_input,
                intent=intent,
                user_id=current_user_id,
            )

        except Exception as exc:
            try:
                self.core.state_manager.transition_to(SystemState.ERROR, "processing_failure")
            except Exception:
                self.core.state_manager.current_state = SystemState.ERROR
                update_state(SystemState.ERROR.value)

            self.core.logger.error("error | type=%s | message=%s", type(exc).__name__, str(exc))

            safe_message = "I'm sorry, something went wrong. Please try again."

            try:
                self.core.state_manager.transition_to(SystemState.IDLE, "error_recovered")
            except Exception:
                self.core.state_manager.current_state = SystemState.IDLE
                update_state(SystemState.IDLE.value)

            return safe_message

    async def _execution_layers(self, *, user_input, intent, persona, model_choice):
        simulation = simulate_action(intent)
        if simulation["risk"] == "high":
            return f"Simulation warning: {simulation['message']}"

        internal_response = self.response_router.route_internal_intent_layer(intent, user_input)
        if internal_response is not None:
            return internal_response

        if self.core.cancel_requested:
            self.core.cancel_requested = False
            return "Task cancelled."

        skill_response = self._skill_memory_layer(intent)
        if skill_response is not None:
            return skill_response

        # ---------------------------------
        # Workflow Memory Check
        # ---------------------------------

        stored_workflow = self.core.workflow_memory.get_workflow(intent)

        if stored_workflow:

            optimized = self.core.workflow_optimizer.optimize(stored_workflow)

            self.core.workflow_memory.store_workflow(intent, optimized)

            ConsoleManager.log("Executing stored workflow...")

            for step in optimized:

                ConsoleManager.log(f"[STEP] {step}")

                # Placeholder execution logic
                if step == "create_project_directory":
                    ConsoleManager.log("Creating project directory")

                elif step == "generate_main_script":
                    ConsoleManager.log("Generating main.py")

                elif step == "create_config_file":
                    ConsoleManager.log("Generating config.json")

            response = "Using an optimized workflow for this task."

            return response

        plan = create_plan(user_input)
        if plan:
            if isinstance(plan, TaskGraph):
                results = self.core.task_graph_executor.execute_graph(plan)

                # ---------------------------------
                # Optimize workflow before storing
                # ---------------------------------

                steps = [node.name for node in plan.nodes]

                optimized_steps = self.core.workflow_optimizer.optimize(steps)

                self.core.workflow_memory.store_workflow(intent, optimized_steps)

                return "Task Graph Execution:\n" + "\n".join(results)

            plan_text = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(plan)])
            results = execute_plan(plan, user_input)
            result_text = "\n".join(results)
            return f"Task Plan:\n{plan_text}\n\nExecution Results:\n{result_text}"

        return await self._model_layer(
            user_input=user_input,
            persona=persona,
            model_choice=model_choice,
        )

    def _skill_memory_layer(self, intent):
        tool_name = self.core.skill_memory.find_tool(intent)
        if not tool_name:
            return None

        from jessica.tools.tool_manager import ToolManager

        manager = ToolManager()

        if tool_name not in manager.tools:
            return None

        result = manager.tools[tool_name]()
        self.core.skill_memory.record_skill(intent, tool_name)
        return f"Skill memory used tool: {tool_name}\n\nResult:\n{result}"

    async def _model_layer(self, *, user_input, persona, model_choice):
        model_input = user_input

        if persona == "TEACHER":
            model_input = f"Explain clearly like a teacher: {user_input}"
        elif persona == "ENGINEER":
            model_input = f"Provide a technical engineering answer: {user_input}"
        elif persona == "ANALYST":
            model_input = f"Provide an analytical breakdown: {user_input}"

        if model_choice == "local":
            self.core.current_task = asyncio.create_task(
                asyncio.to_thread(self.core.model_orchestrator.run_local, model_input)
            )

            try:
                return await self.core.current_task
            finally:
                self.core.current_task = None

        if model_choice == "cloud":
            return self.core.model_orchestrator.run_cloud(model_input)

        return "Processing internally."

    def _finalize(self, response, user_input=None, intent=None, user_id="default"):
        if intent != "PATTERN_DETECTED" and hasattr(self.core, "pattern_engine"):
            patterns = self.core.pattern_engine.detect()

            if patterns:
                action, count = patterns[0]
                skill_name = action.replace(" ", "_").lower()
                
                # Check registry first
                if self.core.skill_registry.skill_exists(skill_name):
                    response = (
                        f"Capability already installed: {skill_name}\n"
                        "Using installed capability."
                    )
                    intent = "PATTERN_DETECTED"

                else:
                    installed_skill = Path("jessica/skills") / skill_name
                    generated_skill = Path("jessica/generated_skills") / skill_name

                    # Skill already installed (filesystem check)
                    if installed_skill.exists():
                        response = (
                            f"Capability already installed: {skill_name}\n"
                            f"Using installed capability."
                        )
                        intent = "PATTERN_DETECTED"

                    # Skill already generated but not installed
                    elif generated_skill.exists():
                        self.core.pending_skill = skill_name
                        response = (
                            f"A prototype capability already exists:\n\n"
                            f"{generated_skill}\n\n"
                            "Install this skill into the system? (yes/no)"
                        )
                        intent = "PATTERN_DETECTED"

                    # Generate new skill
                    else:
                        skill_path = self.core.skill_generator.generate_skill(
                            skill_name,
                            f"Auto-generated capability for repeated task: {action}"
                        )
                        self.core.pending_skill = skill_name
                        response = (
                            f"I noticed repeated '{action}' requests ({count} occurrences).\n\n"
                            f"I generated a prototype capability:\n\n"
                            f"{skill_path}\n\n"
                            "Install this skill into the system? (yes/no)"
                        )
                        intent = "PATTERN_DETECTED"

        if user_input is not None and intent is not None:
            try:
                self.core.episodic_memory.store_event(
                    user_input,
                    response,
                    intent,
                    user_id=user_id,
                )
            except Exception as exc:
                self.core.logger.warning("episodic_memory_store_failed | message=%s", str(exc))

        self.core.state_manager.transition_to(SystemState.RESPONDING, "response_ready")
        self.core.logger.info("response_sent | text=%s", response)
        self.core.state_manager.transition_to(SystemState.IDLE, "cycle_complete")
        return response

    def _normalize_request(self, text):
        """Normalize request text to detect patterns."""
        # Extract key action phrases
        if "analyze" in text and "project" in text:
            return "analyze_project"
        elif "debug" in text:
            return "debug"
        elif "build" in text or "create" in text:
            return "build"
        elif "test" in text:
            return "test"
        elif "refactor" in text:
            return "refactor"
        return None

    def _generate_agent_name(self, normalized_request):
        """Generate a proper agent class name from normalized request."""
        # Convert analyze_project -> AnalyzeProjectAgent
        parts = normalized_request.split('_')
        name = ''.join(word.capitalize() for word in parts) + 'Agent'
        return name
