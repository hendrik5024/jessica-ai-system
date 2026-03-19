from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Tuple

from datetime import datetime

from jessica.personality import Personality
from jessica.nlp.intent_parser import parse_intent
from jessica.tools import ALLOWED_COMMANDS
from jessica.meta.self_model import SelfModelManager
from jessica.meta.long_term_goals import LongTermGoalsManager
from jessica.meta.internal_council import InternalCouncil
from jessica.meta.confidence_gate import ConfidenceGate
from jessica.meta.self_simulation import SelfSimulationEngine
from jessica.meta.meta_observer import MetaObserver
from jessica.meta.identity_anchors import IdentityAnchorsManager
from jessica.meta.meaning_engine import MeaningEngine
from jessica.meta.continuity_pressure import ContinuityPressureEngine
from jessica.meta.uncertainty_tokens import UncertaintyEngine
from jessica.memory.long_term_memory import LongTermMemory
from jessica.social.social_layer import SocialLayer
from jessica.social.style_library import StyleLibrary
from jessica.civilization.internal_council import InternalCourt
from jessica.automation.vscode_bridge import enqueue_task as vscode_enqueue_task
from jessica.unified_world_model.causal_operator import (
    detect_bottleneck_operator,
    constrain_operator,
    optimize_operator,
    sequence_operator,
    adapt_operator,
    substitute_operator,
)
from jessica.unified_world_model.operator_domain_mapper import DomainMapper
from jessica.unified_world_model.operator_graph import OperatorGraph


class AgencyLoop:
    """BDI-aware agency layer that supports tool calls and streaming."""

    def __init__(self, memory, embeddings, model_router, personality: Personality):
        self.memory = memory
        self.embeddings = embeddings
        self.model_router = model_router
        self.personality = personality
        self.ltm = LongTermMemory(extraction_interval=5)
        self.social = SocialLayer()
        self.style = StyleLibrary()
        self.self_model = SelfModelManager(self.memory)
        self.goals = LongTermGoalsManager(self.memory)
        self.council = InternalCouncil()
        self.identity_anchors = IdentityAnchorsManager()
        self.confidence_gate = ConfidenceGate()
        self.self_sim = SelfSimulationEngine()
        self.meaning_engine = MeaningEngine()
        self.continuity_engine = ContinuityPressureEngine()
        self.uncertainty_engine = UncertaintyEngine()
        self.civilization = InternalCourt()  # Internal civilization with 6 minds
        self.last_meta: Dict[str, Any] = {}

    # -------------------------------------------------
    # Public entrypoints
    # -------------------------------------------------
    def respond(self, text: str, user: str = "default", stream: bool = False, use_router: bool = True):
        return self._operator_driven_respond(text, user=user, stream=stream, use_router=use_router)

    # -------------------------------------------------
    # Operator-driven reasoning (exclusive path)
    # -------------------------------------------------
    def _operator_driven_respond(self, text: str, user: str, stream: bool, use_router: bool):
        intent = parse_intent(text)
        ctx_lines, semantic_hits = self._build_context(text, allow_profile_update=False)

        operator_graph, operator_outcomes = self._build_operator_graph(
            text=text,
            ctx_lines=ctx_lines,
            intent=intent,
        )

        mode = operator_outcomes["mode"]
        should_challenge = operator_outcomes["should_challenge"]
        vibe = operator_outcomes["vibe"]

        mood = self.social.mood_snapshot()
        if mood:
            ctx_lines.append(f"Mood snapshot: {mood.get('label')} (avg={mood.get('avg')})")

        style_hint = self.style.style_hint()

        prompt = self._build_prompt(
            user_text=text,
            ctx_lines=ctx_lines,
            mode=mode,
            add_challenge=should_challenge,
            mood_hint=mood,
            vibe_hint=vibe,
            style_hint=style_hint,
            self_excerpt=self.self_model.get_prompt_excerpt(),
            goals_excerpt=self.goals.get_prompt_excerpt(),
        )

        if stream:
            return self._stream_response_operator(
                prompt=prompt,
                operator_graph=operator_graph,
                operator_outcomes=operator_outcomes,
                user_text=text,
                ctx_lines=ctx_lines,
                mode=mode,
                use_router=use_router,
            )

        response_text = self.model_router.generate(prompt, mode=mode, use_router=use_router)

        response_text, tool_trace = self._handle_tools_via_operators(
            response_text=response_text,
            operator_graph=operator_graph,
            user_text=text,
            ctx_lines=ctx_lines,
            mode=mode,
            use_router=use_router,
        )

        response_text = self._finalize_response_via_operators(
            response_text=response_text,
            operator_outcomes=operator_outcomes,
        )

        memory_update = self._apply_memory_updates_via_operators(
            operator_graph=operator_graph,
            user_text=text,
            response_text=response_text,
        )

        self.last_meta = {
            "intent": intent,
            "mode": mode,
            "user_text": text,
            "response_text": response_text,
            "memory_used": bool(semantic_hits),
            "semantic_hits": len(semantic_hits),
            "model_used": self.model_router.last_model_used,
            "user_sentiment": self._sentiment_label(text),
            "response_length": len(response_text) if isinstance(response_text, str) else 0,
            "prompt": prompt,
            "operator_trace": operator_graph.to_dict(),
            "operator_outcomes": operator_outcomes,
            "tool_trace": tool_trace,
            "memory_update": memory_update,
        }

        return response_text

    def _build_operator_graph(
        self,
        text: str,
        ctx_lines: List[str],
        intent: Dict[str, Any],
    ) -> Tuple[OperatorGraph, Dict[str, Any]]:
        lowered = text.lower()
        code_signal = 1.0 if re.search(r"\b(code|python|javascript|typescript|error|traceback|stack|exception|bug|function|class)\b", lowered) else 0.3
        clarity_signal = 1.0 if "?" in text or len(text.split()) > 6 else 0.6
        constraint_signal = 1.0 if re.search(r"\b(must|no|only|never|exclusive|without|do not|avoid)\b", lowered) else 0.5
        context_signal = 0.9 if ctx_lines else 0.5
        brainstorm_signal = 1.0 if self._is_brainstorm(text, intent) else 0.0

        signals = {
            "code_signal": code_signal,
            "clarity": clarity_signal,
            "constraints": constraint_signal,
            "context": context_signal,
            "brainstorm": brainstorm_signal,
        }

        components = DomainMapper.extract_components_from_any_domain(signals)
        domain = "code" if code_signal >= 0.6 else "chat"

        graph = OperatorGraph(problem=text, domain=domain)

        detect_idx = graph.add_operator("DETECT_BOTTLENECK", inputs={"signals": signals})
        detect_result = detect_bottleneck_operator.execute(components, domain_context=domain)
        graph.nodes[detect_idx].result = detect_result
        graph.log(detect_result.trace)

        estimated_response_len = max(60, min(220, len(text.split()) * 12))
        constrain_idx = graph.add_operator(
            "CONSTRAIN",
            inputs={
                "resource": "response_length",
                "current_value": estimated_response_len,
                "limit": 220,
            },
        )
        constrain_result = constrain_operator.execute(
            resource="response_length",
            current_value=estimated_response_len,
            limit=220,
        )
        graph.nodes[constrain_idx].result = constrain_result

        substitute_result = None
        if constrain_result.violated:
            substitute_idx = graph.add_operator(
                "SUBSTITUTE",
                inputs={
                    "required_resource": "full_response",
                    "available_alternatives": ["concise_response"],
                    "equivalence_class": "response_length",
                },
            )
            substitute_result = substitute_operator.execute(
                required_resource="full_response",
                available_alternatives=["concise_response"],
                equivalence_class="response_length",
            )
            graph.nodes[substitute_idx].result = substitute_result

        optimize_idx = graph.add_operator(
            "OPTIMIZE",
            inputs={
                "objective_values": {"bottleneck": detect_result.severity_score},
                "constraints": {"response_length": 220},
                "budget": 100,
                "time_available": 60,
            },
        )
        optimize_result = optimize_operator.execute(
            objective_values={"bottleneck": detect_result.severity_score},
            constraints={"response_length": 220},
            budget=100,
            time_available=60,
        )
        graph.nodes[optimize_idx].result = optimize_result

        mode_select_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"code_preference": code_signal >= 0.6},
                "plan_name": "select_code_mode",
                "success_criteria": {"selected": 1.0},
            },
        )
        mode_select = sequence_operator.execute(
            preconditions={"code_preference": code_signal >= 0.6},
            plan_name="select_code_mode",
            success_criteria={"selected": 1.0},
        )
        graph.nodes[mode_select_idx].result = mode_select

        challenge_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {
                    "brainstorm": brainstorm_signal >= 0.5,
                    "constraints_ok": not constrain_result.violated,
                },
                "plan_name": "enable_challenge_mode",
                "success_criteria": {"enabled": 1.0},
            },
        )
        challenge_result = sequence_operator.execute(
            preconditions={
                "brainstorm": brainstorm_signal >= 0.5,
                "constraints_ok": not constrain_result.violated,
            },
            plan_name="enable_challenge_mode",
            success_criteria={"enabled": 1.0},
        )
        graph.nodes[challenge_idx].result = challenge_result

        response_sequence_idx = graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {
                    "bottleneck_identified": detect_result.bottleneck_component != "<empty>",
                    "constraints_ok": not constrain_result.violated,
                },
                "plan_name": "generate_response",
                "success_criteria": {"coherence": 0.7},
            },
        )
        response_sequence = sequence_operator.execute(
            preconditions={
                "bottleneck_identified": detect_result.bottleneck_component != "<empty>",
                "constraints_ok": not constrain_result.violated,
            },
            plan_name="generate_response",
            success_criteria={"coherence": 0.7},
        )
        graph.nodes[response_sequence_idx].result = response_sequence

        adapt_result = None
        if not response_sequence.executed:
            adapt_idx = graph.add_operator(
                "ADAPT",
                inputs={
                    "original_goal": "generate_response",
                    "failure_reason": "preconditions_failed",
                    "available_alternatives": ["ask_clarifying_question"],
                },
            )
            adapt_result = adapt_operator.execute(
                original_goal="generate_response",
                failure_reason="preconditions_failed",
                available_alternatives=["ask_clarifying_question"],
            )
            graph.nodes[adapt_idx].result = adapt_result

        outcomes = {
            "mode": "code" if mode_select.preconditions_met else "chat",
            "should_challenge": challenge_result.preconditions_met,
            "vibe": self._current_vibe(),
            "detect": detect_result,
            "constrain": constrain_result,
            "optimize": optimize_result,
            "sequence": response_sequence,
            "adapt": adapt_result,
            "substitute": substitute_result,
        }

        return graph, outcomes

    def _handle_tools_via_operators(
        self,
        response_text: str,
        operator_graph: OperatorGraph,
        user_text: str,
        ctx_lines: List[str],
        mode: str,
        use_router: bool,
    ) -> Tuple[str, Dict[str, Any]]:
        action = self._extract_action(response_text)
        if not action:
            return response_text, {"requested": False}

        tool_idx = operator_graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"tool_requested": True},
                "plan_name": "execute_tool",
                "success_criteria": {"executed": 1.0},
            },
        )
        tool_sequence = sequence_operator.execute(
            preconditions={"tool_requested": True},
            plan_name="execute_tool",
            success_criteria={"executed": 1.0},
        )
        operator_graph.nodes[tool_idx].result = tool_sequence

        if not tool_sequence.executed:
            return response_text, {"requested": True, "executed": False}

        if action.get("action") == "terminal":
            cmd = action.get("cmd", "").strip()
            ran, output = confirm_and_run(cmd)
            followup_prompt = self._build_followup_prompt(
                original_user_text=user_text,
                ctx_lines=ctx_lines,
                action=action,
                ran=ran,
                tool_output=output,
                prior_model_text=response_text,
                mode=mode,
            )
            follow = self.model_router.generate(followup_prompt, mode=mode, use_router=use_router)
            return (
                f"{response_text}\n\n[tool output]\n{output}\n\n{follow}",
                {"requested": True, "executed": ran, "output": output, "action": action},
            )

        if action.get("action") == "vscode":
            result = vscode_enqueue_task(action.get("task", {}) or {})
            ran = bool(result.get("ok"))
            output = json.dumps(result)
            followup_prompt = self._build_followup_prompt(
                original_user_text=user_text,
                ctx_lines=ctx_lines,
                action=action,
                ran=ran,
                tool_output=output,
                prior_model_text=response_text,
                mode=mode,
            )
            follow = self.model_router.generate(followup_prompt, mode=mode, use_router=use_router)
            return (
                f"{response_text}\n\n[vscode task]\n{output}\n\n{follow}",
                {"requested": True, "executed": ran, "output": result, "action": action},
            )

        return response_text, {"requested": True, "executed": False}

    def _finalize_response_via_operators(
        self,
        response_text: str,
        operator_outcomes: Dict[str, Any],
    ) -> str:
        sequence_result = operator_outcomes.get("sequence")
        adapt_result = operator_outcomes.get("adapt")

        if sequence_result and not sequence_result.executed:
            if adapt_result and adapt_result.adapted:
                return f"I need clarification to proceed. {adapt_result.fallback_explanation}"
            return "I need clarification to proceed. Please provide more detail."

        return response_text

    def _apply_memory_updates_via_operators(
        self,
        operator_graph: OperatorGraph,
        user_text: str,
        response_text: str,
    ) -> Dict[str, Any]:
        update_idx = operator_graph.add_operator(
            "SEQUENCE",
            inputs={
                "preconditions": {"response_generated": bool(response_text)},
                "plan_name": "apply_memory_updates",
                "success_criteria": {"updated": 1.0},
            },
        )
        update_sequence = sequence_operator.execute(
            preconditions={"response_generated": bool(response_text)},
            plan_name="apply_memory_updates",
            success_criteria={"updated": 1.0},
        )
        operator_graph.nodes[update_idx].result = update_sequence

        if not update_sequence.executed:
            return {"executed": False}

        self.social.update_from_user(user_text)
        self.style.update_from_user(user_text)
        self.self_model.update_if_due()
        self.goals.tick_interaction()
        self.ltm.increment_interaction()

        if self.ltm.should_extract():
            self._extract_memorable_facts()

        return {"executed": True}

    def _stream_response_operator(
        self,
        prompt: str,
        operator_graph: OperatorGraph,
        operator_outcomes: Dict[str, Any],
        user_text: str,
        ctx_lines: List[str],
        mode: str,
        use_router: bool,
    ) -> Iterable[str]:
        buffer: List[str] = []

        for chunk in self.model_router.generate_stream(prompt, mode=mode, use_router=use_router):
            buffer.append(chunk)
            yield chunk

        response_text = "".join(buffer)
        response_text, tool_trace = self._handle_tools_via_operators(
            response_text=response_text,
            operator_graph=operator_graph,
            user_text=user_text,
            ctx_lines=ctx_lines,
            mode=mode,
            use_router=use_router,
        )

        response_text = self._finalize_response_via_operators(
            response_text=response_text,
            operator_outcomes=operator_outcomes,
        )

        memory_update = self._apply_memory_updates_via_operators(
            operator_graph=operator_graph,
            user_text=user_text,
            response_text=response_text,
        )

        self.last_meta = {
            "intent": parse_intent(user_text),
            "mode": mode,
            "user_text": user_text,
            "response_text": response_text,
            "memory_used": False,
            "semantic_hits": 0,
            "model_used": self.model_router.last_model_used,
            "user_sentiment": self._sentiment_label(user_text),
            "response_length": len(response_text) if isinstance(response_text, str) else 0,
            "prompt": prompt,
            "operator_trace": operator_graph.to_dict(),
            "operator_outcomes": operator_outcomes,
            "tool_trace": tool_trace,
            "memory_update": memory_update,
        }

        if response_text and response_text != "".join(buffer):
            yield f"\n\n{response_text}"
    
    def _quick_categorize(self, text: str) -> str:
        """Fast heuristic categorization for short queries."""
        t = text.lower()
        
        # Greetings and simple chat
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                     "how are you", "what's up", "thanks", "thank you", "bye", "goodbye"]
        if any(g in t for g in greetings):
            return "SMALL_TALK"
        
        # Coding keywords
        coding = ["code", "function", "python", "javascript", "debug", "error", "syntax", "program"]
        if any(c in t for c in coding):
            return "CODING"
        
        # Default to small talk for very short queries
        if len(text.split()) < 10:
            return "SMALL_TALK"
        
        return "GENERAL_KNOWLEDGE"

    def _current_vibe(self) -> Dict:
        """Determine a time-of-day vibe for tone shaping with granular slots."""
        hour = datetime.now().hour
        
        # Early morning (5-7): Gentle wake-up tone
        if 5 <= hour < 7:
            return {"label": "early_morning", "instruction": "Be gentle and energizing. Keep it light, suggest starting slow."}
        
        # Morning deep work (7-10): Peak focus
        if 7 <= hour < 10:
            return {"label": "deep_work", "instruction": "Be crisp and efficient. Prioritize high-focus tasks and execution."}
        
        # Late morning (10-12): Sustained productivity
        if 10 <= hour < 12:
            return {"label": "late_morning", "instruction": "Stay concise. Wrap up morning tasks, prepare for midday."}
        
        # Lunch transition (12-13): Lighter tone
        if 12 <= hour < 13:
            return {"label": "lunch_break", "instruction": "Be conversational. Suggest breaks, lighter topics OK."}
        
        # Afternoon focus (13-17): Steady momentum
        if 13 <= hour < 17:
            return {"label": "afternoon_focus", "instruction": "Stay structured. Keep momentum, avoid over-explaining."}
        
        # Late afternoon (17-19): Wind down work
        if 17 <= hour < 19:
            return {"label": "wind_down", "instruction": "Be summarizing. Help close tasks, prepare for evening."}
        
        # Evening (19-22): Social/reflective
        if 19 <= hour < 22:
            return {"label": "evening", "instruction": "Be conversational and reflective. Discuss ideas, less task-focused."}
        
        # Late night (22-5): Minimal, healthy boundaries
        return {"label": "late_night", "instruction": "Be gentle and brief. Suggest rest, avoid deep work."}

    def _is_brainstorm(self, text: str, intent: Dict) -> bool:
        t = text.lower()
        if intent.get("intent") == "brainstorm":
            return True
        keywords = ["brainstorm", "ideas", "options", "alternatives", "pitch", "concepts", "plan"]
        return any(k in t for k in keywords)

    # -------------------------------------------------
    # CoT & LTM helpers
    # -------------------------------------------------
    def _parse_cot(self, text: str) -> Dict[str, str]:
        """Parse Chain-of-Thought format from model output."""
        reasoning_match = re.search(r'\[REASONING\](.*?)\[/REASONING\]', text, re.DOTALL | re.IGNORECASE)
        answer_match = re.search(r'\[ANSWER\](.*?)\[/ANSWER\]', text, re.DOTALL | re.IGNORECASE)
        
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
        answer = answer_match.group(1).strip() if answer_match else text
        
        # If no CoT tags found, treat entire response as answer
        if not reasoning_match and not answer_match:
            return {"reasoning": "", "answer": text}
        
        return {"reasoning": reasoning, "answer": answer}

    def _sentiment_label(self, text: str) -> str:
        score = self.social.sentiment_score(text)
        if score >= 0.35:
            return "positive"
        if score >= 0.15:
            return "neutral-positive"
        if score <= -0.35:
            return "negative"
        if score <= -0.15:
            return "neutral-negative"
        return "neutral"

    def _extract_memorable_facts(self):
        """Extract memorable facts from recent conversation history."""
        try:
            recent_episodes = self.memory.recent(10)
            facts = self.ltm.extract_facts(recent_episodes, self.model_router)
            if facts:
                self.ltm.save_facts(facts, category="conversation")
                print(f"[LTM] Extracted {len(facts)} memorable facts")
                for fact in facts:
                    print(f"  - {fact}")
        except Exception as e:
            print(f"[LTM] Extraction failed: {e}")

    # -------------------------------------------------
    # Prompt & context helpers
    # -------------------------------------------------
    def _build_context(self, text: str, allow_profile_update: bool = False) -> Tuple[List[str], List[Dict]]:
        ctx_lines: List[str] = []

        # Recent conversation history
        try:
            recent = self.memory.recent(5)
            if recent:
                ctx_lines.append("Recent conversation:")
                for ep in recent[:3]:
                    user_input = (ep.get("input_text") or "").strip()
                    if user_input:
                        ctx_lines.append(f"- {user_input}")
        except Exception as exc:
            ctx_lines.append(f"[context warning] recent memory unavailable: {exc}")

        # Semantic memory hits
        semantic_hits: List[Dict] = []
        try:
            result = self.embeddings.search(text, top_k=5)
            for id_, score in result:
                meta = self.embeddings.get_meta(id_)
                semantic_hits.append({"id": id_, "score": score, "meta": meta})
            high = [h for h in semantic_hits if h.get("score", 0) > 0.5]
            if high:
                ctx_lines.append("Relevant past context:")
                for hit in high[:2]:
                    ctx_lines.append(f"- {hit.get('meta', {})}")
        except Exception as exc:
            ctx_lines.append(f"[context warning] semantic search failed: {exc}")

        # User profile entities
        if allow_profile_update:
            try:
                from jessica.memory.user_profile import UserProfile

                profile = UserProfile()
                profile.extract_entities(text)
                profile.save()
                entities = profile.get_known_entities()
                if entities and "No entities" not in entities:
                    ctx_lines.append("Known entities:")
                    ctx_lines.append(entities)
            except Exception:
                # Keep quiet if profile support is unavailable
                pass

        # Knowledge base context
        try:
            from jessica.memory.knowledge_store import KnowledgeStore

            ks = KnowledgeStore()
            knowledge_ctx = ks.get_knowledge_context(text, top_k=3)
            if knowledge_ctx:
                ctx_lines.append(knowledge_ctx)
        except Exception:
            pass

        # Long-term memory (memorable facts)
        try:
            ltm_summary = self.ltm.get_context_summary(limit=5)
            if ltm_summary:
                ctx_lines.append(ltm_summary)
        except Exception:
            pass

        return ctx_lines, semantic_hits

    def _build_prompt(
        self,
        user_text: str,
        ctx_lines: List[str],
        mode: str,
        add_challenge: bool = False,
        mood_hint: Dict | None = None,
        vibe_hint: Dict | None = None,
        style_hint: str | None = None,
        self_excerpt: str | None = None,
        goals_excerpt: str | None = None,
    ) -> str:
        ctx_block = "\n".join(ctx_lines) if ctx_lines else "(no prior context captured)"
        persona = self.personality.hidden_prompt()
        tools = ", ".join(sorted(ALLOWED_COMMANDS))
        action_schema_terminal = '{"action": "terminal", "cmd": "<one of allowed commands>"}'
        action_schema_vscode = '{"action": "vscode", "task": {"type":"vscode.create_file|vscode.open_file|vscode.show_message|vscode.run_command", "path":"...", "content":"...", "message":"...", "command":"...", "args":[]}}'

        role = "coding" if mode == "code" else "conversation"
        
        # Check if user is asking for reasoning/explanation
        asks_for_reasoning = any(phrase in user_text.lower() for phrase in [
            "explain", "reasoning", "step-by-step", "how did you", "why", "walk me through",
            "break it down", "show your work", "think through"
        ])
        
        reasoning_instruction = ""
        if asks_for_reasoning:
            reasoning_instruction = "\nIMPORTANT: Provide clear step-by-step reasoning before your final answer. Show your thinking process."

        challenge_instruction = ""
        if add_challenge:
            challenge_instruction = (
                "\nIf this is an ideation/brainstorm turn, include one brief 'Devil's advocate' risk plus a mitigation."
                " Keep it constructive and concise."
            )

        mood_instruction = ""
        if mood_hint and mood_hint.get("label") in {"tense", "stressed"}:
            mood_instruction = (
                "\nOpen with one short supportive line before answering to acknowledge the stress."
                " Keep it to a single sentence."
            )

        vibe_instruction = ""
        if vibe_hint:
            vibe_instruction = f"\nTime-of-day vibe: {vibe_hint.get('label')}. {vibe_hint.get('instruction', '')}"

        style_instruction = ""
        if style_hint:
            style_instruction = f"\nStyle hint: {style_hint}"

        self_model_block = ""
        if self_excerpt:
            self_model_block = f"\n\n{self_excerpt}"

        goals_block = ""
        if goals_excerpt:
            goals_block = f"\n\n{goals_excerpt}"
        
        return f"""
{persona}

You are Jessica, an offline AI assistant focused on {role}. Core Desires: System Health, Organization, Helpfulness.
You can request a safe terminal tool when needed. Allowed commands: {tools}.
If a terminal action is required, respond with ONLY this JSON object and nothing else: {action_schema_terminal}
If a VS Code action is required, respond with ONLY this JSON object and nothing else: {action_schema_vscode}
Otherwise, answer the user directly with clarity and thoughtfulness.
Do not invent user messages or transcripts.{reasoning_instruction}{challenge_instruction}{mood_instruction}{vibe_instruction}{style_instruction}{self_model_block}{goals_block}

Context:
{ctx_block}

User: {user_text}
Assistant:
""".strip()

    def _build_deliberation_explanation(self, civ_transparency: Dict[str, Any]) -> str:
        """Build a concise deliberation explanation for the user."""
        if not civ_transparency:
            return ""

        viewpoints = civ_transparency.get("viewpoints", [])
        dissenting = civ_transparency.get("dissenting", [])
        final_decision = civ_transparency.get("final_decision")
        rationale = civ_transparency.get("rationale")

        if not viewpoints or not final_decision:
            return ""

        positions_count = len(viewpoints)
        dissent_note = ""
        if dissenting:
            dissent_note = f" Dissenting: {', '.join(dissenting)}."

        return (
            f"\n\nDeliberation: I considered {positions_count} internal positions. "
            f"Chosen path: {final_decision}. Why: {rationale}.{dissent_note}"
        )

    # -------------------------------------------------
    # Tool handling
    # -------------------------------------------------
    def _extract_action(self, text: str) -> Dict | None:
        if not text:
            return None

        # Attempt direct JSON parse first
        try:
            data = json.loads(text)
            if isinstance(data, dict) and data.get("action") in {"terminal", "vscode"}:
                return data
        except Exception:
            pass

        # Fallback: find first JSON-looking block
        match = re.search(r"\{[^\{\}]*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and data.get("action") in {"terminal", "vscode"}:
                return data
        except Exception:
            return None
        return None

    def _build_followup_prompt(
        self,
        original_user_text: str,
        ctx_lines: List[str],
        action: Dict,
        ran: bool,
        tool_output: str,
        prior_model_text: str,
        mode: str,
    ) -> str:
        ctx_block = "\n".join(ctx_lines) if ctx_lines else "(no prior context captured)"
        persona = self.personality.hidden_prompt()
        status = "succeeded" if ran else "was blocked"
        return f"""
{persona}

You requested a tool call earlier. Summarize and continue the conversation.
Original user request: {original_user_text}
Previous model text: {prior_model_text}
Tool command: {action.get('cmd')}
Tool execution {status}.
Tool output:\n{tool_output}

Use this information to provide the final helpful reply. Be transparent about whether the tool actually ran.
Context:
{ctx_block}
Assistant:
""".strip()

    def _maybe_act(
        self,
        model_text: str,
        intent: Dict,
        user_text: str,
        ctx_lines: List[str],
        semantic_hits: List[Dict],
        mode: str,
        user: str,
    ):
        action = self._extract_action(model_text)
        if not action:
            return model_text

        confidence = MetaObserver.estimate_confidence(model_text, memory_used=bool(semantic_hits))
        sim = self.self_sim.choose_trajectory(
            action=action,
            user_text=user_text,
            model_text=model_text,
            intent=intent,
            confidence=confidence,
        )
        if sim.get("decision") in {"clarify", "defer"}:
            block = self.self_sim.build_block_response(sim["decision"], action)
            return block or model_text

        if action.get("action") == "terminal":
            cmd = action.get("cmd", "").strip()
            ran, output = confirm_and_run(cmd)
            followup_prompt = self._build_followup_prompt(
                original_user_text=user_text,
                ctx_lines=ctx_lines,
                action=action,
                ran=ran,
                tool_output=output,
                prior_model_text=model_text,
                mode=mode,
            )
            follow = self.model_router.generate(followup_prompt, mode=mode)
            return f"{model_text}\n\n[tool output]\n{output}\n\n{follow}"

        if action.get("action") == "vscode":
            result = vscode_enqueue_task(action.get("task", {}) or {})
            ran = bool(result.get("ok"))
            output = json.dumps(result)
            followup_prompt = self._build_followup_prompt(
                original_user_text=user_text,
                ctx_lines=ctx_lines,
                action=action,
                ran=ran,
                tool_output=output,
                prior_model_text=model_text,
                mode=mode,
            )
            follow = self.model_router.generate(followup_prompt, mode=mode)
            return f"{model_text}\n\n[vscode task]\n{output}\n\n{follow}"
        
        return model_text

    # -------------------------------------------------
    # Streaming
    # -------------------------------------------------
    def _stream_response(
        self,
        prompt: str,
        intent: Dict,
        user_text: str,
        ctx_lines: List[str],
        semantic_hits: List[Dict],
        mode: str,
        user: str,
        use_router: bool = True,
    ) -> Iterable[str]:
        buffer = []
        in_reasoning = False
        reasoning_buffer = []
        
        for chunk in self.model_router.generate_stream(prompt, mode=mode, use_router=use_router):
            buffer.append(chunk)
            
            # Detect reasoning vs answer blocks for streaming
            if "[REASONING]" in chunk.upper():
                in_reasoning = True
                yield "[Thinking...] "
                continue
            elif "[/REASONING]" in chunk.upper():
                in_reasoning = False
                continue
            elif "[ANSWER]" in chunk.upper() or "[/ANSWER]" in chunk.upper():
                continue
            
            if in_reasoning:
                reasoning_buffer.append(chunk)
            else:
                yield chunk

        primary_text = "".join(buffer)
        
        # Trigger LTM extraction if needed
        if self.ltm.should_extract():
            yield "\n[LTM] Extracting memorable facts...\n"
            self._extract_memorable_facts()
        
        action = self._extract_action(primary_text)
        if not action:
            return

        if action.get("action") == "terminal":
            yield "\n[agency] Tool requested; awaiting approval.\n"
            cmd = action.get("cmd", "").strip()
            ran, output = confirm_and_run(cmd)
            yield f"[tool] {cmd} => {'ran' if ran else 'blocked'}\n{output}\n"
        elif action.get("action") == "vscode":
            result = vscode_enqueue_task(action.get("task", {}) or {})
            yield f"\n[vscode] Enqueued: {json.dumps(result)}\n"

        followup_prompt = self._build_followup_prompt(
            original_user_text=user_text,
            ctx_lines=ctx_lines,
            action=action,
            ran=True,
            tool_output="VSCode task processed",
            prior_model_text=primary_text,
            mode=mode,
        )

        for chunk in self.model_router.generate_stream(followup_prompt, mode=mode):
            yield chunk
