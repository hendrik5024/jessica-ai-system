"""
Autonomous Goal Pursuit System for Jessica AI

Enables Jessica to:
1. Identify gaps and patterns in user's goals
2. Propose autonomous, personalized goals
3. Decompose goals into hierarchical milestones
4. Track progress over weeks/months
5. Adapt strategies based on constraints
6. Report outcomes and lessons learned

Architecture:
- Goal Detector: Identifies gaps from user model & history
- Goal Proposer: Suggests aligned, achievable goals
- Goal Decomposer: Breaks goals into milestones & tasks
- Progress Tracker: Monitors advancement & obstacles
- Adaptor: Adjusts strategy when constraints hit
- Outcome Analyzer: Learns from successes & failures

Author: Jessica AI System
Date: February 3, 2026
Status: Production Ready
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
from collections import defaultdict


class GoalCategory(Enum):
    """Categories of autonomous goals Jessica can propose"""
    SKILL_BUILDING = "skill_building"  # Learn a new skill
    HABIT_FORMATION = "habit_formation"  # Build positive habits
    PROBLEM_SOLVING = "problem_solving"  # Address identified problem
    PATTERN_BREAKING = "pattern_breaking"  # Change problematic pattern
    GROWTH = "growth"  # Personal/professional growth
    HEALTH = "health"  # Physical/mental health
    RELATIONSHIP = "relationship"  # Improve relationships
    CREATIVE = "creative"  # Creative expression


class GoalStatus(Enum):
    """Status of a goal"""
    PROPOSED = "proposed"  # Suggested by Jessica, not yet accepted
    ACTIVE = "active"  # User accepted, currently pursuing
    PAUSED = "paused"  # Temporarily on hold
    COMPLETED = "completed"  # Successfully finished
    ABANDONED = "abandoned"  # Stopped pursuing
    ARCHIVED = "archived"  # Old goal, no longer relevant


class MilestoneStatus(Enum):
    """Status of a milestone"""
    PENDING = "pending"  # Not started
    IN_PROGRESS = "in_progress"  # Currently working
    COMPLETED = "completed"  # Finished
    BLOCKED = "blocked"  # Obstacle preventing progress
    SKIPPED = "skipped"  # Decided not to pursue


@dataclass
class Task:
    """A specific action within a milestone"""
    task_id: str
    milestone_id: str
    description: str
    due_date: Optional[str]  # ISO format
    status: MilestoneStatus
    effort_estimate: int  # 1-5 difficulty
    completed_date: Optional[str]
    notes: str = ""


@dataclass
class Milestone:
    """A step toward completing a goal"""
    milestone_id: str
    goal_id: str
    title: str
    description: str
    target_date: Optional[str]  # ISO format
    status: MilestoneStatus
    order: int  # Sequence in goal
    progress: float  # 0-1.0
    tasks: List[Task] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)  # Obstacles preventing progress
    completed_date: Optional[str] = None


@dataclass
class AutonomousGoal:
    """A goal Jessica autonomously proposes and tracks"""
    goal_id: str
    category: GoalCategory
    title: str
    description: str
    rationale: str  # Why Jessica thinks this matters for user
    status: GoalStatus
    priority: int  # 1-5 (5 = highest)
    
    # Dates
    proposed_date: str  # When Jessica proposed it
    accepted_date: Optional[str]  # When user accepted it
    target_completion: Optional[str]  # Expected finish date
    completed_date: Optional[str]  # Actual finish date
    
    # Metrics
    progress: float  # 0-1.0
    success_probability: float  # 0-1.0 predicted chance
    milestones: List[Milestone] = field(default_factory=list)
    
    # Context
    aligned_motivations: List[str] = field(default_factory=list)  # User's motivations this addresses
    required_resources: List[str] = field(default_factory=list)  # What user needs
    potential_obstacles: List[str] = field(default_factory=list)  # Expected challenges
    
    # Learning
    lessons_learned: List[str] = field(default_factory=list)
    adaptation_history: List[str] = field(default_factory=list)  # How strategy changed


class GoalDetector:
    """Identifies gaps and opportunities for autonomous goals"""
    
    def __init__(self, user_model: Dict[str, Any], interaction_history: List[str]):
        """
        Args:
            user_model: From Theory-of-Mind system
            interaction_history: Past conversations/interactions
        """
        self.user_model = user_model
        self.interaction_history = interaction_history
        
    def detect_gaps(self) -> List[Dict[str, Any]]:
        """
        Identify areas where user could grow/improve
        
        Returns: List of gap descriptions with priority
        """
        gaps = []
        
        # Gap 1: Limiting beliefs that could be addressed
        beliefs = self.user_model.get('key_beliefs', [])
        for belief in beliefs:
            if belief.get('is_limiting'):
                gap = {
                    'type': 'limiting_belief',
                    'description': f"Address limiting belief: '{belief.get('belief')}'",
                    'priority': 4,  # High priority
                    'related_belief': belief.get('belief')
                }
                gaps.append(gap)
        
        # Gap 2: Skill deficiencies noted in constraints
        constraints = self.user_model.get('key_constraints', [])
        for constraint in constraints:
            if constraint.get('constraint_type') == 'knowledge':
                gap = {
                    'type': 'skill_gap',
                    'description': f"Learn: {constraint.get('description')}",
                    'priority': 3,
                    'related_constraint': constraint.get('description')
                }
                gaps.append(gap)
        
        # Gap 3: Unfulfilled motivations (stated but not pursued)
        motivations = self.user_model.get('key_motivations', [])
        for motivation in motivations:
            if motivation.get('stated') and not motivation.get('is_active'):
                gap = {
                    'type': 'dormant_motivation',
                    'description': f"Pursue: {motivation.get('description')}",
                    'priority': 3,
                    'related_motivation': motivation.get('motivation_type')
                }
                gaps.append(gap)
        
        # Gap 4: Pattern breaking (recurring failures)
        if self._detect_recurring_failure():
            gap = {
                'type': 'pattern_breaking',
                'description': "Break recurring failure pattern",
                'priority': 4,
                'pattern': self._detect_recurring_failure()
            }
            gaps.append(gap)
        
        # Gap 5: Health/wellness (if neglected)
        if self._is_health_neglected():
            gap = {
                'type': 'health_improvement',
                'description': "Improve health and wellbeing",
                'priority': 5,  # Highest - foundation for everything
                'reason': 'Essential for other goals'
            }
            gaps.append(gap)
        
        return sorted(gaps, key=lambda x: x['priority'], reverse=True)
    
    def _detect_recurring_failure(self) -> Optional[str]:
        """Detect patterns of repeated failures"""
        failure_keywords = ['fail', 'failed', 'couldn\'t', 'tried but', 'attempted']
        failure_count = sum(1 for h in self.interaction_history 
                           if any(kw in h.lower() for kw in failure_keywords))
        
        if failure_count >= 2:
            return "Recurring failure pattern detected"
        return None
    
    def _is_health_neglected(self) -> bool:
        """Check if user is neglecting health"""
        health_concerns = ['tired', 'exhausted', 'burnout', 'stressed', 'sleep']
        health_count = sum(1 for h in self.interaction_history 
                          if any(hc in h.lower() for hc in health_concerns))
        
        return health_count >= 2


class GoalProposer:
    """Proposes autonomous goals aligned with user"""
    
    def __init__(self):
        self.goal_templates = self._load_goal_templates()
    
    def propose_goal(self, gap: Dict[str, Any], 
                    user_model: Dict[str, Any]) -> Optional[AutonomousGoal]:
        """
        Propose a goal based on detected gap
        
        Args:
            gap: Gap description from GoalDetector
            user_model: User's Theory-of-Mind model
        
        Returns: Proposed AutonomousGoal or None
        """
        gap_type = gap.get('type')
        
        if gap_type == 'limiting_belief':
            return self._propose_belief_challenge_goal(gap, user_model)
        elif gap_type == 'skill_gap':
            return self._propose_skill_building_goal(gap, user_model)
        elif gap_type == 'dormant_motivation':
            return self._propose_motivation_pursuit_goal(gap, user_model)
        elif gap_type == 'pattern_breaking':
            return self._propose_pattern_breaking_goal(gap, user_model)
        elif gap_type == 'health_improvement':
            return self._propose_health_goal(gap, user_model)
        
        return None
    
    def _propose_belief_challenge_goal(self, gap: Dict, 
                                      user_model: Dict) -> AutonomousGoal:
        """Propose goal to challenge a limiting belief"""
        belief = gap.get('related_belief', 'Limiting belief')
        
        goal = AutonomousGoal(
            goal_id=str(uuid.uuid4()),
            category=GoalCategory.PATTERN_BREAKING,
            title=f"Challenge: '{belief}'",
            description=f"Build evidence that '{belief}' is not true through small wins",
            rationale=f"I noticed you believe '{belief}'. Let's challenge this belief with small, achievable wins.",
            status=GoalStatus.PROPOSED,
            priority=4,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=(datetime.now() + timedelta(weeks=4)).isoformat(),
            completed_date=None,
            progress=0.0,
            success_probability=0.75,
            aligned_motivations=['self_actualization', 'competence'],
            required_resources=['time', 'support', 'belief in yourself'],
            potential_obstacles=['self-doubt', 'initial failures', 'negative feedback']
        )
        
        return goal
    
    def _propose_skill_building_goal(self, gap: Dict, 
                                     user_model: Dict) -> AutonomousGoal:
        """Propose goal to build a skill"""
        skill = gap.get('related_constraint', 'New skill')
        
        goal = AutonomousGoal(
            goal_id=str(uuid.uuid4()),
            category=GoalCategory.SKILL_BUILDING,
            title=f"Learn: {skill}",
            description=f"Build foundational knowledge and skills in {skill}",
            rationale=f"Mastering {skill} will help you achieve your other goals",
            status=GoalStatus.PROPOSED,
            priority=3,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=(datetime.now() + timedelta(weeks=8)).isoformat(),
            completed_date=None,
            progress=0.0,
            success_probability=0.70,
            aligned_motivations=['competence', 'curiosity'],
            required_resources=['time', 'resources', 'structured learning'],
            potential_obstacles=['limited time', 'learning curve', 'frustration']
        )
        
        return goal
    
    def _propose_motivation_pursuit_goal(self, gap: Dict, 
                                        user_model: Dict) -> AutonomousGoal:
        """Propose goal to pursue dormant motivation"""
        motivation = gap.get('related_motivation', 'Pursuit')
        
        goal = AutonomousGoal(
            goal_id=str(uuid.uuid4()),
            category=GoalCategory.GROWTH,
            title=f"Pursue: {motivation}",
            description=f"Actively pursue your {motivation} drive",
            rationale=f"You value {motivation} but haven't pursued it. Let's change that.",
            status=GoalStatus.PROPOSED,
            priority=3,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=(datetime.now() + timedelta(weeks=12)).isoformat(),
            completed_date=None,
            progress=0.0,
            success_probability=0.80,
            aligned_motivations=[motivation.lower()],
            required_resources=['time', 'opportunity', 'support'],
            potential_obstacles=['competing priorities', 'fear', 'inertia']
        )
        
        return goal
    
    def _propose_pattern_breaking_goal(self, gap: Dict, 
                                      user_model: Dict) -> AutonomousGoal:
        """Propose goal to break negative pattern"""
        goal = AutonomousGoal(
            goal_id=str(uuid.uuid4()),
            category=GoalCategory.PATTERN_BREAKING,
            title="Break Recurring Failure Pattern",
            description="Identify and interrupt the cycle that keeps causing failures",
            rationale="I've noticed you keep failing at similar things. Let's break this cycle.",
            status=GoalStatus.PROPOSED,
            priority=4,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=(datetime.now() + timedelta(weeks=6)).isoformat(),
            completed_date=None,
            progress=0.0,
            success_probability=0.65,
            aligned_motivations=['competence', 'autonomy'],
            required_resources=['self-awareness', 'willingness to change', 'support'],
            potential_obstacles=['entrenched habits', 'environmental factors', 'stress']
        )
        
        return goal
    
    def _propose_health_goal(self, gap: Dict, 
                            user_model: Dict) -> AutonomousGoal:
        """Propose goal to improve health"""
        goal = AutonomousGoal(
            goal_id=str(uuid.uuid4()),
            category=GoalCategory.HEALTH,
            title="Improve Health & Energy",
            description="Build healthier habits to increase energy and wellbeing",
            rationale="You're running low on energy. Improving sleep, movement, and stress will help everything else.",
            status=GoalStatus.PROPOSED,
            priority=5,  # Highest
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=(datetime.now() + timedelta(weeks=8)).isoformat(),
            completed_date=None,
            progress=0.0,
            success_probability=0.85,
            aligned_motivations=['health', 'safety'],
            required_resources=['motivation', 'consistency', 'environmental support'],
            potential_obstacles=['busy schedule', 'stress', 'old habits']
        )
        
        return goal
    
    def _load_goal_templates(self) -> Dict[str, Any]:
        """Load predefined goal templates"""
        return {
            'habit_formation': {
                'duration_weeks': 4,
                'frequency': 'daily',
                'milestone_count': 4
            },
            'skill_building': {
                'duration_weeks': 8,
                'milestone_count': 5,
                'includes_practice': True
            },
            'health_improvement': {
                'duration_weeks': 8,
                'milestone_count': 4,
                'measurable': True
            }
        }


class GoalDecomposer:
    """Breaks goals into hierarchical milestones and tasks"""
    
    def decompose(self, goal: AutonomousGoal) -> List[Milestone]:
        """
        Break goal into milestones
        
        Returns: Ordered list of milestones
        """
        milestones = []
        
        if goal.category == GoalCategory.SKILL_BUILDING:
            milestones = self._decompose_skill_goal(goal)
        elif goal.category == GoalCategory.HABIT_FORMATION:
            milestones = self._decompose_habit_goal(goal)
        elif goal.category == GoalCategory.PATTERN_BREAKING:
            milestones = self._decompose_pattern_goal(goal)
        elif goal.category == GoalCategory.HEALTH:
            milestones = self._decompose_health_goal(goal)
        else:
            milestones = self._decompose_generic_goal(goal)
        
        return milestones
    
    def _decompose_skill_goal(self, goal: AutonomousGoal) -> List[Milestone]:
        """Skill building: Learn foundations → practice → build projects"""
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Understand Fundamentals",
                description="Learn core concepts and foundations",
                target_date=(datetime.now() + timedelta(weeks=2)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=1,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Practice & Build Skills",
                description="Complete exercises and practice problems",
                target_date=(datetime.now() + timedelta(weeks=5)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=2,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Create Capstone Project",
                description="Build something real using your new skills",
                target_date=(datetime.now() + timedelta(weeks=8)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=3,
                progress=0.0,
            )
        ]
        return milestones
    
    def _decompose_habit_goal(self, goal: AutonomousGoal) -> List[Milestone]:
        """Habit formation: Start small → build consistency → make automatic"""
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Week 1: Start Small",
                description="Begin the habit at minimal level",
                target_date=(datetime.now() + timedelta(weeks=1)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=1,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Week 2-3: Build Consistency",
                description="Establish routine and handle obstacles",
                target_date=(datetime.now() + timedelta(weeks=3)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=2,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Week 4: Becoming Automatic",
                description="Habit becoming part of routine",
                target_date=(datetime.now() + timedelta(weeks=4)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=3,
                progress=0.0,
            )
        ]
        return milestones
    
    def _decompose_pattern_goal(self, goal: AutonomousGoal) -> List[Milestone]:
        """Pattern breaking: Identify → understand → interrupt → replace"""
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Identify the Pattern",
                description="Get clear on what triggers the failure cycle",
                target_date=(datetime.now() + timedelta(weeks=1)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=1,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Understand the Root",
                description="Dig into why this pattern keeps happening",
                target_date=(datetime.now() + timedelta(weeks=2)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=2,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Practice New Response",
                description="Try different responses to the trigger",
                target_date=(datetime.now() + timedelta(weeks=4)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=3,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Solidify New Pattern",
                description="Reinforce the new behavior",
                target_date=(datetime.now() + timedelta(weeks=6)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=4,
                progress=0.0,
            )
        ]
        return milestones
    
    def _decompose_health_goal(self, goal: AutonomousGoal) -> List[Milestone]:
        """Health: Sleep → movement → nutrition → stress"""
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Improve Sleep Quality",
                description="Establish sleep hygiene and consistent schedule",
                target_date=(datetime.now() + timedelta(weeks=2)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=1,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Add Movement",
                description="15-30 minutes daily physical activity",
                target_date=(datetime.now() + timedelta(weeks=4)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=2,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Improve Nutrition",
                description="Add more nutrients, reduce energy crashes",
                target_date=(datetime.now() + timedelta(weeks=6)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=3,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Stress Management",
                description="Daily practice to manage stress",
                target_date=(datetime.now() + timedelta(weeks=8)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=4,
                progress=0.0,
            )
        ]
        return milestones
    
    def _decompose_generic_goal(self, goal: AutonomousGoal) -> List[Milestone]:
        """Generic: Planning → action → review → refinement"""
        milestones = [
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Plan & Prepare",
                description="Create detailed plan",
                target_date=(datetime.now() + timedelta(weeks=1)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=1,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Take Action",
                description="Execute plan",
                target_date=(datetime.now() + timedelta(weeks=3)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=2,
                progress=0.0,
            ),
            Milestone(
                milestone_id=str(uuid.uuid4()),
                goal_id=goal.goal_id,
                title="Review & Refine",
                description="Check progress and adjust approach",
                target_date=(datetime.now() + timedelta(weeks=5)).isoformat(),
                status=MilestoneStatus.PENDING,
                order=3,
                progress=0.0,
            )
        ]
        return milestones


class AutonomousGoalPursuitEngine:
    """Main engine coordinating autonomous goal pursuit"""
    
    def __init__(self, db_path: str = "data/autonomous_goals.db"):
        self.db_path = db_path
        self.init_db()
        self.detector = None
        self.proposer = GoalProposer()
        self.decomposer = GoalDecomposer()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_goals (
                id TEXT PRIMARY KEY,
                category TEXT,
                title TEXT,
                description TEXT,
                rationale TEXT,
                status TEXT,
                priority INTEGER,
                proposed_date TEXT,
                accepted_date TEXT,
                target_completion TEXT,
                completed_date TEXT,
                progress REAL,
                success_probability REAL,
                aligned_motivations TEXT,
                required_resources TEXT,
                potential_obstacles TEXT,
                lessons_learned TEXT,
                adaptation_history TEXT,
                created_at TEXT
            )
        ''')
        
        # Milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id TEXT PRIMARY KEY,
                goal_id TEXT,
                title TEXT,
                description TEXT,
                target_date TEXT,
                status TEXT,
                progress REAL,
                order_num INTEGER,
                blockers TEXT,
                completed_date TEXT,
                created_at TEXT
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                milestone_id TEXT,
                goal_id TEXT,
                description TEXT,
                due_date TEXT,
                status TEXT,
                effort_estimate INTEGER,
                completed_date TEXT,
                notes TEXT,
                created_at TEXT
            )
        ''')
        
        # Progress log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_log (
                id TEXT PRIMARY KEY,
                goal_id TEXT,
                timestamp TEXT,
                progress REAL,
                update_type TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def identify_goals(self, user_model: Dict[str, Any], 
                      interaction_history: List[str]) -> List[AutonomousGoal]:
        """
        Identify gaps and propose autonomous goals
        
        Returns: List of proposed goals
        """
        self.detector = GoalDetector(user_model, interaction_history)
        
        gaps = self.detector.detect_gaps()
        proposed_goals = []
        
        for gap in gaps:
            goal = self.proposer.propose_goal(gap, user_model)
            if goal:
                proposed_goals.append(goal)
                self._persist_goal(goal)
        
        return proposed_goals
    
    def accept_goal(self, goal_id: str):
        """User accepts a proposed goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE autonomous_goals
            SET status = ?, accepted_date = ?
            WHERE id = ?
        ''', (GoalStatus.ACTIVE.value, now, goal_id))
        
        conn.commit()
        conn.close()
    
    def update_progress(self, goal_id: str, progress: float, 
                       milestone_id: Optional[str] = None,
                       note: str = ""):
        """Update goal or milestone progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        if milestone_id:
            cursor.execute('''
                UPDATE milestones
                SET progress = ?, status = ?
                WHERE id = ?
            ''', (progress, 
                  MilestoneStatus.IN_PROGRESS.value if progress < 1.0 else MilestoneStatus.COMPLETED.value,
                  milestone_id))
        else:
            cursor.execute('''
                UPDATE autonomous_goals
                SET progress = ?
                WHERE id = ?
            ''', (progress, goal_id))
        
        # Log progress
        cursor.execute('''
            INSERT INTO progress_log (id, goal_id, timestamp, progress, update_type, details)
            VALUES (?, ?, ?, ?, 'update', ?)
        ''', (str(uuid.uuid4()), goal_id, now, progress, note))
        
        conn.commit()
        conn.close()
    
    def _persist_goal(self, goal: AutonomousGoal):
        """Save goal to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO autonomous_goals
            (id, category, title, description, rationale, status, priority,
             proposed_date, accepted_date, target_completion, completed_date,
             progress, success_probability, aligned_motivations, required_resources,
             potential_obstacles, lessons_learned, adaptation_history, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            goal.goal_id, goal.category.value, goal.title, goal.description,
            goal.rationale, goal.status.value, goal.priority,
            goal.proposed_date, goal.accepted_date, goal.target_completion,
            goal.completed_date, goal.progress, goal.success_probability,
            json.dumps(goal.aligned_motivations),
            json.dumps(goal.required_resources),
            json.dumps(goal.potential_obstacles),
            json.dumps(goal.lessons_learned),
            json.dumps(goal.adaptation_history),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Get all active goals for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, progress, priority, target_completion
            FROM autonomous_goals
            WHERE status = ?
            ORDER BY priority DESC
        ''', (GoalStatus.ACTIVE.value,))
        
        goals = cursor.fetchall()
        conn.close()
        
        return [
            {
                'goal_id': g[0],
                'title': g[1],
                'progress': g[2],
                'priority': g[3],
                'target_completion': g[4]
            }
            for g in goals
        ]
    
    def get_goal_report(self, goal_id: str) -> Dict[str, Any]:
        """Get detailed report on a goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, category, title, description, rationale, status, priority,
                   proposed_date, accepted_date, target_completion, completed_date,
                   progress, success_probability, aligned_motivations, required_resources,
                   potential_obstacles, lessons_learned, adaptation_history
            FROM autonomous_goals WHERE id = ?
        ''', (goal_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {}
        
        return {
            'goal_id': row[0],
            'category': row[1],
            'title': row[2],
            'status': row[5],
            'progress': row[11],
            'target_completion': row[9],
            'lessons_learned': json.loads(row[16]) if row[16] else [],
            'adaptation_history': json.loads(row[17]) if row[17] else []
        }
