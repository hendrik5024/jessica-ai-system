"""
System 2 Reasoning - Long-Term Recursive Thinking

Extends the existing ReflectionWindow with deeper counterfactual
reasoning and failure reprocessing during idle time.

Integrates with:
- Existing ReflectionWindow (short-term reflection)
- RegretMemory (failure tracking)
- AutodidacticLoop (learning updates)
- Background cognition engine (scheduling)
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReasoningDepth(Enum):
    """Depth of reasoning analysis"""
    SHALLOW = "shallow"  # Quick review
    MEDIUM = "medium"  # Standard analysis
    DEEP = "deep"  # Full counterfactual tree


@dataclass
class CounterfactualScenario:
    """Alternative "what if" scenario"""
    original_situation: str
    original_action: str
    original_outcome: str
    alternative_action: str
    predicted_outcome: str
    reasoning: str
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)


@dataclass
class LearningExtraction:
    """Extracted learning from reflection"""
    learning_type: str  # "prompt_update", "knowledge_gap", "principle"
    summary: str
    actionable_changes: List[str]
    confidence: float
    domain: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class System2Session:
    """Record of System 2 reasoning session"""
    session_id: str
    start_time: float
    end_time: Optional[float]
    focus: str  # What we're thinking about
    regrets_processed: int = 0
    counterfactuals_generated: int = 0
    learnings_extracted: int = 0
    updates_applied: int = 0
    interrupted: bool = False
    results: Dict[str, Any] = field(default_factory=dict)


class System2Reasoner:
    """
    Deep reasoning system for failure reprocessing
    
    During idle time:
    1. Query regret memory for failures
    2. Generate counterfactual scenarios ("what should I have done?")
    3. Extract generalizable learnings
    4. Update prompts, knowledge, and strategies
    """
    
    def __init__(
        self,
        regret_memory,  # RegretMemoryStore
        autodidactic_loop,  # AutodidacticLoop
        reflection_window  # ReflectionWindow (existing)
    ):
        self.regret_memory = regret_memory
        self.autodidactic_loop = autodidactic_loop
        self.reflection_window = reflection_window
        
        # Session tracking
        self.active_session: Optional[System2Session] = None
        self.completed_sessions: List[System2Session] = []
        
        # Learning storage (in-memory for now)
        self.extracted_learnings: List[LearningExtraction] = []
        self.prompt_updates: List[Dict[str, str]] = []
        
        # Statistics
        self.total_counterfactuals = 0
        self.total_learnings = 0
        self.total_updates = 0
    
    def think_slow(
        self,
        interrupt_flag,
        depth: ReasoningDepth = ReasoningDepth.MEDIUM,
        time_range_hours: int = 24
    ) -> System2Session:
        """
        Main System 2 reasoning loop
        
        Processes failures and generates improvements during idle time.
        Can be interrupted when user returns.
        """
        session_id = f"system2_{int(time.time())}"
        
        self.active_session = System2Session(
            session_id=session_id,
            start_time=time.time(),
            end_time=None,
            focus=f"Regret analysis (last {time_range_hours}h)"
        )
        
        logger.info(f"Starting System 2 reasoning: depth={depth.value}, range={time_range_hours}h")
        
        try:
            # Step 1: Get recent failures from regret memory
            regrets = self._query_recent_regrets(time_range_hours)
            self.active_session.regrets_processed = len(regrets)
            logger.info(f"Found {len(regrets)} regrets to process")
            
            # Step 2: Process each regret
            for i, regret in enumerate(regrets):
                if interrupt_flag.is_set():
                    logger.info("System 2 reasoning interrupted by user activity")
                    self.active_session.interrupted = True
                    break
                
                # Generate counterfactuals
                counterfactuals = self._generate_counterfactuals(regret, depth)
                self.active_session.counterfactuals_generated += len(counterfactuals)
                
                # Extract learnings
                learnings = self._extract_learnings(regret, counterfactuals)
                self.active_session.learnings_extracted += len(learnings)
                
                # Apply learnings (if not interrupted)
                if learnings and not interrupt_flag.is_set():
                    updates = self._apply_learnings(learnings)
                    self.active_session.updates_applied += updates
                
                logger.debug(
                    f"Processed regret {i+1}/{len(regrets)}: "
                    f"{len(counterfactuals)} counterfactuals, "
                    f"{len(learnings)} learnings"
                )
            
            # Step 3: Synthesize cross-regret patterns
            if not interrupt_flag.is_set():
                patterns = self._find_patterns_across_regrets()
                self.active_session.results["patterns"] = patterns
                logger.info(f"Identified {len(patterns)} cross-regret patterns")
            
        except Exception as e:
            logger.error(f"Error in System 2 reasoning: {e}")
        
        finally:
            session = self._end_session()
        
        return session
    
    def _query_recent_regrets(self, time_range_hours: int) -> List[Dict[str, Any]]:
        """Get recent failures from regret memory"""
        now = datetime.now()
        start_time = datetime.fromtimestamp(now.timestamp() - time_range_hours * 3600)
        
        try:
            regrets = self.regret_memory.query_regrets(
                time_range_start=start_time,
                time_range_end=now
            )
            return regrets if regrets else []
        except Exception as e:
            logger.error(f"Error querying regret memory: {e}")
            return []
    
    def _generate_counterfactuals(
        self,
        regret: Dict[str, Any],
        depth: ReasoningDepth
    ) -> List[CounterfactualScenario]:
        """
        Generate "what should I have done instead?" scenarios
        
        For each failure, create 2-5 alternative approaches that
        would likely have led to better outcomes.
        """
        counterfactuals = []
        
        situation = regret.get("situation", "")
        my_action = regret.get("my_action", "")
        outcome = regret.get("outcome", "")
        what_i_wish = regret.get("what_i_wish_i_had_done", "")
        domain = regret.get("domain", "general")
        
        # Counterfactual 1: User's stated better alternative
        if what_i_wish:
            counterfactuals.append(CounterfactualScenario(
                original_situation=situation,
                original_action=my_action,
                original_outcome=outcome,
                alternative_action=what_i_wish,
                predicted_outcome="Better outcome (per user feedback)",
                reasoning="User explicitly stated this would have been better",
                confidence=0.95,
                evidence=["User feedback"]
            ))
        
        # Counterfactual 2: Earlier detection/intervention
        if self._is_timing_issue(outcome):
            counterfactuals.append(CounterfactualScenario(
                original_situation=situation,
                original_action=my_action,
                original_outcome=outcome,
                alternative_action=f"Detect '{self._extract_problem(situation)}' earlier and intervene",
                predicted_outcome="Issue addressed before escalation",
                reasoning="Earlier detection allows proactive intervention",
                confidence=0.85,
                evidence=["Outcome indicates late detection", "Proactive > Reactive"]
            ))
        
        # Counterfactual 3: Ask for clarification
        if self._is_ambiguity_issue(situation, outcome):
            counterfactuals.append(CounterfactualScenario(
                original_situation=situation,
                original_action=my_action,
                original_outcome=outcome,
                alternative_action="Ask clarifying questions: 'Can you specify...?' or 'Do you mean...?'",
                predicted_outcome="Correct understanding before action",
                reasoning="Ambiguity should trigger confirmation before action",
                confidence=0.88,
                evidence=["Situation or outcome indicates ambiguity", "Clarification is low-cost"]
            ))
        
        # Counterfactual 4: Consult knowledge first
        if domain != "general":
            counterfactuals.append(CounterfactualScenario(
                original_situation=situation,
                original_action=my_action,
                original_outcome=outcome,
                alternative_action=f"Query {domain} knowledge base before responding",
                predicted_outcome="More informed, accurate response",
                reasoning="Domain knowledge should inform specialized responses",
                confidence=0.80,
                evidence=[f"Failure in {domain} domain", "Knowledge lookup is available"]
            ))
        
        # Counterfactual 5: Conservative initial approach (if depth is DEEP)
        if depth == ReasoningDepth.DEEP and self._is_risk_issue(my_action):
            counterfactuals.append(CounterfactualScenario(
                original_situation=situation,
                original_action=my_action,
                original_outcome=outcome,
                alternative_action="Start with conservative/safe option, then escalate if needed",
                predicted_outcome="Reduced risk of negative outcome",
                reasoning="When uncertain, prefer reversible actions",
                confidence=0.75,
                evidence=["Action appears risky", "Progressive disclosure principle"]
            ))
        
        self.total_counterfactuals += len(counterfactuals)
        logger.debug(f"Generated {len(counterfactuals)} counterfactuals (depth={depth.value})")
        
        return counterfactuals
    
    def _is_timing_issue(self, outcome: str) -> bool:
        """Check if outcome indicates timing/detection issue"""
        keywords = ["too late", "should have", "earlier", "sooner", "already", "by the time"]
        return any(kw in outcome.lower() for kw in keywords)
    
    def _is_ambiguity_issue(self, situation: str, outcome: str) -> bool:
        """Check if situation/outcome indicates ambiguity"""
        keywords = ["unclear", "misunderstood", "confused", "ambiguous", "vague", "meant", "thought"]
        text = (situation + " " + outcome).lower()
        return any(kw in text for kw in keywords)
    
    def _is_risk_issue(self, action: str) -> bool:
        """Check if action seems risky/aggressive"""
        keywords = ["bold", "risky", "aggressive", "direct", "immediate", "all", "fully"]
        return any(kw in action.lower() for kw in keywords)
    
    def _extract_problem(self, situation: str) -> str:
        """Extract the core problem from situation description"""
        # Simple heuristic - would use NLP in full implementation
        return situation.split("when")[0].strip() if "when" in situation else situation[:50]
    
    def _extract_learnings(
        self,
        regret: Dict[str, Any],
        counterfactuals: List[CounterfactualScenario]
    ) -> List[LearningExtraction]:
        """
        Extract generalizable learnings from counterfactual analysis
        
        Transform specific failures into general principles,
        prompt updates, and knowledge gaps.
        """
        learnings = []
        domain = regret.get("domain", "general")
        
        if not counterfactuals:
            return learnings
        
        # Learning 1: Best alternative as general principle
        best_cf = max(counterfactuals, key=lambda c: c.confidence)
        situation_type = self._classify_situation_type(regret)
        
        learnings.append(LearningExtraction(
            learning_type="principle",
            summary=f"In '{situation_type}' situations: {best_cf.reasoning}",
            actionable_changes=[
                f"Add guardrail: Check for '{situation_type}' before acting",
                f"Update {domain} decision template"
            ],
            confidence=best_cf.confidence,
            domain=domain
        ))
        
        # Learning 2: Common theme across counterfactuals
        themes = self._identify_themes(counterfactuals)
        
        if "clarification" in themes:
            learnings.append(LearningExtraction(
                learning_type="prompt_update",
                summary="Add 'Ask clarifying questions when uncertain' to system prompt",
                actionable_changes=[
                    "Update system prompt with uncertainty threshold",
                    "Add confidence check before action",
                    "Generate clarifying questions template"
                ],
                confidence=0.87,
                domain=domain
            ))
        
        if "knowledge_lookup" in themes:
            learnings.append(LearningExtraction(
                learning_type="knowledge_gap",
                summary=f"Knowledge gap in {domain} domain",
                actionable_changes=[
                    f"Trigger autodidactic learning for {domain}",
                    f"Add {domain} to high-priority learning queue",
                    f"Create synthetic training data for {domain} failures"
                ],
                confidence=0.82,
                domain=domain
            ))
        
        if "early_detection" in themes:
            learnings.append(LearningExtraction(
                learning_type="principle",
                summary="Proactive detection > Reactive response",
                actionable_changes=[
                    "Add monitoring/alerting to system",
                    "Shift from reactive to proactive mode",
                    "Check for potential issues before they escalate"
                ],
                confidence=0.84,
                domain=domain
            ))
        
        self.total_learnings += len(learnings)
        self.extracted_learnings.extend(learnings)
        
        return learnings
    
    def _classify_situation_type(self, regret: Dict[str, Any]) -> str:
        """Classify what type of situation this was"""
        situation = regret.get("situation", "").lower()
        outcome = regret.get("outcome", "").lower()
        
        combined = situation + " " + outcome
        
        if any(kw in combined for kw in ["unclear", "ambiguous", "vague"]):
            return "ambiguous_request"
        elif any(kw in combined for kw in ["urgent", "quickly", "time"]):
            return "time_pressure"
        elif any(kw in combined for kw in ["complex", "multiple", "many"]):
            return "complex_task"
        elif any(kw in combined for kw in ["new", "unfamiliar", "first time"]):
            return "novel_situation"
        elif any(kw in combined for kw in ["misunderstood", "wrong", "incorrect"]):
            return "interpretation_error"
        else:
            return "general_failure"
    
    def _identify_themes(self, counterfactuals: List[CounterfactualScenario]) -> List[str]:
        """Identify common themes across counterfactuals"""
        themes = []
        
        all_text = " ".join(
            cf.alternative_action + " " + cf.reasoning
            for cf in counterfactuals
        ).lower()
        
        theme_keywords = {
            "clarification": ["clarify", "ask", "confirm", "verify", "check"],
            "early_detection": ["earlier", "detect", "monitor", "anticipate", "proactive"],
            "knowledge_lookup": ["consult", "query", "knowledge", "lookup", "check"],
            "caution": ["conservative", "safe", "careful", "cautious", "gradual"]
        }
        
        for theme, keywords in theme_keywords.items():
            if sum(1 for kw in keywords if kw in all_text) >= 2:  # At least 2 keyword matches
                themes.append(theme)
        
        return themes
    
    def _apply_learnings(self, learnings: List[LearningExtraction]) -> int:
        """
        Apply extracted learnings to update system
        
        Routes to appropriate subsystems:
        - Prompt updates → Template storage
        - Knowledge gaps → Autodidactic loop
        - Principles → Decision-making rules
        """
        updates = 0
        
        for learning in learnings:
            try:
                if learning.learning_type == "knowledge_gap":
                    # Add domain to autodidactic learning queue
                    self.autodidactic_loop.add_priority_domain(learning.domain)
                    logger.info(f"Added '{learning.domain}' to learning queue (confidence={learning.confidence:.2f})")
                    updates += 1
                
                elif learning.learning_type == "prompt_update":
                    # Store prompt update
                    self.prompt_updates.append({
                        "summary": learning.summary,
                        "changes": learning.actionable_changes,
                        "confidence": learning.confidence,
                        "timestamp": learning.timestamp.isoformat()
                    })
                    logger.info(f"Stored prompt update: {learning.summary}")
                    updates += 1
                
                elif learning.learning_type == "principle":
                    # Store principle (would update decision rules in full implementation)
                    logger.info(f"[PRINCIPLE] {learning.summary} (confidence={learning.confidence:.2f})")
                    for change in learning.actionable_changes:
                        logger.info(f"  → {change}")
                    updates += 1
                
            except Exception as e:
                logger.error(f"Error applying learning: {e}")
        
        self.total_updates += updates
        return updates
    
    def _find_patterns_across_regrets(self) -> List[Dict[str, Any]]:
        """Identify patterns across multiple regrets"""
        patterns = []
        
        if len(self.extracted_learnings) < 3:
            return patterns
        
        # Group learnings by domain
        domain_counts = {}
        for learning in self.extracted_learnings[-20:]:  # Last 20 learnings
            domain = learning.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Domains with 3+ failures = systemic issue
        for domain, count in domain_counts.items():
            if count >= 3:
                patterns.append({
                    "pattern_type": "repeated_domain_failures",
                    "domain": domain,
                    "failure_count": count,
                    "recommendation": f"Systemic issue in {domain} - prioritize comprehensive learning",
                    "confidence": min(0.9, 0.6 + count * 0.1)
                })
        
        # Group learnings by type
        type_counts = {}
        for learning in self.extracted_learnings[-20:]:
            ltype = learning.learning_type
            type_counts[ltype] = type_counts.get(ltype, 0) + 1
        
        # Many "clarification" learnings = need better uncertainty handling
        if type_counts.get("prompt_update", 0) >= 3:
            patterns.append({
                "pattern_type": "uncertainty_handling_gap",
                "evidence": f"{type_counts['prompt_update']} prompt updates about clarification",
                "recommendation": "Implement systematic uncertainty quantification and clarification protocol",
                "confidence": 0.85
            })
        
        # Many knowledge gaps = need more aggressive learning
        if type_counts.get("knowledge_gap", 0) >= 3:
            patterns.append({
                "pattern_type": "insufficient_learning_rate",
                "evidence": f"{type_counts['knowledge_gap']} knowledge gaps identified",
                "recommendation": "Increase autodidactic learning frequency or breadth",
                "confidence": 0.82
            })
        
        return patterns
    
    def _end_session(self) -> Optional[System2Session]:
        """End active System 2 session and return it"""
        if not self.active_session:
            return None
        
        self.active_session.end_time = time.time()
        duration = self.active_session.end_time - self.active_session.start_time
        
        # Save session before clearing
        completed_session = self.active_session
        self.completed_sessions.append(completed_session)
        
        logger.info(
            f"System 2 session complete: "
            f"duration={duration:.1f}s, "
            f"regrets={completed_session.regrets_processed}, "
            f"counterfactuals={completed_session.counterfactuals_generated}, "
            f"learnings={completed_session.learnings_extracted}, "
            f"updates={completed_session.updates_applied}, "
            f"interrupted={completed_session.interrupted}"
        )
        
        self.active_session = None
        return completed_session
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get System 2 reasoning statistics"""
        return {
            "total_sessions": len(self.completed_sessions),
            "total_counterfactuals": self.total_counterfactuals,
            "total_learnings": self.total_learnings,
            "total_updates": self.total_updates,
            "avg_counterfactuals_per_session": self.total_counterfactuals / len(self.completed_sessions) if self.completed_sessions else 0,
            "avg_learnings_per_session": self.total_learnings / len(self.completed_sessions) if self.completed_sessions else 0,
            "prompt_updates_pending": len(self.prompt_updates),
            "learnings_by_domain": self._get_learnings_by_domain()
        }
    
    def _get_learnings_by_domain(self) -> Dict[str, int]:
        """Count learnings by domain"""
        domain_counts = {}
        for learning in self.extracted_learnings:
            domain = learning.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        return domain_counts


def create_system2_reasoner(
    regret_memory,
    autodidactic_loop,
    reflection_window
) -> System2Reasoner:
    """Create System 2 reasoning system"""
    return System2Reasoner(
        regret_memory=regret_memory,
        autodidactic_loop=autodidactic_loop,
        reflection_window=reflection_window
    )
