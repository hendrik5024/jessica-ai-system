"""
Test Suite for Autonomous Goal Pursuit System

Tests all components:
- Goal detection (identifying gaps)
- Goal proposal (suggesting aligned goals)
- Goal decomposition (breaking into milestones)
- Progress tracking
- Database persistence

Author: Jessica AI System
Date: February 3, 2026
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
import json

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jessica.brain.autonomous_goals import (
    GoalDetector, GoalProposer, GoalDecomposer, 
    AutonomousGoalPursuitEngine, GoalCategory, GoalStatus,
    AutonomousGoal, Milestone
)


class TestGoalDetector(unittest.TestCase):
    """Tests for goal detection from user model"""
    
    def setUp(self):
        self.user_model = {
            'key_beliefs': [
                {'belief': "I cannot do hard things", 'is_limiting': True},
                {'belief': "I am capable of learning", 'is_limiting': False}
            ],
            'key_constraints': [
                {'constraint_type': 'knowledge', 'description': 'Programming skills'}
            ],
            'key_motivations': [
                {'motivation_type': 'competence', 'description': 'Master coding', 'stated': True, 'is_active': False}
            ]
        }
        self.history = ['I fail at difficult things', 'I am tired all the time', 'Never tried coding before']
    
    def test_detect_limiting_belief_gap(self):
        """Test detection of limiting belief gaps"""
        detector = GoalDetector(self.user_model, self.history)
        gaps = detector.detect_gaps()
        
        self.assertTrue(len(gaps) > 0)
        self.assertTrue(any(g['type'] == 'limiting_belief' for g in gaps))
    
    def test_detect_skill_gap(self):
        """Test detection of skill gaps"""
        detector = GoalDetector(self.user_model, self.history)
        gaps = detector.detect_gaps()
        
        self.assertTrue(any(g['type'] == 'skill_gap' for g in gaps))
    
    def test_detect_dormant_motivation(self):
        """Test detection of unfulfilled motivations"""
        detector = GoalDetector(self.user_model, self.history)
        gaps = detector.detect_gaps()
        
        self.assertTrue(any(g['type'] == 'dormant_motivation' for g in gaps))
    
    def test_detect_recurring_failure(self):
        """Test detection of recurring failures"""
        history = ['I failed at this', 'I tried but failed', 'Failed again']
        detector = GoalDetector(self.user_model, history)
        gaps = detector.detect_gaps()
        
        # Recurring failures should be detected
        self.assertTrue(any(g['type'] == 'pattern_breaking' for g in gaps))
    
    def test_detect_health_neglect(self):
        """Test detection of neglected health"""
        history = ['I am exhausted', 'Burnt out and tired', 'Cannot sleep']
        detector = GoalDetector(self.user_model, history)
        gaps = detector.detect_gaps()
        
        # Health gap should be highest priority (5)
        health_gap = next((g for g in gaps if g['type'] == 'health_improvement'), None)
        self.assertIsNotNone(health_gap)
        self.assertEqual(health_gap['priority'], 5)
    
    def test_gaps_prioritized(self):
        """Test that gaps are returned in priority order"""
        detector = GoalDetector(self.user_model, self.history)
        gaps = detector.detect_gaps()
        
        # Should be sorted by priority (highest first)
        priorities = [g['priority'] for g in gaps]
        self.assertEqual(priorities, sorted(priorities, reverse=True))


class TestGoalProposer(unittest.TestCase):
    """Tests for goal proposal"""
    
    def setUp(self):
        self.proposer = GoalProposer()
        self.user_model = {'key_beliefs': []}
    
    def test_propose_belief_challenge_goal(self):
        """Test proposing a goal to challenge limiting belief"""
        gap = {'type': 'limiting_belief', 'related_belief': "I cannot learn"}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertIsNotNone(goal)
        self.assertEqual(goal.category, GoalCategory.PATTERN_BREAKING)
        self.assertEqual(goal.status, GoalStatus.PROPOSED)
        self.assertTrue("I cannot learn" in goal.title)
    
    def test_propose_skill_building_goal(self):
        """Test proposing skill building goal"""
        gap = {'type': 'skill_gap', 'related_constraint': 'Python Programming'}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertIsNotNone(goal)
        self.assertEqual(goal.category, GoalCategory.SKILL_BUILDING)
        self.assertIn('Learn', goal.title)
    
    def test_propose_health_goal(self):
        """Test proposing health improvement goal"""
        gap = {'type': 'health_improvement'}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertIsNotNone(goal)
        self.assertEqual(goal.category, GoalCategory.HEALTH)
        self.assertEqual(goal.priority, 5)  # Highest priority
    
    def test_goal_has_target_completion_date(self):
        """Test that proposed goals have target completion dates"""
        gap = {'type': 'skill_gap', 'related_constraint': 'C++'}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertIsNotNone(goal.target_completion)
        # Should be in future
        target_date = datetime.fromisoformat(goal.target_completion)
        self.assertGreater(target_date, datetime.now())
    
    def test_goal_has_success_probability(self):
        """Test that goals have success predictions"""
        gap = {'type': 'skill_gap', 'related_constraint': 'Java'}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertGreater(goal.success_probability, 0.0)
        self.assertLess(goal.success_probability, 1.0)
    
    def test_goal_aligned_with_motivations(self):
        """Test that goals are aligned with user motivations"""
        gap = {'type': 'skill_gap', 'related_constraint': 'Design'}
        goal = self.proposer.propose_goal(gap, self.user_model)
        
        self.assertTrue(len(goal.aligned_motivations) > 0)


class TestGoalDecomposer(unittest.TestCase):
    """Tests for goal decomposition"""
    
    def setUp(self):
        self.decomposer = GoalDecomposer()
    
    def test_decompose_skill_goal(self):
        """Test decomposing skill building goal"""
        goal = AutonomousGoal(
            goal_id='test1',
            category=GoalCategory.SKILL_BUILDING,
            title='Learn Python',
            description='Master Python programming',
            rationale='Important skill',
            status=GoalStatus.PROPOSED,
            priority=3,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=None,
            completed_date=None,
            progress=0.0,
            success_probability=0.75
        )
        
        milestones = self.decomposer.decompose(goal)
        
        self.assertEqual(len(milestones), 3)
        self.assertEqual(milestones[0].title, 'Understand Fundamentals')
        self.assertEqual(milestones[1].title, 'Practice & Build Skills')
        self.assertEqual(milestones[2].title, 'Create Capstone Project')
    
    def test_decompose_habit_goal(self):
        """Test decomposing habit formation goal"""
        goal = AutonomousGoal(
            goal_id='test2',
            category=GoalCategory.HABIT_FORMATION,
            title='Morning Exercise',
            description='Exercise 30 minutes each morning',
            rationale='Health improvement',
            status=GoalStatus.PROPOSED,
            priority=3,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=None,
            completed_date=None,
            progress=0.0,
            success_probability=0.80
        )
        
        milestones = self.decomposer.decompose(goal)
        
        self.assertEqual(len(milestones), 3)
        self.assertIn('Week 1', milestones[0].title)
        self.assertIn('Week 2-3', milestones[1].title)
        self.assertIn('Week 4', milestones[2].title)
    
    def test_decompose_pattern_breaking_goal(self):
        """Test decomposing pattern breaking goal"""
        goal = AutonomousGoal(
            goal_id='test3',
            category=GoalCategory.PATTERN_BREAKING,
            title='Break Procrastination Cycle',
            description='Stop procrastinating on important tasks',
            rationale='Pattern holding me back',
            status=GoalStatus.PROPOSED,
            priority=4,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=None,
            completed_date=None,
            progress=0.0,
            success_probability=0.65
        )
        
        milestones = self.decomposer.decompose(goal)
        
        self.assertEqual(len(milestones), 4)
        self.assertEqual(milestones[0].title, 'Identify the Pattern')
        self.assertEqual(milestones[1].title, 'Understand the Root')
    
    def test_decompose_health_goal(self):
        """Test decomposing health improvement goal"""
        goal = AutonomousGoal(
            goal_id='test4',
            category=GoalCategory.HEALTH,
            title='Improve Health',
            description='Sleep, exercise, nutrition',
            rationale='Foundation for other goals',
            status=GoalStatus.PROPOSED,
            priority=5,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=None,
            completed_date=None,
            progress=0.0,
            success_probability=0.85
        )
        
        milestones = self.decomposer.decompose(goal)
        
        self.assertEqual(len(milestones), 4)
        self.assertIn('Sleep', milestones[0].title)
        self.assertIn('Movement', milestones[1].title)
        self.assertIn('Nutrition', milestones[2].title)
    
    def test_milestones_ordered(self):
        """Test that milestones are in correct order"""
        goal = AutonomousGoal(
            goal_id='test5',
            category=GoalCategory.SKILL_BUILDING,
            title='Learn Design',
            description='Master design principles',
            rationale='Career goal',
            status=GoalStatus.PROPOSED,
            priority=3,
            proposed_date=datetime.now().isoformat(),
            accepted_date=None,
            target_completion=None,
            completed_date=None,
            progress=0.0,
            success_probability=0.75
        )
        
        milestones = self.decomposer.decompose(goal)
        
        # Check order numbers
        for i, milestone in enumerate(milestones, 1):
            self.assertEqual(milestone.order, i)


class TestAutonomousGoalEngine(unittest.TestCase):
    """Tests for main engine"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.engine = AutonomousGoalPursuitEngine(self.temp_db.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
    
    def test_identify_goals(self):
        """Test identifying goals from user model"""
        user_model = {
            'key_beliefs': [
                {'belief': "I can't succeed", 'is_limiting': True}
            ],
            'key_constraints': [],
            'key_motivations': []
        }
        history = []
        
        goals = self.engine.identify_goals(user_model, history)
        
        self.assertGreater(len(goals), 0)
    
    def test_accept_goal(self):
        """Test accepting a proposed goal"""
        user_model = {'key_beliefs': [], 'key_constraints': [], 'key_motivations': []}
        goals = self.engine.identify_goals(user_model, [])
        
        if len(goals) > 0:
            goal_id = goals[0].goal_id
            self.engine.accept_goal(goal_id)
            
            active_goals = self.engine.get_active_goals()
            self.assertTrue(any(g['goal_id'] == goal_id for g in active_goals))
    
    def test_update_progress(self):
        """Test updating goal progress"""
        user_model = {'key_beliefs': [], 'key_constraints': [], 'key_motivations': []}
        goals = self.engine.identify_goals(user_model, [])
        
        if len(goals) > 0:
            goal_id = goals[0].goal_id
            self.engine.update_progress(goal_id, 0.5, note='Halfway there')
            
            report = self.engine.get_goal_report(goal_id)
            self.assertEqual(report['progress'], 0.5)
    
    def test_get_active_goals(self):
        """Test retrieving active goals"""
        user_model = {'key_beliefs': [], 'key_constraints': [], 'key_motivations': []}
        goals = self.engine.identify_goals(user_model, [])
        
        if len(goals) > 0:
            goal_id = goals[0].goal_id
            self.engine.accept_goal(goal_id)
            
            active = self.engine.get_active_goals()
            self.assertTrue(len(active) > 0)
            self.assertTrue(any(g['goal_id'] == goal_id for g in active))


class TestGoalIntegration(unittest.TestCase):
    """Integration tests for full goal pursuit flow"""
    
    def test_full_goal_flow(self):
        """Test complete flow: detect → propose → decompose → track"""
        # Setup
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        engine = AutonomousGoalPursuitEngine(temp_db.name)
        
        try:
            # Step 1: Identify goals
            user_model = {
                'key_beliefs': [
                    {'belief': 'I can never keep up', 'is_limiting': True}
                ],
                'key_constraints': [],
                'key_motivations': [
                    {'motivation_type': 'competence', 'stated': True, 'is_active': False}
                ]
            }
            history = ['Always behind', 'Overwhelmed']
            
            goals = engine.identify_goals(user_model, history)
            self.assertGreater(len(goals), 0)
            
            goal = goals[0]
            
            # Step 2: Accept goal
            engine.accept_goal(goal.goal_id)
            active = engine.get_active_goals()
            self.assertTrue(any(g['goal_id'] == goal.goal_id for g in active))
            
            # Step 3: Update progress
            engine.update_progress(goal.goal_id, 0.25)
            report = engine.get_goal_report(goal.goal_id)
            self.assertEqual(report['progress'], 0.25)
            
        finally:
            if os.path.exists(temp_db.name):
                os.remove(temp_db.name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
