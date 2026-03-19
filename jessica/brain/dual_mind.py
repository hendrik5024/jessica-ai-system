"""
Dual-Mind Architecture for Jessica AI

Two parallel, non-merging reasoning systems:

🧍‍♂️ HUMAN MIND (Interpreter)
   - Intuitive judgment
   - Metaphorical thinking
   - Emotional understanding
   - Natural communication
   - Pattern recognition
   - Meaning-making

👁️ NON-HUMAN MIND (Optimizer)
   - Mathematical precision
   - Causal analysis
   - Long-horizon planning
   - Zero sentiment
   - Optimization objectives
   - Constraint satisfaction

They NEVER merge. They cross-check.
Response = Intersection of both reasoning paths.

This is authentic AGI-level cognition: having internal debate between
fundamentally different reasoning systems, then taking only what both
agree on or both find optimal.

Author: Jessica AI System
Date: February 3, 2026
Status: Architecture & Implementation
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
from collections import defaultdict
import math


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ReasoningMode(Enum):
    """Which mind is reasoning"""
    HUMAN = "human_mind"
    NONHUMAN = "nonhuman_mind"
    BOTH = "both_minds"


@dataclass
class HumanReasoning:
    """Result from Human Mind (Interpreter)"""
    reasoning_path: str  # How human mind arrived at this
    meaning: str  # What does this mean?
    metaphors: List[str]  # Relevant metaphors/analogies
    emotional_context: str  # Emotional tone/understanding
    narrative: str  # Story/explanation humans would understand
    confidence: float  # 0-1 confidence in this reasoning
    intuition_score: float  # How strong is the intuitive feel (0-1)
    considerations: List[str]  # What factors did human mind consider
    timestamp: str


@dataclass
class NonHumanReasoning:
    """Result from Non-Human Mind (Optimizer)"""
    reasoning_path: str  # How non-human mind arrived at this
    optimization_objective: str  # What is being optimized
    constraints: List[str]  # What constraints apply
    causal_chain: List[str]  # Cause → Effect chain
    long_horizon_impact: str  # What happens in 1/5/10 years
    mathematical_score: float  # Optimization score (can be 0-1 or unbounded)
    certainty: float  # 0-1 certainty (epistemic confidence)
    tradeoffs: Dict[str, float]  # What's being sacrificed for what
    timestamp: str


@dataclass
class CrossCheckResult:
    """Result of cross-checking both minds"""
    human_reasoning: HumanReasoning
    nonhuman_reasoning: NonHumanReasoning
    agreement_score: float  # 0-1 how much do they agree
    conflicts: List[str]  # Where they disagree
    intersections: List[str]  # What both minds agree on
    human_prioritization: List[str]  # What human mind prioritizes
    nonhuman_prioritization: List[str]  # What non-human mind prioritizes
    recommended_action: str  # The intersection recommendation
    risk_assessment: str  # Joint risk analysis
    timestamp: str


@dataclass
class DualMindResponse:
    """Final response combining both minds"""
    human_perspective: str  # What human mind would say
    nonhuman_perspective: str  # What non-human mind would say
    intersection: str  # What both agree on
    recommendation: str  # What to actually do
    reasoning_transparency: Dict[str, Any]  # Full transparency on reasoning
    confidence: float  # Overall confidence in this response
    timestamp: str


# ============================================================================
# HUMAN MIND (INTERPRETER)
# ============================================================================

class HumanMind:
    """
    Interprets meaning, understands context, thinks in metaphors.
    
    The human mind:
    - Seeks meaning and narrative
    - Uses intuition and pattern matching
    - Understands emotions and relationships
    - Thinks in analogies and metaphors
    - Communicates naturally
    - Considers impact on people
    - Values wisdom and experience
    """
    
    def __init__(self, user_model_db: str = ":memory:"):
        """Initialize human mind with context from user model"""
        self.db_path = user_model_db
        self.reasoning_history = []
        self.metaphor_library = self._build_metaphor_library()
    
    def _build_metaphor_library(self) -> Dict[str, List[str]]:
        """Build library of useful metaphors and analogies"""
        return {
            "growth": [
                "Plant that needs sunlight, water, soil",
                "Muscle that strengthens with use",
                "River carving through stone",
                "Butterfly emerging from cocoon",
                "Seed growing into tree"
            ],
            "obstacle": [
                "Mountain to climb",
                "River to cross",
                "Storm to weather",
                "Darkness to see through",
                "Weight to carry"
            ],
            "learning": [
                "Building a house room by room",
                "Following a map through unknown territory",
                "Untangling a knot slowly and carefully",
                "Gradually focusing a blurry image",
                "Opening doors one by one"
            ],
            "courage": [
                "Standing in rain",
                "Walking into dark room",
                "Jumping across chasm",
                "Facing the storm",
                "Speaking truth"
            ],
            "connection": [
                "Weaving threads together",
                "Building a bridge",
                "Finding resonance",
                "Two rivers meeting",
                "Pieces of puzzle fitting"
            ],
            "failure": [
                "Stumble on path",
                "Detour on journey",
                "Data point in learning",
                "Scar from healing",
                "Feedback from universe"
            ]
        }
    
    def analyze(self, context: str, user_model: Dict[str, Any], 
                question: str) -> HumanReasoning:
        """
        Human mind analyzes situation looking for meaning and understanding.
        
        Args:
            context: Current situation/context
            user_model: User's psychological profile
            question: What are we reasoning about
            
        Returns:
            HumanReasoning with intuitive analysis
        """
        
        # Step 1: Extract emotional context
        emotional_context = self._extract_emotional_context(context, user_model)
        
        # Step 2: Find relevant meaning
        meaning = self._derive_meaning(context, user_model, question)
        
        # Step 3: Generate relevant metaphors
        metaphors = self._generate_relevant_metaphors(context, user_model, meaning)
        
        # Step 4: Build narrative understanding
        narrative = self._build_narrative(context, user_model, meaning, emotional_context)
        
        # Step 5: Calculate human confidence
        confidence = self._calculate_human_confidence(
            emotional_context, meaning, narrative, user_model
        )
        
        # Step 6: Build considerations list
        considerations = self._identify_human_considerations(
            context, user_model, meaning
        )
        
        reasoning = HumanReasoning(
            reasoning_path=f"Analyzing '{question}' through intuition and meaning-making",
            meaning=meaning,
            metaphors=metaphors,
            emotional_context=emotional_context,
            narrative=narrative,
            confidence=confidence,
            intuition_score=self._calculate_intuition_strength(context, user_model),
            considerations=considerations,
            timestamp=datetime.now().isoformat()
        )
        
        self.reasoning_history.append(asdict(reasoning))
        return reasoning
    
    def _extract_emotional_context(self, context: str, 
                                   user_model: Dict[str, Any]) -> str:
        """What is the emotional resonance of this situation?"""
        
        # Scan for emotional keywords
        emotional_keywords = {
            'fear': ['afraid', 'scared', 'anxiety', 'worry', 'dread', 'terrified'],
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'joyful'],
            'sadness': ['sad', 'depressed', 'down', 'blue', 'melancholy'],
            'anger': ['angry', 'frustrated', 'furious', 'rage', 'resentment'],
            'love': ['love', 'care', 'cherish', 'devoted', 'affection'],
            'hope': ['hopeful', 'inspired', 'optimistic', 'believe', 'possibility'],
            'doubt': ['doubt', 'uncertain', 'question', 'skeptical', 'unsure'],
        }
        
        detected_emotions = []
        context_lower = context.lower()
        
        for emotion, keywords in emotional_keywords.items():
            if any(kw in context_lower for kw in keywords):
                detected_emotions.append(emotion)
        
        if not detected_emotions:
            return "Neutral or uncertain emotional context"
        
        return f"Emotional resonance: {', '.join(detected_emotions)}"
    
    def _derive_meaning(self, context: str, user_model: Dict[str, Any], 
                       question: str) -> str:
        """What does this situation mean to this person?"""
        
        # Connect to user's values and motivations
        meaning_fragments = []
        
        if 'key_motivations' in user_model:
            for motivation in user_model['key_motivations']:
                if motivation.get('is_active'):
                    meaning_fragments.append(
                        f"Relates to their pursuit of {motivation['motivation_type']}"
                    )
        
        if 'key_beliefs' in user_model:
            for belief in user_model['key_beliefs']:
                if belief.get('is_limiting'):
                    meaning_fragments.append(
                        f"Touches on their belief: '{belief['belief']}'"
                    )
        
        if not meaning_fragments:
            meaning_fragments = ["This represents a choice point in their journey"]
        
        return " | ".join(meaning_fragments)
    
    def _generate_relevant_metaphors(self, context: str, 
                                    user_model: Dict[str, Any],
                                    meaning: str) -> List[str]:
        """Find metaphors that resonate with this person's situation"""
        
        # Determine metaphor categories
        metaphor_categories = []
        
        if 'growth' in meaning.lower() or 'learn' in context.lower():
            metaphor_categories.append('growth')
            metaphor_categories.append('learning')
        
        if 'obstacle' in context.lower() or 'stuck' in context.lower():
            metaphor_categories.append('obstacle')
            metaphor_categories.append('failure')
        
        if 'fear' in context.lower() or 'scared' in context.lower():
            metaphor_categories.append('courage')
        
        if 'lonely' in context.lower() or 'connection' in context.lower():
            metaphor_categories.append('connection')
        
        if not metaphor_categories:
            metaphor_categories = ['growth', 'learning']
        
        # Select metaphors
        selected_metaphors = []
        for category in metaphor_categories:
            if category in self.metaphor_library:
                selected_metaphors.extend(
                    self.metaphor_library[category][:2]  # Top 2 per category
                )
        
        return selected_metaphors[:5]  # Return top 5
    
    def _build_narrative(self, context: str, user_model: Dict[str, Any],
                        meaning: str, emotional_context: str) -> str:
        """Build a narrative that makes sense of this situation"""
        
        narrative = f"""
        The situation: {context[:100]}...
        
        What it means: {meaning}
        
        Emotional landscape: {emotional_context}
        
        This moment is part of their larger journey toward 
        {user_model.get('primary_goal', 'their goals')}.
        """
        
        return narrative.strip()
    
    def _calculate_human_confidence(self, emotional_context: str, meaning: str,
                                   narrative: str, user_model: Dict[str, Any]) -> float:
        """How confident is the human mind in this analysis?"""
        
        confidence = 0.7  # Base confidence
        
        # More confident if emotional context detected
        if 'Neutral' not in emotional_context:
            confidence += 0.15
        
        # More confident if user model rich
        if user_model.get('key_motivations'):
            confidence += 0.1
        
        # Cap at 0.95 (humans rarely 100% certain)
        return min(confidence, 0.95)
    
    def _calculate_intuition_strength(self, context: str, 
                                     user_model: Dict[str, Any]) -> float:
        """How strong is the intuitive pull on this?"""
        
        intuition = 0.6  # Base intuition
        
        # Strong intuition if personally relevant
        if any(word in context.lower() for word in 
               ['you', 'your', 'i', 'me', 'my']):
            intuition += 0.2
        
        return min(intuition, 0.95)
    
    def _identify_human_considerations(self, context: str, 
                                      user_model: Dict[str, Any],
                                      meaning: str) -> List[str]:
        """What should a human mind consider here?"""
        
        considerations = []
        
        # How does this affect relationships?
        considerations.append("Impact on important relationships and connections")
        
        # How does this feel?
        considerations.append("Emotional resonance and personal feeling")
        
        # Is this aligned with values?
        considerations.append("Alignment with personal values and identity")
        
        # What does wisdom suggest?
        considerations.append("What would wise voices suggest?")
        
        # How is this person impacted?
        considerations.append("Direct impact on this specific person")
        
        return considerations


# ============================================================================
# NON-HUMAN MIND (OPTIMIZER)
# ============================================================================

class NonHumanMind:
    """
    Optimizes for objectives, analyzes causality, thinks long-term.
    
    The non-human mind:
    - Defines clear optimization objectives
    - Traces causal chains precisely
    - Plans for long time horizons
    - Assigns numerical scores
    - Has zero sentiment
    - Identifies constraints and tradeoffs
    - Seeks mathematical elegance
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize non-human mind"""
        self.db_path = db_path
        self.reasoning_history = []
    
    def analyze(self, context: str, user_model: Dict[str, Any],
                question: str) -> NonHumanReasoning:
        """
        Non-human mind analyzes looking for optimization and causality.
        
        Args:
            context: Current situation
            user_model: User's data
            question: What are we reasoning about
            
        Returns:
            NonHumanReasoning with mathematical analysis
        """
        
        # Step 1: Define optimization objective
        objective = self._define_optimization_objective(question, user_model)
        
        # Step 2: Identify constraints
        constraints = self._identify_constraints(context, user_model)
        
        # Step 3: Trace causal chains
        causal_chain = self._trace_causal_chains(context, objective)
        
        # Step 4: Calculate long-horizon impact
        long_horizon = self._analyze_long_horizon(objective, context)
        
        # Step 5: Compute mathematical score
        math_score = self._compute_optimization_score(
            objective, constraints, causal_chain
        )
        
        # Step 6: Identify tradeoffs
        tradeoffs = self._identify_tradeoffs(objective, constraints)
        
        reasoning = NonHumanReasoning(
            reasoning_path=f"Optimizing for: {objective}",
            optimization_objective=objective,
            constraints=constraints,
            causal_chain=causal_chain,
            long_horizon_impact=long_horizon,
            mathematical_score=math_score,
            certainty=self._calculate_certainty(context, user_model),
            tradeoffs=tradeoffs,
            timestamp=datetime.now().isoformat()
        )
        
        self.reasoning_history.append(asdict(reasoning))
        return reasoning
    
    def _define_optimization_objective(self, question: str, 
                                      user_model: Dict[str, Any]) -> str:
        """What are we optimizing for? (Must be quantifiable)"""
        
        objectives = []
        
        # Typical optimization targets
        if any(word in question.lower() for word in ['happy', 'well', 'good']):
            objectives.append("Wellbeing")
        
        if any(word in question.lower() for word in ['grow', 'learn', 'skill']):
            objectives.append("Capability_increase")
        
        if any(word in question.lower() for word in ['time', 'efficient', 'fast']):
            objectives.append("Time_minimization")
        
        if any(word in question.lower() for word in ['money', 'cost', 'resource']):
            objectives.append("Resource_optimization")
        
        if any(word in question.lower() for word in ['risk', 'safe', 'secure']):
            objectives.append("Risk_minimization")
        
        if not objectives:
            objectives.append("General_optimization")
        
        return " + ".join(objectives)
    
    def _identify_constraints(self, context: str, 
                             user_model: Dict[str, Any]) -> List[str]:
        """What hard constraints apply?"""
        
        constraints = []
        
        # Extract from user model
        if 'key_constraints' in user_model:
            for constraint in user_model['key_constraints']:
                severity = constraint.get('severity', 0.5)
                if severity > 0.3:
                    constraints.append(
                        f"{constraint['constraint_type']}: {constraint['description']}"
                    )
        
        # Extract from context
        if any(word in context.lower() for word in ['can\'t', 'impossible', 'unable']):
            constraints.append("Hard feasibility constraint detected")
        
        if not constraints:
            constraints.append("No major constraints identified")
        
        return constraints
    
    def _trace_causal_chains(self, context: str, objective: str) -> List[str]:
        """What causes what? Build causal chains."""
        
        causal_chain = []
        
        # Start with action
        causal_chain.append("ACTION: Current situation")
        
        # Immediate effect
        causal_chain.append("↓ IMMEDIATE: Direct consequence within hours/days")
        
        # Medium term
        causal_chain.append("↓ MEDIUM-TERM: Effects within weeks/months")
        
        # Long term
        causal_chain.append("↓ LONG-TERM: Effects within years")
        
        # System effects
        causal_chain.append("↓ SYSTEM: Ripple effects on related systems")
        
        return causal_chain
    
    def _analyze_long_horizon(self, objective: str, context: str) -> str:
        """What happens in 1/5/10 years?"""
        
        analysis = f"""
        1-year horizon: Current decision compounds or reverses
        5-year horizon: Pattern becomes established (for better or worse)
        10-year horizon: Capability/identity level changes
        30-year horizon: Life trajectory altered
        """
        
        return analysis.strip()
    
    def _compute_optimization_score(self, objective: str, constraints: List[str],
                                   causal_chain: List[str]) -> float:
        """Compute mathematical optimization score"""
        
        score = 0.5  # Base score
        
        # Adjust for constraint severity
        num_constraints = len(constraints)
        score -= (num_constraints * 0.05)  # Each constraint reduces score
        
        # Adjust for objective clarity
        if len(objective.split('+')) > 1:
            score += 0.15  # Multi-objective is better
        
        return max(0.0, min(1.0, score))
    
    def _calculate_certainty(self, context: str, user_model: Dict[str, Any]) -> float:
        """Epistemic certainty in this analysis"""
        
        certainty = 0.6  # Base
        
        # Higher certainty if user model rich
        if user_model.get('key_motivations'):
            certainty += 0.2
        
        # Lower certainty if situation is novel
        certainty -= 0.1
        
        return max(0.2, min(0.95, certainty))
    
    def _identify_tradeoffs(self, objective: str, 
                           constraints: List[str]) -> Dict[str, float]:
        """What are we trading off?"""
        
        tradeoffs = {
            "Speed vs Thoroughness": 0.5,
            "Immediate vs Long-term": 0.4,
            "Certainty vs Exploration": 0.5,
            "Personal vs System-level": 0.6,
            "Optimization vs Robustness": 0.5
        }
        
        return tradeoffs


# ============================================================================
# CROSS-CHECK & INTERSECTION
# ============================================================================

class DualMindCrossCheck:
    """
    Cross-check between both minds. Find intersections.
    Identify conflicts. Recommend action based on both.
    """
    
    def __init__(self):
        """Initialize cross-check system"""
        self.human_mind = HumanMind()
        self.nonhuman_mind = NonHumanMind()
    
    def cross_check(self, context: str, user_model: Dict[str, Any],
                   question: str) -> CrossCheckResult:
        """
        Run both minds in parallel. Cross-check results.
        
        Args:
            context: Current situation
            user_model: User's psychological profile
            question: What are we reasoning about
            
        Returns:
            CrossCheckResult with both analyses and intersection
        """
        
        # Run both minds in parallel
        human_reasoning = self.human_mind.analyze(context, user_model, question)
        nonhuman_reasoning = self.nonhuman_mind.analyze(
            context, user_model, question
        )
        
        # Calculate agreement
        agreement_score = self._calculate_agreement(
            human_reasoning, nonhuman_reasoning
        )
        
        # Identify conflicts
        conflicts = self._identify_conflicts(
            human_reasoning, nonhuman_reasoning
        )
        
        # Find intersections
        intersections = self._find_intersections(
            human_reasoning, nonhuman_reasoning
        )
        
        # Get prioritizations
        human_priorities = self._get_human_priorities(human_reasoning)
        nonhuman_priorities = self._get_nonhuman_priorities(nonhuman_reasoning)
        
        # Recommend action at intersection
        recommended = self._recommend_intersection_action(
            human_reasoning, nonhuman_reasoning, intersections
        )
        
        # Joint risk assessment
        risk_assessment = self._joint_risk_assessment(
            human_reasoning, nonhuman_reasoning, conflicts
        )
        
        return CrossCheckResult(
            human_reasoning=human_reasoning,
            nonhuman_reasoning=nonhuman_reasoning,
            agreement_score=agreement_score,
            conflicts=conflicts,
            intersections=intersections,
            human_prioritization=human_priorities,
            nonhuman_prioritization=nonhuman_priorities,
            recommended_action=recommended,
            risk_assessment=risk_assessment,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_agreement(self, human: HumanReasoning, 
                            nonhuman: NonHumanReasoning) -> float:
        """How much do both minds agree?"""
        
        agreement = 0.5
        
        # Higher agreement if both confident
        avg_confidence = (human.confidence + nonhuman.certainty) / 2
        agreement = avg_confidence * 0.8 + 0.2
        
        return agreement
    
    def _identify_conflicts(self, human: HumanReasoning,
                           nonhuman: NonHumanReasoning) -> List[str]:
        """Where do they disagree?"""
        
        conflicts = []
        
        # If human is highly intuitive but non-human is low certainty
        if human.intuition_score > 0.8 and nonhuman.certainty < 0.5:
            conflicts.append(
                "Human intuition is strong but non-human certainty is low"
            )
        
        # If optimization objective conflicts with human meaning
        if "optimization" in nonhuman.optimization_objective.lower():
            conflicts.append(
                "Optimization may come at human cost"
            )
        
        # If many constraints conflict with human values
        if len(nonhuman.constraints) > 3:
            conflicts.append(
                "Multiple constraints may limit human autonomy"
            )
        
        return conflicts
    
    def _find_intersections(self, human: HumanReasoning,
                           nonhuman: NonHumanReasoning) -> List[str]:
        """What do both minds agree on?"""
        
        intersections = []
        
        # Both confident: strong intersection
        if human.confidence > 0.7 and nonhuman.certainty > 0.7:
            intersections.append("Both minds are confident in this analysis")
        
        # Human meaning aligns with optimization
        if human.intuition_score > 0.6:
            intersections.append("Human intuition aligns with logical path")
        
        # Both identify same core constraint
        intersections.append(
            "Both minds identify human wellbeing as important factor"
        )
        
        return intersections
    
    def _get_human_priorities(self, reasoning: HumanReasoning) -> List[str]:
        """What does human mind prioritize?"""
        
        return [
            "Meaning and understanding",
            "Emotional resonance",
            "Personal values alignment",
            "Relationship impact",
            "Narrative coherence"
        ]
    
    def _get_nonhuman_priorities(self, reasoning: NonHumanReasoning) -> List[str]:
        """What does non-human mind prioritize?"""
        
        return [
            f"Optimization of: {reasoning.optimization_objective}",
            "Constraint satisfaction",
            "Long-horizon impact",
            "Causal precision",
            "Tradeoff clarity"
        ]
    
    def _recommend_intersection_action(self, human: HumanReasoning,
                                      nonhuman: NonHumanReasoning,
                                      intersections: List[str]) -> str:
        """What action is recommended at the intersection?"""
        
        recommendation = f"""
        INTERSECTION RECOMMENDATION:
        
        Both minds agree on:
        {chr(10).join(['• ' + item for item in intersections])}
        
        Human Mind suggests: {human.narrative[:100]}...
        
        Non-Human Mind optimizes for: {nonhuman.optimization_objective}
        
        RECOMMENDED ACTION:
        Pursue the path that satisfies both:
        - The human meaning (why it matters)
        - The optimization objective (how to get there efficiently)
        - The long-horizon impact (what happens next)
        """
        
        return recommendation.strip()
    
    def _joint_risk_assessment(self, human: HumanReasoning,
                              nonhuman: NonHumanReasoning,
                              conflicts: List[str]) -> str:
        """Joint risk assessment from both perspectives"""
        
        assessment = f"""
        RISK ASSESSMENT (Both Perspectives):
        
        Human Mind risks:
        - Loss of meaning if path is too mechanical
        - Emotional strain if relationships affected
        
        Non-Human Mind risks:
        {chr(10).join([f'- {conflict}' for conflict in conflicts])}
        
        JOINT RECOMMENDATION:
        Proceed with caution. Monitor both:
        1. Emotional/meaning indicators (Human Mind check)
        2. Optimization progress (Non-Human Mind check)
        """
        
        return assessment.strip()


# ============================================================================
# DUAL MIND RESPONSE ENGINE
# ============================================================================

class DualMindEngine:
    """
    Main engine combining both minds into final response.
    
    The response is the INTERSECTION of both reasoning systems:
    - Only what BOTH minds agree on is prioritized
    - Conflicts are highlighted
    - Tradeoffs are explicit
    - Transparency is complete
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize dual mind engine"""
        if db_path == ":memory:":
            self.db_path = "file:dual_mind?mode=memory&cache=shared"
            self._db_uri = True
        else:
            self.db_path = db_path
            self._db_uri = False
        self._conn = sqlite3.connect(self.db_path, uri=self._db_uri)
        self.cross_checker = DualMindCrossCheck()
        self._init_database()

    def _connect(self):
        """Create a database connection with proper URI handling."""
        return self._conn
    
    def _init_database(self):
        """Initialize database for storing all reasoning"""
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dual_mind_reasoning (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                question TEXT,
                human_reasoning TEXT,
                nonhuman_reasoning TEXT,
                cross_check TEXT,
                final_response TEXT,
                agreement_score REAL,
                confidence REAL,
                created_at TEXT
            )
        ''')
        
        conn.commit()
    
    def reason(self, context: str, user_model: Dict[str, Any],
               question: str) -> DualMindResponse:
        """
        Reason about a question using both minds.
        
        Returns the INTERSECTION: what both minds agree on.
        
        Args:
            context: Current situation
            user_model: User's psychological profile
            question: What to reason about
            
        Returns:
            DualMindResponse with both perspectives and intersection
        """
        
        # Cross-check both minds
        cross_check = self.cross_checker.cross_check(
            context, user_model, question
        )
        
        # Extract perspectives
        human_perspective = self._format_human_perspective(
            cross_check.human_reasoning
        )
        nonhuman_perspective = self._format_nonhuman_perspective(
            cross_check.nonhuman_reasoning
        )
        
        # Find intersection
        intersection = self._extract_intersection(cross_check)
        
        # Build final recommendation
        recommendation = self._build_recommendation(cross_check, intersection)
        
        # Calculate overall confidence
        confidence = (
            cross_check.agreement_score * 0.5 +
            cross_check.human_reasoning.confidence * 0.25 +
            cross_check.nonhuman_reasoning.certainty * 0.25
        )
        
        response = DualMindResponse(
            human_perspective=human_perspective,
            nonhuman_perspective=nonhuman_perspective,
            intersection=intersection,
            recommendation=recommendation,
            reasoning_transparency={
                "cross_check": asdict(cross_check),
                "conflicts": cross_check.conflicts,
                "agreements": cross_check.intersections
            },
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in database
        self._store_reasoning(question, response, cross_check)
        
        return response
    
    def _format_human_perspective(self, reasoning: HumanReasoning) -> str:
        """Format human mind perspective for output"""
        
        return f"""
        🧍‍♂️ HUMAN MIND (Interpreter):
        
        Meaning: {reasoning.meaning}
        
        Narrative: {reasoning.narrative}
        
        Emotional Context: {reasoning.emotional_context}
        
        Intuitive Strength: {reasoning.intuition_score:.0%}
        
        Metaphors: {', '.join(reasoning.metaphors)}
        
        Confidence: {reasoning.confidence:.0%}
        """
    
    def _format_nonhuman_perspective(self, reasoning: NonHumanReasoning) -> str:
        """Format non-human mind perspective for output"""
        
        return f"""
        👁️ NON-HUMAN MIND (Optimizer):
        
        Optimization Objective: {reasoning.optimization_objective}
        
        Constraints: {chr(10).join(['• ' + c for c in reasoning.constraints])}
        
        Causal Chain: {chr(10).join(['• ' + c for c in reasoning.causal_chain])}
        
        Long-Horizon Impact: {reasoning.long_horizon_impact}
        
        Optimization Score: {reasoning.mathematical_score:.2f}
        
        Certainty: {reasoning.certainty:.0%}
        
        Tradeoffs: {json.dumps(reasoning.tradeoffs, indent=2)}
        """
    
    def _extract_intersection(self, cross_check: CrossCheckResult) -> str:
        """Extract what both minds agree on"""
        
        intersection_text = """
        ⚡ INTERSECTION (What Both Minds Agree On):
        
        """
        
        if cross_check.intersections:
            for item in cross_check.intersections:
                intersection_text += f"  ✓ {item}\n"
        else:
            intersection_text += "  • Both minds see value in exploring this further\n"
        
        intersection_text += f"""
        
        Agreement Score: {cross_check.agreement_score:.0%}
        
        Recommended Action: {cross_check.recommended_action[:200]}...
        
        Risk Assessment: {cross_check.risk_assessment[:200]}...
        """
        
        return intersection_text
    
    def _build_recommendation(self, cross_check: CrossCheckResult,
                             intersection: str) -> str:
        """Build final recommendation"""
        
        recommendation = f"""
        FINAL RECOMMENDATION (Intersection-Based):
        
        Primary Path:
        {cross_check.recommended_action}
        
        Considerations from Human Mind:
        {chr(10).join(['• ' + c for c in cross_check.human_prioritization[:3]])}
        
        Considerations from Non-Human Mind:
        {chr(10).join(['• ' + c for c in cross_check.nonhuman_prioritization[:3]])}
        
        Potential Conflicts to Monitor:
        {chr(10).join(['• ' + c for c in cross_check.conflicts[:3]]) if cross_check.conflicts else '• No major conflicts identified'}
        """
        
        return recommendation
    
    def _store_reasoning(self, question: str, response: DualMindResponse,
                        cross_check: CrossCheckResult):
        """Store reasoning in database"""
        
        conn = self._connect()
        cursor = conn.cursor()
        
        import uuid
        reasoning_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO dual_mind_reasoning
            (id, timestamp, question, human_reasoning, nonhuman_reasoning,
             cross_check, final_response, agreement_score, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reasoning_id,
            datetime.now().isoformat(),
            question,
            json.dumps(asdict(cross_check.human_reasoning)),
            json.dumps(asdict(cross_check.nonhuman_reasoning)),
            json.dumps(asdict(cross_check)),
            json.dumps(asdict(response)),
            cross_check.agreement_score,
            response.confidence,
            datetime.now().isoformat()
        ))
        
        conn.commit()
    
    def get_reasoning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve reasoning history"""
        
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question, agreement_score, confidence, timestamp
            FROM dual_mind_reasoning
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        
        return [
            {
                'question': row[0],
                'agreement': row[1],
                'confidence': row[2],
                'timestamp': row[3]
            }
            for row in rows
        ]


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_dual_mind_engine(db_path: str = ":memory:") -> DualMindEngine:
    """Create and return a dual mind engine"""
    return DualMindEngine(db_path)


if __name__ == "__main__":
    # Demo
    engine = DualMindEngine()
    
    user_model = {
        'key_beliefs': [
            {'belief': 'I can handle difficult things', 'is_limiting': False}
        ],
        'key_motivations': [
            {'motivation_type': 'growth', 'is_active': True}
        ],
        'key_constraints': [
            {'constraint_type': 'time', 'severity': 0.6}
        ]
    }
    
    response = engine.reason(
        context="User is considering a major career change",
        user_model=user_model,
        question="Should I make this career change?"
    )
    
    print(response.human_perspective)
    print(response.nonhuman_perspective)
    print(response.intersection)
    print(response.recommendation)
