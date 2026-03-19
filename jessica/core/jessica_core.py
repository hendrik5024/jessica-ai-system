import os

from config import Settings
from jessica.cognition.activity_stream import ActivityStream
from jessica.cognition.cognitive_pipeline import CognitivePipeline
from jessica.cognition.fact_extractor import FactExtractor
from jessica.cognition.insight_manager import InsightManager
from jessica.cognition.pattern_engine import PatternEngine
from jessica.cognition.predictive_engine import PredictiveEngine
from jessica.cognition.project_builder import ProjectBuilder
from jessica.cognition.skill_generator import SkillGenerator
from jessica.cognition.skill_installer import SkillInstaller
from jessica.cognition.workflow_optimizer import WorkflowOptimizer
from jessica.execution.task_graph_executor import TaskGraphExecutor
from jessica.memory.episodic_memory import EpisodicMemory
from jessica.memory.identity_manager import IdentityManager
from jessica.memory.knowledge_memory import KnowledgeMemory
from jessica.memory.skill_memory import SkillMemory
from jessica.memory.workflow_memory import WorkflowMemory
from jessica.models.model_orchestrator import ModelOrchestrator
from jessica.autonomy.self_improvement_engine import SelfImprovementEngine
from jessica.self_improvement.capability_advisor import CapabilityAdvisor
from jessica.self_improvement.tool_advisor import ToolAdvisor
from jessica.tools.load_generated_tools import load_generated_tools
from jessica.tools.code_analyzer import CodeAnalyzer
from jessica.tools.code_editor_engine import CodeEditorEngine
from jessica.tools.refactor_analyzer import RefactorAnalyzer
from jessica.tools.patch_generator import PatchGenerator
from jessica.tools.patch_queue import PatchQueue
from jessica.tools.project_refactor_engine import ProjectRefactorEngine
from jessica.tools.project_analyzer import ProjectAnalyzer
from jessica.tools.register_tools import register_all_tools
from jessica.system.skill_registry import SkillRegistry
from model_interface import ModelInterface
from state_manager import StateManager

from .request_pipeline import RequestPipeline
from .response_router import ResponseRouter


class JessicaCore:
    def __init__(self, settings: Settings, logger):
        self.settings = settings
        self.logger = logger
        self.state_manager = StateManager(logger)
        self.current_task = None
        self.cancel_requested = False

        self.model = ModelInterface()
        self.model_orchestrator = ModelOrchestrator(self.model)

        self.capability_advisor = CapabilityAdvisor()
        self.tool_advisor = ToolAdvisor()
        self.predictive_engine = PredictiveEngine()
        self.insight_manager = InsightManager()
        self.workflow_optimizer = WorkflowOptimizer()
        self.task_graph_executor = TaskGraphExecutor()
        self.episodic_memory = EpisodicMemory()
        self.knowledge_memory = KnowledgeMemory()
        self.fact_extractor = FactExtractor()
        self.pattern_engine = PatternEngine()
        self.skill_generator = SkillGenerator()
        self.skill_installer = SkillInstaller()
        self.skill_registry = SkillRegistry()
        self.project_builder = ProjectBuilder()
        self.pending_skill = None
        self.identity = IdentityManager()
        self.skill_memory = SkillMemory()
        self.workflow_memory = WorkflowMemory()
        self.activity = ActivityStream()
        self.project_analyzer = ProjectAnalyzer()
        self.code_analyzer = CodeAnalyzer()
        self.code_editor_engine = CodeEditorEngine()
        self.refactor_analyzer = RefactorAnalyzer()
        self.patch_generator = PatchGenerator()
        self.patch_queue = PatchQueue()
        self.project_refactor_engine = ProjectRefactorEngine()
        self.self_improvement_engine = SelfImprovementEngine()

        register_all_tools()
        load_generated_tools()

        self.response_router = ResponseRouter(self)
        self.request_pipeline = RequestPipeline(self, self.response_router)
        self.cognitive_pipeline = CognitivePipeline(self)

    def _clean_response(self, response: str) -> str:
        cleaned = (response or "").strip()

        if "Final Answer:" in cleaned:
            cleaned = cleaned.split("Final Answer:", 1)[1].strip()

        for marker in ["Reasoning:", "Chain-of-thought:", "<think>", "</think>"]:
            if marker in cleaned:
                cleaned = cleaned.split(marker, 1)[0].strip()

        return cleaned

    def _is_valid_response(self, response: str) -> bool:
        if not response:
            return False

        if not isinstance(response, str):
            return False

        if not response.strip():
            return False

        return True

    async def handle_input(self, user_input, user_id=None):
        resolved_user_id = str(user_id or os.getenv("JESSICA_USER_ID", "default")).strip() or "default"
        return await self.request_pipeline.process(user_input, user_id=resolved_user_id)




def execute_workflow(self, workflow):

    executor = getattr(self, "tool_executor", None)

    for step in workflow:
        if executor and hasattr(executor, "execute"):
            executor.execute(step)

    return "Workflow completed."