"""
Phase 87/90/91: Cognitive Kernel

Jessica's unified entry point.
All responses originate from Jessica.
Model is only an advisory tool.
Phase 90: Permission-governed with audit logging.
Phase 91: Internal belief system for identity consistency.
Phase 98.5: Belief-aware routing with model governance.
"""

from typing import Optional
from jessica.core.knowledge_store import KnowledgeStore
from jessica.core.reasoning_engine import ReasoningEngine
from jessica.core.cognitive_controller import CognitiveController
from jessica.core.tool_selector import ToolSelector
from jessica.reasoning.structured_reasoner import StructuredReasoner, ProblemType
from jessica.reasoning.self_verifier import SelfVerifier
from jessica.security.permission_manager import PermissionManager
from jessica.security.audit_log import AuditLog
from jessica.beliefs.belief_store import BeliefStore
from jessica.beliefs.belief_reasoner import BeliefReasoner
from jessica.autonomy.autonomy_orchestrator import AutonomyOrchestrator
from jessica.execution.action_executor import ActionExecutor
from jessica.routing.personal_question_detector import PersonalQuestionDetector
from jessica.routing.model_governor import ModelGovernor
from jessica.context.context_manager import ContextManager
from jessica.memory.belief_store import BeliefStore as MemoryBeliefStore
from jessica.reasoning.identity_reasoner import IdentityReasoner
from jessica.reasoning.memory_reasoner import MemoryReasoner
from jessica.reasoning.time_reasoner import TimeReasoner
from jessica.memory.conversation_memory import ConversationMemory


class CognitiveKernel:
    """
    The central orchestrator of Jessica.
    Phase 87: Complete control architecture.
    Phase 90: Permission-governed with audit logging.
    Phase 91: Internal belief system for identity consistency.
    Phase 92: Autonomous action proposals.
    Phase 93: Action execution engine.
    Phase 95: Tool selection engine for intelligent routing.
    Phase 96: Deterministic structured reasoning without blind fallback.
    Phase 97: Self-verification for error detection and correction.
    Phase 98.5: Belief-aware routing with model governance.
    """

    def __init__(self, llm=None):
        self.permission_manager = PermissionManager()
        self.audit_log = AuditLog()
        self.belief_store = BeliefStore()
        self.belief_reasoner = BeliefReasoner(self.belief_store)
        self.tool_selector = ToolSelector()
        self.autonomy = AutonomyOrchestrator()
        self.executor = ActionExecutor(
            permission_manager=self.permission_manager,
            audit_log=self.audit_log,
        )
        self.knowledge_store = KnowledgeStore(permission_manager=self.permission_manager)
        self.reasoning_engine = ReasoningEngine(permission_manager=self.permission_manager)
        # Phase 96: Initialize structured reasoning engine
        self.structured_reasoner = StructuredReasoner()
        # Phase 97: Initialize self-verification engine
        self.verifier = SelfVerifier()
        # Phase 98.5: Initialize routing components
        self.personal_detector = PersonalQuestionDetector()
        self.model_governor = ModelGovernor(audit_log=self.audit_log)
        # Phase 98.7: Initialize context manager for conversation memory
        self.context = ContextManager()
        # Phase 102: Working memory for conversational flow
        self.conversation_memory = ConversationMemory(max_turns=10)
        # Phase 98.8: Initialize aggressive belief capture system (NEW)
        self.memory_beliefs = MemoryBeliefStore()
        # Phase 98.9: Initialize identity reasoning engine (NEW)
        self.identity_reasoner = IdentityReasoner(self.memory_beliefs)
        # Phase 99: Initialize memory reasoning engine (NEW)
        self.memory_reasoner = MemoryReasoner(self.memory_beliefs)
        # Phase 100: Initialize time and age reasoning engine (NEW)
        self.time_reasoner = TimeReasoner(self.memory_beliefs)
        # Pass model to reasoning engine for fallback
        if llm:
            self.reasoning_engine.model = llm
        self.controller = CognitiveController(
            self.knowledge_store, self.reasoning_engine, llm, self.belief_store, self.belief_reasoner
        )
        self.model = llm

        original_add_turn = self.context.add_turn

        def add_turn_with_working_memory(user_input: str, assistant_response: str):
            original_add_turn(user_input, assistant_response)
            self.conversation_memory.add_turn(user_input, str(assistant_response))

        self.context.add_turn = add_turn_with_working_memory

    def process(self, user_input: str) -> str:
        """
        Main entry point with belief-first routing (Phase 98.5).
        Phase 98.7: Now includes conversation context memory.
        
        Priority Order:
        1. IdentityReasoner
        2. MemoryReasoner
        3. StructuredReasoner
        4. Model fallback (with governance)
        
        Jessica controls all responses.
        Phase 90: All actions logged and permission-checked.
        Phase 92: Proposal-based autonomy with human approval.
        Phase 95: Tool selection for intelligent routing.
        Phase 96: Deterministic structured reasoning before model fallback.
        Phase 97: Self-verification for error detection and correction.
        Phase 98.5: Belief-aware routing with model governance.
        Phase 98.7: Conversation context awareness and memory.
        Phase 98.9: Identity reasoning engine with fact-linking.
        """
        questions = self._split_questions(user_input)
        if len(questions) > 1:
            responses = []
            for question in questions:
                response = self._handle_single_question(question)
                responses.append(response if isinstance(response, str) else str(response))
            combined_response = " ".join(responses)
            self.conversation_memory.add_turn(user_input, combined_response)
            return combined_response

        user_input = questions[0] if questions else user_input

        recent = self.conversation_memory.get_recent()
        last_user = self.conversation_memory.get_last_user_input()
        last_response = self.conversation_memory.get_last_response()

        # Phase 98.7: Get recent conversation context
        recent_context = self.context.get_recent_context()

        q = user_input.lower()

        identity_answer = self._get_identity_answer(q)
        if identity_answer:
            self.context.add_turn(user_input, identity_answer)
            return identity_answer

        if "incorrect" in q or "wrong" in q:
            if last_response:
                response = "I understand that my previous answer may be incorrect. Let me review it."
                self.context.add_turn(user_input, response)
                return response

        if "that" in q and last_user:
            combined = last_user + " " + user_input
            if combined.strip().lower() != user_input.strip().lower():
                return self.process(combined)

        if "if i were born" in q:
            hypothetical_age = self._calculate_age_from_text(q)
            if hypothetical_age is not None:
                response = f"You would be {hypothetical_age} years old."
                self.context.add_turn(user_input, response)
                return response

        # ===== PRIORITY 0: TIME & AGE REASONING (Phase 100) =====
        if "how old am i" in q:
            age = self.time_reasoner.calculate_age()
            if age is not None:
                age_response = f"You are {age} years old."
                self.context.add_turn(user_input, age_response)
                return age_response
        
        # ===== PRIORITY 0: IDENTITY REASONING (Phase 98.9) =====
        # NEW: Link facts together, answer consistently, speak naturally
        if self.identity_reasoner.has_identity_question(user_input):
            identity_answer = self.identity_reasoner.answer(user_input)
            if identity_answer:
                lower_identity_answer = identity_answer.lower().strip()
                unknown_markers = [
                    "i do not know",
                    "i'm not sure",
                    "i am not sure",
                    "yet",
                ]
                should_fallback_to_memory = any(marker in lower_identity_answer for marker in unknown_markers)

                if not should_fallback_to_memory:
                    self.audit_log.record("identity_reasoned", "allowed", {"question": user_input, "answer": identity_answer})
                    self.context.add_turn(user_input, identity_answer)
                    return identity_answer

        # ===== PRIORITY 1: MEMORY FACT CAPTURE + REASONING (Phase 99) =====
        lower_input = user_input.lower()

        if "favorite color is" in lower_input:
            start_idx = lower_input.find("favorite color is")
            value = user_input[start_idx + len("favorite color is"):].strip().strip(".!? ")
            if value:
                self.memory_beliefs.set_fact("favorite_color", value)
                remember_response = f"I will remember that your favorite color is {value}."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if "my age is" in lower_input:
            import re
            match = re.search(r"my age is\s+(\d{1,3})", lower_input)
            if match:
                age_value = int(match.group(1))
                self.memory_beliefs.set_fact("age", age_value)
                remember_response = f"I will remember that you are {age_value} years old."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if "years old" in lower_input and ("i am" in lower_input or "i'm" in lower_input):
            import re
            match = re.search(r"\b(\d{1,3})\s+years old\b", lower_input)
            if match:
                age_value = int(match.group(1))
                self.memory_beliefs.set_fact("age", age_value)
                remember_response = f"I will remember that you are {age_value} years old."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if "my city is" in lower_input:
            start_idx = lower_input.find("my city is")
            city_value = user_input[start_idx + len("my city is"):].strip().strip(".!? ")
            if city_value:
                self.memory_beliefs.set_fact("city", city_value)
                remember_response = f"I will remember that your city is {city_value}."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if "i live in" in lower_input:
            start_idx = lower_input.find("i live in")
            city_value = user_input[start_idx + len("i live in"):].strip().strip(".!? ")
            if city_value:
                self.memory_beliefs.set_fact("city", city_value)
                remember_response = f"I will remember that you live in {city_value}."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if "my job is" in lower_input:
            start_idx = lower_input.find("my job is")
            job_value = user_input[start_idx + len("my job is"):].strip().strip(".!? ")
            if job_value:
                self.memory_beliefs.set_fact("job", job_value)
                self.memory_beliefs.set("profession", job_value)
                remember_response = f"I will remember that your job is {job_value}."
                self.context.add_turn(user_input, remember_response)
                return remember_response

        if (("i am a " in lower_input) or ("i am an " in lower_input)) and "creator" not in lower_input:
            phrase = "i am an " if "i am an " in lower_input else "i am a "
            start_idx = lower_input.find(phrase)
            job_value = user_input[start_idx + len(phrase):].strip().strip(".!? ")
            if job_value:
                self.memory_beliefs.set_fact("job", job_value)
                self.memory_beliefs.set("profession", job_value)
                remember_response = f"I will remember that your job is {job_value}."
                self.context.add_turn(user_input, remember_response)
                return remember_response
        
        # Phase 98.8: AGGRESSIVE BELIEF CAPTURE (NEW - CRITICAL)
        self._capture_beliefs_from_input(user_input)

        memory_answer = self.memory_reasoner.answer(user_input)
        if memory_answer:
            self.audit_log.record("memory_reasoned", "allowed", {"question": user_input, "answer": memory_answer})
            self.context.add_turn(user_input, memory_answer)
            return memory_answer
        
        # Memory hook: capture user information
        self._capture_memory(user_input)

        # Phase 95: Select appropriate tool for this request
        selected_tool = self.tool_selector.select_tool(user_input)

        # Phase 92: Check if action proposal needed
        proposal = self.autonomy.process(user_input)
        if proposal:
            response = {
                "type": "proposal",
                "description": proposal.description,
                "reasoning": proposal.reasoning,
                "actions": proposal.actions,
                "risk": proposal.risk_level,
                "proposal_id": proposal.proposal_id,
                "selected_tool": selected_tool,
            }
            # Phase 98.7: Store turn in context
            self.context.add_turn(user_input, str(response))
            return response

        # ===== PRIORITY 2: Math Questions (Phase 96) =====
        # Phase 98.7: Pass context to structured reasoning
        reasoning_response = self.structured_reasoner.process(user_input, context=recent_context)
        
        if (reasoning_response.validation.confidence > 0.5 and 
            reasoning_response.problem_type != ProblemType.PERSONAL):
            # Phase 97: Verify the structured response
            verified_response = self.verifier.verify(reasoning_response)
            # Phase 98.7: Store turn in context
            self.context.add_turn(user_input, verified_response.answer)
            return verified_response.answer
        
        # ===== PRIORITY 3 & 4: Model fallback with governance =====
        identity_questions = [
            "who created you",
            "who made you",
            "who coded you",
            "who are you",
        ]

        if any(identity_q in q for identity_q in identity_questions):
            creator = self.memory_beliefs.get_fact("creator") or self.memory_beliefs.get("creator")
            if creator:
                response = f"{creator} created me."
                self.context.add_turn(user_input, response)
                return response
            response = "I do not know who created me yet."
            self.context.add_turn(user_input, response)
            return response

        # Get belief answer if it exists (for conflict checking)
        belief_answer = self._answer_from_beliefs(user_input)
        
        # Get model answer (if model available)
        model_answer = None
        if self.model:
            try:
                model_answer = self.controller.reasoning_engine.model.generate(user_input)
                model_answer = self._convert_model_to_jessica(model_answer)
            except Exception as e:
                self.audit_log.log("model_error", {"question": user_input, "error": str(e)})
        
        # Phase 98.8: Block dangerous model outputs FIRST
        if model_answer:
            blocked_answer = self._block_model_dangerous_outputs(model_answer)
            if blocked_answer != model_answer:
                # Model was trying to say something dangerous
                self.audit_log.record("model_blocked_for_safety", "denied", {
                    "question": user_input,
                    "blocked_output": model_answer,
                    "safe_output": blocked_answer
                })
                self.context.add_turn(user_input, blocked_answer)
                return blocked_answer
            
            # Phase 98.8: Detect conflicts between model and beliefs
            conflict_response = self._detect_belief_conflicts(model_answer, user_input)
            if conflict_response:
                self.audit_log.record("model_conflicted_with_belief", "denied", {
                    "question": user_input,
                    "model_answer": model_answer,
                    "belief_answer": conflict_response
                })
                self.context.add_turn(user_input, conflict_response)
                return conflict_response
        
        # Check model governance (Phase 98.5)
        if model_answer:
            governance = self.model_governor.govern_model_response(
                question=user_input,
                model_answer=model_answer,
                belief_answer=belief_answer
            )
            
            if governance["allowed"]:
                # Phase 98.7: Store turn in context
                safe_answer = self._convert_model_to_jessica(governance["answer"])
                self.context.add_turn(user_input, safe_answer)
                return safe_answer
            elif governance["conflict"]:
                # Conflict detected: use belief instead
                self.audit_log.record("model_blocked_due_to_conflict", "denied", {
                    "question": user_input,
                    "belief": belief_answer,
                    "model": model_answer
                })
                # Phase 98.7: Store turn in context
                self.context.add_turn(user_input, governance["answer"])
                return governance["answer"]
            else:
                # Model not authorized
                self.audit_log.record("model_not_authorized", "denied", {
                    "question": user_input,
                    "reason": governance["reason"]
                })
        
        # Final fallback: use controller (legacy path)
        result = self.controller.process(user_input)
        # Phase 98.7: Store turn in context
        if isinstance(result, str):
            safe_result = self._convert_model_to_jessica(result)
            self.context.add_turn(user_input, safe_result)
            return safe_result

        self.context.add_turn(user_input, str(result))
        return result

    def _handle_single_question(self, question: str):
        return self.process(question)

    def _split_questions(self, text: str):
        parts = text.replace(" and ", "?").split("?")
        return [part.strip() for part in parts if part.strip()]

    def _calculate_age_from_text(self, text: str):
        import re
        from datetime import datetime

        match = re.search(r"(19\d{2}|20\d{2})", text)
        if not match:
            return None

        year = int(match.group(0))
        current_year = datetime.now().year
        return current_year - year

    def _convert_model_to_jessica(self, model_answer: str) -> str:
        if not model_answer:
            return "I could not determine an answer."

        forbidden = [
            "as an ai",
            "i am phi",
            "i am chatgpt",
            "language model",
            "trained by",
            "engineers",
            "developers",
        ]

        text = model_answer.lower()

        for phrase in forbidden:
            if phrase in text:
                return "I do not have enough information to answer that yet."

        cleaned = model_answer.replace("Assistant:", "").strip()
        return cleaned

    def _get_identity_answer(self, question: str):
        if "my name" in question:
            name = self.memory_beliefs.get_fact("user_name") or self.memory_beliefs.get("user_name")
            if name:
                return f"Your name is {name}."

        if "favorite color" in question:
            color = self.memory_beliefs.get_fact("favorite_color")
            if color:
                return f"Your favorite color is {color}."

        if "who created you" in question:
            creator = self.memory_beliefs.get_fact("creator") or self.memory_beliefs.get("creator")
            if creator:
                return f"{creator} created me."

        return None

    def _answer_from_beliefs(self, user_input: str) -> Optional[str]:
        """
        Try to answer from stored beliefs and memory.
        
        This now delegates identity questions to IdentityReasoner.
        Kept for backward compatibility and belief lookups.
        
        Args:
            user_input: Question asked
            
        Returns:
            Answer from beliefs, or None if not found
        """
        # Identity questions are now handled by IdentityReasoner (Phase 98.9)
        # This method is kept for general belief lookups and conflict checking
        return None


    def _capture_memory(self, user_input: str):
        """
        Capture and store user information.
        Phase 91: Also creates beliefs for identity consistency.
        """
        text = user_input.lower()

        # Name storage
        if "my name is" in text:
            start = text.find("my name is")
            name = user_input[start + len("my name is"):].strip()
            self.knowledge_store.set_fact("user.name", name)
            self.belief_store.update_belief("user", "name", name, confidence=1.0, source="interaction")

        # Birth year storage
        if "born in" in text:
            words = text.split()
            for word in words:
                if word.isdigit() and len(word) == 4:
                    year = int(word)
                    self.knowledge_store.set_fact("user.birth_year", year)
                    self.belief_store.update_belief("user", "birth_year", str(year), confidence=1.0, source="interaction")
                    break

        # Location storage
        if "i live in" in text:
            start = text.find("i live in")
            location = user_input[start + len("i live in"):].strip()
            self.knowledge_store.set_fact("user.location", location)
            self.belief_store.update_belief("user", "location", location, confidence=1.0, source="interaction")

        # Creator storage
        if "i am your creator" in text or "i created you" in text:
            name = self.knowledge_store.get_fact("user.name")
            if name:
                self.knowledge_store.set_fact("jessica.creator", name)
                self.belief_store.update_belief("system", "creator", name, confidence=1.0, source="interaction")

    def _capture_beliefs_from_input(self, user_input: str) -> None:
        """
        Phase 98.8: AGGRESSIVE belief capture from user input.
        Extracts and stores core facts that become absolute truth.
        """
        lower_input = user_input.lower()
        
        # Capture user name
        if "my name is" in lower_input:
            try:
                # Find what comes after "my name is"
                start_idx = lower_input.find("my name is")
                name_part = user_input[start_idx + len("my name is"):].strip()
                # Get first word as name
                name = name_part.split()[0] if name_part.split() else None
                if name:
                    self.memory_beliefs.set("user_name", name.capitalize())
            except Exception:
                pass
        
        # Capture creator information
        if "i created you" in lower_input or "i am your creator" in lower_input:
            user_name = self.memory_beliefs.get("user_name")
            if user_name:
                self.memory_beliefs.set("creator", user_name)
        
        # Capture birth date information (year/month/day)
        if "born" in lower_input or "birthday" in lower_input:
            try:
                year, month, day = self._extract_birth_info(user_input)
                if year:
                    self.memory_beliefs.set("birth_year", int(year))
                    self.memory_beliefs.set_fact("birth_year", int(year))
                if month:
                    self.memory_beliefs.set_fact("birth_month", int(month))
                if day:
                    self.memory_beliefs.set_fact("birth_day", int(day))
            except Exception:
                pass
        
        # Capture job/profession
        professions = ["engineer", "doctor", "teacher", "programmer", "designer", "artist", "lawyer", "nurse", "manager"]
        for prof in professions:
            if f"i am a {prof}" in lower_input or f"i am an {prof}" in lower_input or f"i'm a {prof}" in lower_input:
                self.memory_beliefs.set("profession", prof.capitalize())
                break
        
        # Capture hobbies/interests
        if "i like" in lower_input:
            try:
                parts = lower_input.split("i like", 1)[-1].strip().split()[0]
                if parts:
                    self.memory_beliefs.set("interest", parts.capitalize())
            except Exception:
                pass
        elif "i enjoy" in lower_input:
            try:
                parts = lower_input.split("i enjoy", 1)[-1].strip().split()[0]
                if parts:
                    self.memory_beliefs.set("interest", parts.capitalize())
            except Exception:
                pass

    def _extract_birth_info(self, text: str):
        text = text.lower()

        import re
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)

        months = {
            "january": 1, "february": 2, "march": 3,
            "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9,
            "october": 10, "november": 11, "december": 12,
        }

        month = None
        for name, num in months.items():
            if name in text:
                month = num

        day = None
        month_pattern = "|".join(months.keys())

        day_before_month = re.search(
            rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({month_pattern})\b",
            text,
        )
        day_after_month = re.search(
            rf"\b({month_pattern})\s+(\d{{1,2}})(?:st|nd|rd|th)?\b",
            text,
        )

        if day_before_month:
            day = int(day_before_month.group(1))
            month_name = day_before_month.group(2)
            month = months.get(month_name, month)
        elif day_after_month:
            month_name = day_after_month.group(1)
            day = int(day_after_month.group(2))
            month = months.get(month_name, month)

        if day is not None and (day < 1 or day > 31):
            day = None

        year = year_match.group(0) if year_match else None

        return year, month, day

    def _check_belief_priority_routing(self, user_input: str) -> Optional[str]:
        """
        Phase 98.8: ABSOLUTE PRIORITY ROUTING.
        Beliefs ALWAYS win over everything else.
        Returns answer if belief found, None otherwise.
        """
        lower_input = user_input.lower()
        
        # ===== What is YOUR name? =====
        if "your name" in lower_input and ("what" in lower_input or "who are you" in lower_input):
            return "My name is Jessica."
        
        # ===== What is MY name? =====
        if "my name" in lower_input and "what" in lower_input:
            name = self.memory_beliefs.get("user_name")
            if name:
                return f"Your name is {name}."
        
        # ===== Who created you? =====
        if "who created you" in lower_input or "who made you" in lower_input:
            creator = self.memory_beliefs.get("creator")
            if creator:
                return f"You ({creator}) created me."
            return "You created me."
        
        # ===== How old am I? =====
        if "how old am i" in lower_input or "my age" in lower_input:
            birth_year = self.memory_beliefs.get("birth_year")
            if birth_year:
                from datetime import datetime
                current_year = datetime.now().year
                age = current_year - birth_year
                return f"You are {age} years old."
        
        # ===== What do I do? / What's my job? =====
        if "my job" in lower_input or "my profession" in lower_input or "what do i do" in lower_input:
            profession = self.memory_beliefs.get("profession")
            if profession:
                return f"You are a {profession}."
        
        # ===== What are my interests? =====
        if "my interest" in lower_input or "what do i like" in lower_input or "what do i enjoy" in lower_input:
            interest = self.memory_beliefs.get("interest")
            if interest:
                return f"You like {interest}."
        
        return None

    def _block_model_dangerous_outputs(self, model_answer: str) -> str:
        """
        Phase 98.8: BLOCK model from saying dangerous things.
        Prevents identity confusion and contradiction.
        """
        if not model_answer:
            return model_answer
        
        lower_answer = model_answer.lower()
        
        # Block model claiming to be another AI
        dangerous_identities = ["phi", "gemini", "openai", "chatgpt", "claude", "gpt", "bard", "llama"]
        for identity in dangerous_identities:
            if f"i am {identity}" in lower_answer or f"i'm {identity}" in lower_answer:
                return "I am Jessica."
        
        # Block model overriding user identity
        user_name = self.memory_beliefs.get("user_name")
        if user_name and "name is" in lower_answer:
            if user_name.lower() not in lower_answer:
                # Model tried to override user name
                return f"Your name is {user_name}."
        
        # Block model claiming different creator
        creator = self.memory_beliefs.get("creator")
        if creator and ("creator" in lower_answer or "created" in lower_answer):
            if creator.lower() not in lower_answer:
                return f"You ({creator}) created me."
        
        return model_answer

    def _detect_belief_conflicts(self, model_answer: str, question: str) -> Optional[str]:
        """
        Phase 98.8: Detect conflicts between model and beliefs.
        Beliefs always win.
        """
        if not model_answer:
            return None
        
        lower_question = question.lower()
        lower_answer = model_answer.lower()
        
        # If asking about user name and model answer differs from belief
        if "name" in lower_question:
            user_name = self.memory_beliefs.get("user_name")
            if user_name and user_name.lower() not in lower_answer:
                return f"Your name is {user_name}."
        
        # If asking about creator and model answer differs
        if "creator" in lower_question or "created you" in lower_question:
            creator = self.memory_beliefs.get("creator")
            if creator and creator.lower() not in lower_answer:
                return f"You ({creator}) created me."
        
        # If asking about Jessica's identity
        if ("what is your name" in lower_question or "who are you" in lower_question) and "jessica" not in lower_answer:
            return "I am Jessica."
        
        return None

    def execute_proposal(self, proposal, user_input=None):
        """
        Execute an approved proposal.
        Phase 93: Action execution engine.

        Args:
            proposal: ActionProposal object with actions to execute
            user_input: Optional original user input for context

        Returns:
            List of execution results
        """
        # Use user_input if provided, otherwise use description
        context = user_input if user_input else proposal.description
        return self.executor.execute(proposal.actions, context)
