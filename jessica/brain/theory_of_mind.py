"""
Advanced Theory-of-Mind Engine for Jessica AI

This module builds dynamic models of user motivations, beliefs, constraints,
and values through multi-turn interactions. It enables Jessica to:

1. Infer underlying user goals and motivations
2. Detect limiting beliefs and constraints
3. Synthesize behavioral patterns
4. Track value alignment
5. Predict intervention effectiveness

Author: Jessica AI System
Date: February 3, 2026
Status: Production Ready
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import re
from enum import Enum


class MotivationType(Enum):
    """Categories of human motivation (Maslow + Self-Determination Theory)"""
    SAFETY = "safety"  # Security, stability, predictability
    BELONGING = "belonging"  # Connection, acceptance, relationships
    COMPETENCE = "competence"  # Mastery, skill-building, achievement
    AUTONOMY = "autonomy"  # Freedom, control, self-determination
    SELF_ACTUALIZATION = "self_actualization"  # Growth, meaning, purpose
    CURIOSITY = "curiosity"  # Learning, exploration, understanding
    HEALTH = "health"  # Physical/mental wellbeing, energy
    FINANCIAL = "financial"  # Money, security, resources


class ConstraintType(Enum):
    """Categories of user constraints"""
    TIME = "time"  # Limited time/schedule
    ENERGY = "energy"  # Fatigue, burnout, health limitations
    KNOWLEDGE = "knowledge"  # Lack of understanding/skills
    RESOURCES = "resources"  # Money, tools, access
    SOCIAL = "social"  # Relationships, support, approval
    PSYCHOLOGICAL = "psychological"  # Fear, anxiety, trauma, limiting beliefs
    STRUCTURAL = "structural"  # Systems, organizations, rules limiting them
    FINANCIAL = "financial"  # Financial/resource constraints (alias for resources)


@dataclass
class UserBelief:
    """Represents an inferred user belief"""
    belief: str  # The belief itself
    is_limiting: bool  # True if holds user back
    confidence: float  # 0-1 confidence score
    evidence_count: int  # How many times observed
    first_observed: str  # ISO timestamp
    last_observed: str  # ISO timestamp
    domain: str  # Which knowledge domain it relates to


@dataclass
class UserConstraint:
    """Represents an inferred constraint on user"""
    constraint_type: ConstraintType
    description: str
    severity: float  # 0-1 (1 = major blocker)
    evidence: List[str]  # Statements or behaviors indicating this
    first_observed: str
    last_observed: str


@dataclass
class UserMotivation:
    """Represents an inferred user motivation"""
    motivation_type: MotivationType
    description: str  # Specific goal or aspiration
    intensity: float  # 0-1 (how important is this)
    stated: bool  # True if user explicitly said it
    frequency: int  # How often mentioned/implied
    is_active: bool  # Actively pursuing now?
    first_observed: str
    last_observed: str


@dataclass
class BehaviorPattern:
    """Represents a recurring user behavior pattern"""
    pattern_name: str
    description: str
    frequency: int  # Times observed
    contexts: List[str]  # Where/when it happens
    outcomes: List[str]  # What happens as result
    is_productive: Optional[bool]  # None=neutral, True=helpful, False=harmful
    opportunities: List[str]  # How to leverage or redirect


@dataclass
class UserValue:
    """Represents something the user values"""
    value: str  # What they value (e.g., "autonomy", "family", "learning")
    explicitly_stated: bool  # Did they say it directly?
    inferred_from: List[str]  # Behaviors/choices revealing this
    consistency: float  # 0-1 (how consistently they act on it)
    priority: int  # Relative priority vs other values


@dataclass
class InterventionPrediction:
    """Prediction of whether an intervention will be effective for user"""
    intervention: str
    predicted_effectiveness: float  # 0-1 confidence
    reasoning: str
    aligned_motivations: List[str]
    conflicting_constraints: List[str]
    alternative_suggestions: List[str]


class TheoryOfMindEngine:
    """
    Main engine for building and maintaining user models.
    
    Maintains persistent database of:
    - Inferred motivations
    - Discovered beliefs (especially limiting beliefs)
    - Detected constraints
    - Behavioral patterns
    - Value alignments
    
    Evolves through multi-turn interactions.
    """

    def __init__(self, db_path: str = "data/theory_of_mind.db"):
        self.db_path = db_path
        self._in_memory = db_path == ":memory:"
        if self._in_memory:
            # For in-memory DB, keep a persistent connection
            self.conn = sqlite3.connect(":memory:")
            self.init_db()
        else:
            self.conn = None
            self.init_db()
        self.motivation_patterns = self._load_motivation_patterns()
        self.constraint_patterns = self._load_constraint_patterns()
        self.belief_keywords = self._load_belief_keywords()

    def init_db(self):
        """Initialize database schema"""
        if self._in_memory:
            cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        # Beliefs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beliefs (
                id INTEGER PRIMARY KEY,
                belief TEXT UNIQUE,
                is_limiting INTEGER,
                confidence REAL,
                evidence_count INTEGER,
                first_observed TEXT,
                last_observed TEXT,
                domain TEXT,
                created_at TEXT
            )
        ''')

        # Constraints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS constraints (
                id INTEGER PRIMARY KEY,
                constraint_type TEXT,
                description TEXT UNIQUE,
                severity REAL,
                evidence TEXT,
                first_observed TEXT,
                last_observed TEXT,
                created_at TEXT
            )
        ''')

        # Motivations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motivations (
                id INTEGER PRIMARY KEY,
                motivation_type TEXT,
                description TEXT UNIQUE,
                intensity REAL,
                stated INTEGER,
                frequency INTEGER,
                is_active INTEGER,
                first_observed TEXT,
                last_observed TEXT,
                created_at TEXT
            )
        ''')

        # Behavior patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_patterns (
                id INTEGER PRIMARY KEY,
                pattern_name TEXT UNIQUE,
                description TEXT,
                frequency INTEGER,
                contexts TEXT,
                outcomes TEXT,
                is_productive INTEGER,
                opportunities TEXT,
                created_at TEXT
            )
        ''')

        # User_values table (renamed to avoid SQLite reserved word)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_values (
                id INTEGER PRIMARY KEY,
                value TEXT UNIQUE,
                explicitly_stated INTEGER,
                inferred_from TEXT,
                consistency REAL,
                priority INTEGER,
                created_at TEXT
            )
        ''')

        # Interaction history (for pattern detection)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                user_statement TEXT,
                assistant_response TEXT,
                detected_motivations TEXT,
                detected_constraints TEXT,
                detected_beliefs TEXT,
                interaction_timestamp TEXT
            )
        ''')

        if self._in_memory:
            self.conn.commit()
        else:
            conn.commit()
            conn.close()

    def analyze_user_statement(self, statement: str) -> Dict[str, Any]:
        """
        Analyze a single user statement for motivations, beliefs, constraints.
        Also persists findings to database for long-term model building.
        
        Returns dict with:
        {
            'inferred_motivations': [UserMotivation, ...],
            'inferred_beliefs': [UserBelief, ...],
            'detected_constraints': [UserConstraint, ...],
            'behavioral_cues': [str, ...],
            'needs_follow_up': bool,
            'followup_questions': [str, ...]
        }
        """
        result = {
            'inferred_motivations': [],
            'inferred_beliefs': [],
            'detected_constraints': [],
            'behavioral_cues': [],
            'needs_follow_up': False,
            'followup_questions': []
        }

        # Detect motivations
        result['inferred_motivations'] = self._extract_motivations(statement)

        # Detect beliefs (especially limiting ones)
        result['inferred_beliefs'] = self._extract_beliefs(statement)

        # Detect constraints
        result['detected_constraints'] = self._extract_constraints(statement)

        # Detect behavioral cues (tone, confidence level, etc.)
        result['behavioral_cues'] = self._extract_behavioral_cues(statement)

        # Determine if follow-up needed for deeper understanding
        if len(result['inferred_beliefs']) > 0 or len(result['detected_constraints']) > 0:
            result['needs_follow_up'] = True
            result['followup_questions'] = self._generate_followup_questions(
                result['inferred_beliefs'],
                result['detected_constraints'],
                result['inferred_motivations']
            )

        # Persist to database
        self._persist_analysis(statement, result)

        return result

    def _persist_analysis(self, statement: str, analysis: Dict[str, Any]):
        """Persist analysis results to database"""
        if self._in_memory:
            cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        # Persist beliefs
        for belief in analysis['inferred_beliefs']:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO beliefs
                (belief, is_limiting, confidence, evidence_count, first_observed, last_observed, domain, created_at)
                VALUES (?, ?, ?, 1, ?, ?, 'psychology', ?)
            ''', (belief.belief, 1 if belief.is_limiting else 0, belief.confidence, now, now, now))

        # Persist constraints
        for constraint in analysis['detected_constraints']:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO constraints
                (constraint_type, description, severity, evidence, first_observed, last_observed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (constraint.constraint_type.value, constraint.description, constraint.severity, 
                  json.dumps(constraint.evidence), now, now, now))

        # Persist motivations
        for motivation in analysis['inferred_motivations']:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO motivations
                (motivation_type, description, intensity, stated, frequency, is_active, first_observed, last_observed, created_at)
                VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
            ''', (motivation.motivation_type.value, motivation.description, motivation.intensity, 
                  1 if motivation.stated else 0, 1 if motivation.is_active else 0, now, now, now))

        if self._in_memory:
            self.conn.commit()
        else:
            conn.commit()
            conn.close()

    def _extract_motivations(self, statement: str) -> List[UserMotivation]:
        """Extract motivation signals from statement"""
        motivations = []
        statement_lower = statement.lower()

        # Define motivation keywords
        motivation_keywords = {
            MotivationType.AUTONOMY: [
                "want to decide", "need control", "freedom", "independent",
                "my choice", "don't want to be told", "prefer to", "on my terms"
            ],
            MotivationType.COMPETENCE: [
                "want to learn", "get better at", "master", "improve", "skill",
                "achieve", "succeed", "prove", "accomplish"
            ],
            MotivationType.BELONGING: [
                "want to connect", "feel alone", "need support", "community",
                "relationship", "understand me", "accepted", "belong"
            ],
            MotivationType.SAFETY: [
                "worried about", "afraid of", "concerned", "nervous", "security",
                "stability", "predictable", "control risk"
            ],
            MotivationType.HEALTH: [
                "tired", "exhausted", "energized", "healthy", "sleep", "exercise",
                "mental health", "stress", "anxiety", "panic"
            ],
            MotivationType.FINANCIAL: [
                "money", "afford", "cost", "expensive", "budget", "debt",
                "save", "earn", "income"
            ],
            MotivationType.SELF_ACTUALIZATION: [
                "purpose", "meaning", "passion", "legacy", "potential",
                "calling", "mission", "unique", "authentic"
            ],
            MotivationType.CURIOSITY: [
                "why", "understand", "explain", "curious", "wonder",
                "explore", "discover", "question"
            ]
        }

        for mtype, keywords in motivation_keywords.items():
            for keyword in keywords:
                if keyword in statement_lower:
                    intensity = 0.7 if len(motivations) == 0 else 0.5
                    motivation = UserMotivation(
                        motivation_type=mtype,
                        description=statement[:100],  # First 100 chars as description
                        intensity=intensity,
                        stated=True,
                        frequency=1,
                        is_active=True,
                        first_observed=datetime.now().isoformat(),
                        last_observed=datetime.now().isoformat()
                    )
                    motivations.append(motivation)
                    break

        return motivations

    def _extract_beliefs(self, statement: str) -> List[UserBelief]:
        """Extract belief statements (especially limiting beliefs)"""
        beliefs = []
        statement_lower = statement.lower()

        # Limiting belief patterns
        limiting_belief_patterns = [
            r"i (can't|cannot|am not|will never)",
            r"i'm (not good|too old|too young|not smart|not capable)",
            r"it's (impossible|too hard|hopeless|not for me)",
            r"people like me (can't|don't)",
            r"i (always|never) (succeed|fail|get)",
            r"i don't know if i",  # Uncertainty about abilities
            r"don't (have|know|think)",  # Lack statements
        ]

        for pattern in limiting_belief_patterns:
            matches = re.findall(pattern, statement_lower)
            if matches:
                beliefs.append(UserBelief(
                    belief=statement[:150],
                    is_limiting=True,
                    confidence=0.8,
                    evidence_count=1,
                    first_observed=datetime.now().isoformat(),
                    last_observed=datetime.now().isoformat(),
                    domain="psychology"
                ))
                break

        # Positive belief patterns
        positive_belief_patterns = [
            r"i (can|am|will)",
            r"i'm (good|capable|smart|learning)",
            r"it's (possible|doable|achievable)",
        ]

        for pattern in positive_belief_patterns:
            if re.search(pattern, statement_lower):
                beliefs.append(UserBelief(
                    belief=statement[:150],
                    is_limiting=False,
                    confidence=0.7,
                    evidence_count=1,
                    first_observed=datetime.now().isoformat(),
                    last_observed=datetime.now().isoformat(),
                    domain="psychology"
                ))
                break

        return beliefs

    def _extract_constraints(self, statement: str) -> List[UserConstraint]:
        """Extract constraint signals"""
        constraints = []
        statement_lower = statement.lower()

        constraint_keywords = {
            ConstraintType.TIME: ["busy", "no time", "schedule", "deadline", "rush", "crammed"],
            ConstraintType.ENERGY: ["tired", "exhausted", "burnout", "burned out", "burnt out", "no energy", "depleted"],
            ConstraintType.KNOWLEDGE: ["don't know", "confused", "don't understand", "new to"],
            ConstraintType.FINANCIAL: ["money", "afford", "can't afford", "no money", "limited resources", "broke", "financial"],
            ConstraintType.RESOURCES: ["resources", "tools", "access"],
            ConstraintType.SOCIAL: ["alone", "no support", "isolated", "judged", "pressure"],
            ConstraintType.PSYCHOLOGICAL: ["afraid", "anxious", "depressed", "trauma", "stuck", "terrified"],
            ConstraintType.STRUCTURAL: ["rules say", "company policy", "can't change", "system won't"]
        }

        for ctype, keywords in constraint_keywords.items():
            for keyword in keywords:
                if keyword in statement_lower:
                    constraints.append(UserConstraint(
                        constraint_type=ctype,
                        description=f"{ctype.value}: {statement[:100]}",
                        severity=0.7,
                        evidence=[statement],
                        first_observed=datetime.now().isoformat(),
                        last_observed=datetime.now().isoformat()
                    ))
                    break

        return constraints

    def _extract_behavioral_cues(self, statement: str) -> List[str]:
        """Extract behavioral and emotional cues"""
        cues = []

        # Confidence level
        if any(word in statement.lower() for word in ["definitely", "absolutely", "certain", "sure"]):
            cues.append("high_confidence")
        elif any(word in statement.lower() for word in ["maybe", "might", "probably", "unsure"]):
            cues.append("low_confidence")

        # Emotional valence
        if any(word in statement.lower() for word in ["love", "excited", "happy", "grateful"]):
            cues.append("positive_emotion")
        elif any(word in statement.lower() for word in ["hate", "angry", "frustrated", "devastated"]):
            cues.append("negative_emotion")

        # Help-seeking
        if "help" in statement.lower() or "?" in statement:
            cues.append("help_seeking")

        # Vulnerability
        if any(word in statement.lower() for word in ["struggle", "fail", "can't", "weak", "broken", "suffering"]):
            cues.append("vulnerability")

        return cues

    def _generate_followup_questions(self, beliefs: List[UserBelief],
                                   constraints: List[UserConstraint],
                                   motivations: List[UserMotivation]) -> List[str]:
        """Generate clarifying follow-up questions"""
        questions = []

        # Questions about limiting beliefs
        if any(b.is_limiting for b in beliefs):
            questions.append("What makes you think that belief is true? Can you give me an example?")
            questions.append("Has there been any time when this wasn't true?")

        # Questions about constraints
        if len(constraints) > 0:
            constraint = constraints[0]
            if constraint.constraint_type == ConstraintType.TIME:
                questions.append("What if you had just 15 minutes—what would be a small win?")
            elif constraint.constraint_type == ConstraintType.ENERGY:
                questions.append("When do you have the most energy? How could we work with your rhythm?")
            elif constraint.constraint_type == ConstraintType.PSYCHOLOGICAL:
                questions.append("What specifically are you afraid might happen?")

        # Questions about motivations
        if len(motivations) > 0:
            questions.append("What would success look like to you?")

        return questions[:3]  # Return top 3

    def _load_motivation_patterns(self) -> Dict:
        """Load motivation inference patterns"""
        return {}

    def _load_constraint_patterns(self) -> Dict:
        """Load constraint detection patterns"""
        return {}

    def _load_belief_keywords(self) -> Dict:
        """Load belief keywords"""
        return {}

    def update_belief(self, belief_text: str, is_limiting: bool = None, confidence: float = 0.7):
        """Update or add a belief in the database"""
        if self._in_memory:
            cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        cursor.execute('SELECT * FROM beliefs WHERE belief = ?', (belief_text,))
        existing = cursor.fetchone()

        now = datetime.now().isoformat()

        if existing:
            # Update existing belief
            cursor.execute('''
                UPDATE beliefs
                SET evidence_count = evidence_count + 1,
                    last_observed = ?,
                    confidence = MAX(confidence, ?)
                WHERE belief = ?
            ''', (now, confidence, belief_text))
        else:
            # Insert new belief
            cursor.execute('''
                INSERT INTO beliefs
                (belief, is_limiting, confidence, evidence_count, first_observed, last_observed, domain, created_at)
                VALUES (?, ?, ?, 1, ?, ?, 'psychology', ?)
            ''', (belief_text, 1 if is_limiting else 0, confidence, now, now, now))

        if self._in_memory:
            self.conn.commit()
        else:
            conn.commit()
            conn.close()

    def get_user_model_summary(self) -> Dict[str, Any]:
        """Get summary of current user model"""
        if self._in_memory:
            cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        # Get beliefs
        cursor.execute('SELECT belief, is_limiting, confidence FROM beliefs ORDER BY confidence DESC LIMIT 5')
        beliefs = cursor.fetchall()

        # Get constraints
        cursor.execute('SELECT constraint_type, description, severity FROM constraints ORDER BY severity DESC LIMIT 5')
        constraints = cursor.fetchall()

        # Get motivations
        cursor.execute('SELECT motivation_type, description, intensity FROM motivations ORDER BY intensity DESC LIMIT 5')
        motivations = cursor.fetchall()

        if not self._in_memory:
            conn.close()

        return {
            'key_beliefs': beliefs,
            'key_constraints': constraints,
            'key_motivations': motivations,
            'generated_at': datetime.now().isoformat()
        }

    def predict_intervention_effectiveness(self, intervention: str) -> InterventionPrediction:
        """
        Predict how effective an intervention will be for this user
        
        Considers:
        - User's motivations (aligned interventions score higher)
        - User's constraints (interventions working around constraints score higher)
        - User's beliefs (aligned with positive beliefs, challenges limiting beliefs)
        """
        if self._in_memory:
            cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        # Get user model
        cursor.execute('SELECT motivation_type, intensity FROM motivations WHERE is_active = 1')
        active_motivations = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT constraint_type, severity FROM constraints ORDER BY severity DESC')
        major_constraints = [row[0] for row in cursor.fetchall()[:3]]

        cursor.execute('SELECT belief FROM beliefs WHERE is_limiting = 1')
        limiting_beliefs = [row[0] for row in cursor.fetchall()]

        if not self._in_memory:
            conn.close()

        # Score effectiveness
        effectiveness = 0.5  # Start neutral

        # Boost for aligned motivations
        for motivation in active_motivations:
            if motivation.lower() in intervention.lower():
                effectiveness += 0.15

        # Boost for working around constraints
        for constraint in major_constraints:
            if constraint.lower() in intervention.lower():
                effectiveness += 0.1

        # Boost for addressing limiting beliefs
        for belief in limiting_beliefs[:2]:
            if belief[:30].lower() in intervention.lower():
                effectiveness += 0.1

        effectiveness = min(0.95, effectiveness)  # Cap at 0.95

        return InterventionPrediction(
            intervention=intervention,
            predicted_effectiveness=effectiveness,
            reasoning="Based on user's motivations, constraints, and beliefs",
            aligned_motivations=active_motivations,
            conflicting_constraints=major_constraints,
            alternative_suggestions=[]
        )
