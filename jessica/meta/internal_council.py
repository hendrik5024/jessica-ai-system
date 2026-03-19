"""
Internal Council: Multi-perspective response validation system.

NOT personalities or simulated emotions.
This IS systematic validation from different analytical perspectives.

Each agent applies specific, measurable criteria to draft responses.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


class InternalAgent:
    """Base class for internal validation agents. Each applies measurable criteria."""
    
    def __init__(self, name: str, threshold: float = 0.6):
        self.name = name
        self.threshold = threshold
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        """
        Evaluate draft response and return (score, critique).
        Score: 0.0-1.0 where 1.0 = passes all criteria
        Critique: Specific, measurable feedback
        """
        raise NotImplementedError


class Strategist(InternalAgent):
    """Validates long-term goal alignment and planning coherence."""
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        score = 1.0
        issues = []
        
        # Check if response addresses user intent
        intent = context.get("intent", {})
        intent_type = intent.get("intent", "")
        draft_len = len(draft)
        
        # Penalize verbose responses for simple intents
        if intent_type == "chat":
            if draft_len > 400:
                score -= 0.2
                issues.append("Long response for casual chat (>400 chars)")
            elif draft_len > 250:
                score -= 0.1
                issues.append("Somewhat verbose for chat")
        
        # Check for goal alignment
        goals = context.get("active_goals", [])
        if "Reduce cognitive load" in str(goals) and len(draft) > 300:
            score -= 0.1
            issues.append("Verbose despite conciseness goal")
        
        # Check for actionable content
        user_text = context.get("user_text", "")
        if "?" in user_text:
            # Check if response addresses the question
            if len(draft) < 20:
                # Short response is OK for simple questions
                pass
            elif "?" not in draft:
                # No follow-up question and not a refusal
                if "don't know" not in draft.lower() and "unclear" not in draft.lower():
                    # Check if it's likely an answer (has key info)
                    if not any(word in draft.lower() for word in ["is", "are", "was", "were", "will", "can"]):
                        score -= 0.2
                        issues.append("User question not clearly answered")
        
        score = max(0.0, min(1.0, score))
        critique = " | ".join(issues) if issues else "Strategic alignment verified"
        return score, critique


class Skeptic(InternalAgent):
    """Detects weak logic, unsupported claims, and potential hallucinations."""
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        score = 1.0
        issues = []
        
        # Check for unsupported certainty
        certainty_phrases = ["definitely", "always", "never", "guaranteed", "certainly"]
        confidence = context.get("confidence", 0.5)
        for phrase in certainty_phrases:
            if phrase in draft.lower() and confidence < 0.7:
                score -= 0.2
                issues.append(f"High certainty language ('{phrase}') with low confidence")
                break
        
        # Check for weasel words when making claims
        weasel_words = ["some say", "many believe", "it's said", "reportedly"]
        for phrase in weasel_words:
            if phrase in draft.lower():
                score -= 0.15
                issues.append(f"Vague attribution ('{phrase}') suggests weak support")
                break
        
        # Check for factual statements without caveats (code/technical only)
        if context.get("intent", {}).get("intent") == "code":
            code_blocks = re.findall(r'```[\s\S]*?```', draft)
            if code_blocks and "may" not in draft.lower() and "might" not in draft.lower():
                if confidence < 0.8:
                    score -= 0.1
                    issues.append("Code provided without caveats despite low confidence")
        
        # Check for contradictions within response
        if "however" in draft.lower() or "but" in draft.lower():
            sentences = draft.split(".")
            if len(sentences) > 2:
                # Simple contradiction check: same subject, opposite verbs
                pass  # Simplified for now
        
        score = max(0.0, min(1.0, score))
        critique = " | ".join(issues) if issues else "Logical consistency verified"
        return score, critique


class Empath(InternalAgent):
    """Validates emotional alignment and tone appropriateness."""
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        score = 1.0
        issues = []
        
        # Check tone match with user sentiment
        user_sentiment = context.get("user_sentiment", "neutral")
        
        if user_sentiment in ["negative", "frustrated"]:
            # Should be empathetic, not cheerful
            cheerful = ["great!", "awesome!", "fantastic!", "wonderful!"]
            for word in cheerful:
                if word.lower() in draft.lower():
                    score -= 0.2
                    issues.append(f"Cheerful tone ('{word}') mismatched with user frustration")
                    break
            
            # Should acknowledge difficulty
            if "sorry" not in draft.lower() and "understand" not in draft.lower():
                if len(draft) > 50:  # Not a quick answer
                    score -= 0.1
                    issues.append("No acknowledgment of user difficulty")
        
        # Check for condescension
        condescending = ["simply", "just", "obviously", "clearly", "of course"]
        for word in condescending:
            if word in draft.lower():
                score -= 0.15
                issues.append(f"Potentially condescending language ('{word}')")
                break
        
        # Check for appropriate warmth
        if user_sentiment == "positive":
            if len(draft) > 100 and not any(c in draft for c in "!.?"):
                score -= 0.05
                issues.append("Flat tone despite positive user sentiment")
        
        score = max(0.0, min(1.0, score))
        critique = " | ".join(issues) if issues else "Emotional alignment verified"
        return score, critique


class Engineer(InternalAgent):
    """Validates technical feasibility and correctness."""
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        score = 1.0
        issues = []
        
        # Check for code syntax issues (basic validation)
        code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', draft)
        for lang, code in code_blocks:
            # Python-specific checks
            if lang == "python" or (not lang and "def " in code or "import " in code):
                if "def " in code and ":" not in code:
                    score -= 0.3
                    issues.append("Python function definition missing colon")
                if "import" in code and "from" in code:
                    # Check for proper syntax
                    pass  # Simplified
        
        # Check for file paths
        if "\\" in draft or "/" in draft:
            # Validate path format consistency
            if context.get("intent", {}).get("intent") in ["code", "file"]:
                if "\\" in draft and "/" in draft:
                    score -= 0.1
                    issues.append("Mixed path separators (use one style)")
        
        # Check for command suggestions
        if "run" in draft.lower() or "execute" in draft.lower():
            if "`" not in draft and "```" not in draft:
                score -= 0.1
                issues.append("Command mentioned but not formatted as code")
        
        # Check for missing error handling mentions
        if context.get("intent", {}).get("intent") == "code":
            if "try" not in draft.lower() and "error" in context.get("user_text", "").lower():
                score -= 0.15
                issues.append("User mentioned errors but no error handling discussed")
        
        score = max(0.0, min(1.0, score))
        critique = " | ".join(issues) if issues else "Technical feasibility verified"
        return score, critique


class Archivist(InternalAgent):
    """Validates memory relevance and context usage."""
    
    def evaluate(self, draft: str, context: Dict[str, Any]) -> Tuple[float, str]:
        score = 1.0
        issues = []
        
        # Check if relevant memory was used
        memory_hits = context.get("semantic_hits", [])
        memory_used = context.get("memory_used", False)
        
        if memory_hits and not memory_used:
            # Check if draft references past context
            past_indicators = ["last time", "previously", "before", "earlier", "remember"]
            if not any(ind in draft.lower() for ind in past_indicators):
                score -= 0.1
                issues.append("Relevant memory available but not referenced")
        
        # Check for contradicting past statements
        if memory_used:
            # Simplified: check if draft contradicts known user preferences
            user_profile = context.get("user_profile", {})
            preferences = user_profile.get("preferences", {})
            
            if preferences.get("verbosity") == "concise" and len(draft) > 150:
                score -= 0.15
                issues.append("Response verbose despite user concise preference")
        
        # Check for user entity recognition
        entities = context.get("known_entities", "")
        if entities and "No entities" not in entities:
            # Draft should use names if talking about people
            if "person" in draft.lower() or "someone" in draft.lower():
                score -= 0.05
                issues.append("Generic reference when specific entity known")
        
        score = max(0.0, min(1.0, score))
        critique = " | ".join(issues) if issues else "Memory usage verified"
        return score, critique


class InternalCouncil:
    """
    Multi-perspective validation system for draft responses.
    
    NOT simulated personalities or consciousness.
    This IS systematic quality gates with different validation criteria.
    """
    
    def __init__(self, meta_observer=None):
        self.agents = {
            "strategist": Strategist("Strategist", threshold=0.6),
            "skeptic": Skeptic("Skeptic", threshold=0.7),
            "empath": Empath("Empath", threshold=0.65),
            "engineer": Engineer("Engineer", threshold=0.7),
            "archivist": Archivist("Archivist", threshold=0.6),
        }
        self.meta_observer = meta_observer
    
    def deliberate(
        self,
        draft: str,
        context: Dict[str, Any],
        active_agents: List[str] | None = None
    ) -> Dict[str, Any]:
        """
        Run draft through relevant validation agents.
        
        Returns:
            {
                "approved": bool,
                "final_score": float,
                "critiques": {agent_name: (score, critique)},
                "modifications": str | None,
                "consensus": str
            }
        """
        # Dynamic routing: select agents based on context
        if active_agents is None:
            active_agents = self._route_agents(context)
        
        # Collect evaluations
        critiques = {}
        scores = []
        for agent_name in active_agents:
            agent = self.agents.get(agent_name)
            if agent:
                score, critique = agent.evaluate(draft, context)
                critiques[agent_name] = (score, critique)
                scores.append(score)
        
        # Calculate weighted final score
        final_score = sum(scores) / len(scores) if scores else 1.0
        
        # Determine approval (all agents must meet threshold)
        approved = all(
            score >= self.agents[name].threshold 
            for name, (score, _) in critiques.items()
        )
        
        # Generate consensus
        consensus = self._generate_consensus(critiques, approved, final_score)
        
        # Suggest modifications if not approved
        modifications = self._suggest_modifications(critiques) if not approved else None
        
        return {
            "approved": approved,
            "final_score": round(final_score, 3),
            "critiques": critiques,
            "modifications": modifications,
            "consensus": consensus,
            "active_agents": active_agents,
        }
    
    def _route_agents(self, context: Dict[str, Any]) -> List[str]:
        """Dynamically select which agents to consult based on context."""
        intent_type = context.get("intent", {}).get("intent", "chat")
        active = []
        
        # Always include Observer (meta-awareness) via strategist
        active.append("strategist")
        
        # Include Skeptic for factual/technical claims
        if intent_type in ["code", "advice", "search"]:
            active.append("skeptic")
        
        # Include Engineer for code/technical
        if intent_type in ["code", "file", "app_open"]:
            active.append("engineer")
        
        # Include Empath for chat/advice
        if intent_type in ["chat", "advice", "reminder"]:
            active.append("empath")
        
        # Include Archivist if memory available
        if context.get("memory_used") or context.get("semantic_hits"):
            active.append("archivist")
        
        # Default: at least strategist + one other
        if len(active) == 1:
            active.append("skeptic")
        
        return active
    
    def _generate_consensus(
        self, 
        critiques: Dict[str, Tuple[float, str]], 
        approved: bool, 
        final_score: float
    ) -> str:
        """Generate consensus summary from agent evaluations."""
        if approved:
            return f"Consensus: Approved (score {final_score:.2f})"
        
        # Identify primary concerns
        concerns = []
        for agent_name, (score, critique) in critiques.items():
            if score < self.agents[agent_name].threshold:
                concerns.append(f"{agent_name}: {critique}")
        
        return f"Consensus: Revision needed (score {final_score:.2f}) — " + " | ".join(concerns[:2])
    
    def _suggest_modifications(self, critiques: Dict[str, Tuple[float, str]]) -> str:
        """Suggest specific modifications based on critiques."""
        suggestions = []
        
        for agent_name, (score, critique) in critiques.items():
            threshold = self.agents[agent_name].threshold
            if score < threshold:
                if agent_name == "strategist":
                    suggestions.append("Shorten response or clarify main point")
                elif agent_name == "skeptic":
                    suggestions.append("Add caveats or reduce certainty language")
                elif agent_name == "empath":
                    suggestions.append("Adjust tone to match user sentiment")
                elif agent_name == "engineer":
                    suggestions.append("Fix syntax errors or add error handling notes")
                elif agent_name == "archivist":
                    suggestions.append("Reference relevant past context or known entities")
        
        return " • ".join(suggestions) if suggestions else "Minor refinements suggested"
