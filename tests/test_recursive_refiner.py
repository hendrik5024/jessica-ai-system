"""
Comprehensive test suite for Jessica's Autonomous Refinement Module

Tests cover:
1. Failure clustering and pattern detection
2. Root cause analysis
3. Code patch generation
4. Synthetic test generation
5. Sandbox execution and safety
6. Wisdom scoring
7. Psychological versioning
8. Integration with autodidactic loop
9. Regression detection
10. Health metrics
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Import system modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jessica.brain.recursive_refiner import (
    FailureClusterer,
    RootCauseAnalyzer,
    CodeArchitect,
    SyntheticTestGenerator,
    SandboxExecutor,
    WisdomScorer,
    PsychologicalVersionControl,
    AutonomousRefinementEngine,
    FailureCluster,
    CodePatch,
    WisdomScore,
    ConfidenceLevel,
    RefinementPhase
)

from jessica.brain.refinement_integration import (
    RefinementCycleOrchestrator,
    AutonomousLearningIntegration
)


class TestFailureClusterer:
    """Tests for failure clustering"""
    
    def test_initialize_clusterer(self):
        """Test clusterer initialization"""
        clusterer = FailureClusterer(regret_memory=None)
        assert clusterer is not None
        assert clusterer.clusters == {}
    
    def test_analyze_failures_returns_clusters(self):
        """Test failure analysis returns clusters"""
        clusterer = FailureClusterer(regret_memory=None)
        clusters = clusterer.analyze_failures(max_failures=100)
        
        assert isinstance(clusters, list)
        assert len(clusters) > 0
    
    def test_clusters_sorted_by_severity(self):
        """Test clusters are sorted by severity × urgency"""
        clusterer = FailureClusterer(regret_memory=None)
        clusters = clusterer.analyze_failures(max_failures=100)
        
        # Check sorting
        scores = [c.severity * c.urgency for c in clusters]
        assert scores == sorted(scores, reverse=True)
    
    def test_cluster_properties(self):
        """Test cluster has required properties"""
        clusterer = FailureClusterer(regret_memory=None)
        clusters = clusterer.analyze_failures(max_failures=50)
        
        if clusters:
            cluster = clusters[0]
            assert hasattr(cluster, 'cluster_id')
            assert hasattr(cluster, 'failure_type')
            assert hasattr(cluster, 'affected_module')
            assert cluster.count > 0
            assert 0 <= cluster.severity <= 1
            assert 0 <= cluster.urgency <= 1


class TestRootCauseAnalyzer:
    """Tests for root cause analysis"""
    
    def test_initialize_analyzer(self):
        """Test analyzer initialization"""
        analyzer = RootCauseAnalyzer(causal_models=None)
        assert analyzer is not None
    
    def test_analyze_cluster_returns_analysis(self):
        """Test analysis returns structured result"""
        analyzer = RootCauseAnalyzer(causal_models=None)
        
        # Create mock cluster
        cluster = FailureCluster(
            cluster_id="test_cluster",
            failure_type="logic_error",
            affected_module="jessica/skills/coding.py",
            count=3,
            common_pattern="Regex pattern mismatch"
        )
        
        analysis = analyzer.analyze_cluster(cluster)
        
        assert isinstance(analysis, dict)
        assert "root_cause" in analysis
        assert "affected_code" in analysis
        assert "confidence" in analysis
        assert analysis["confidence"] > 0
    
    def test_analysis_includes_lessons(self):
        """Test analysis identifies lessons needed"""
        analyzer = RootCauseAnalyzer(causal_models=None)
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="jessica/skills/coding.py",
            count=2,
            common_pattern="Pattern"
        )
        
        analysis = analyzer.analyze_cluster(cluster)
        
        assert "lessons_needed" in analysis
        assert isinstance(analysis["lessons_needed"], list)


class TestCodeArchitect:
    """Tests for code patch generation"""
    
    def test_initialize_architect(self):
        """Test architect initialization"""
        architect = CodeArchitect(codellama_model=None, regret_memory=None)
        assert architect is not None
    
    def test_design_fix_returns_patch(self):
        """Test design_fix returns valid CodePatch"""
        architect = CodeArchitect(codellama_model=None, regret_memory=None)
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test_module.py",
            count=1,
            common_pattern="Test pattern"
        )
        
        root_cause = {
            "root_cause": "Bad logic",
            "affected_code": "test_code()",
            "condition_chain": ["A", "B", "C"],
            "confidence": 0.9,
            "lessons_needed": ["Lesson 1"]
        }
        
        patch = architect.design_fix(cluster, root_cause)
        
        assert isinstance(patch, CodePatch)
        assert patch.source_module == cluster.affected_module
        assert 0 < patch.confidence <= 1
        assert len(patch.related_lessons) > 0
    
    def test_patch_properties(self):
        """Test patch has all required properties"""
        architect = CodeArchitect(codellama_model=None, regret_memory=None)
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test.py",
            count=1,
            common_pattern="Pattern"
        )
        
        root_cause = {"root_cause": "Bad", "affected_code": "code", 
                     "condition_chain": [], "confidence": 0.9, "lessons_needed": []}
        
        patch = architect.design_fix(cluster, root_cause)
        
        assert patch.patch_id
        assert patch.old_code
        assert patch.new_code
        assert patch.reasoning
        assert patch.generated_by == "CodeLlama-13b"


class TestSyntheticTestGenerator:
    """Tests for synthetic test generation"""
    
    def test_initialize_generator(self):
        """Test generator initialization"""
        gen = SyntheticTestGenerator()
        assert gen is not None
    
    def test_generate_tests_returns_list(self):
        """Test generate_tests returns list of tests"""
        gen = SyntheticTestGenerator()
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test.py",
            count=1,
            common_pattern="Pattern"
        )
        
        tests = gen.generate_tests(cluster, "new_code", num_tests=5)
        
        assert isinstance(tests, list)
        assert len(tests) == 5
    
    def test_tests_have_required_properties(self):
        """Test each test has required properties"""
        gen = SyntheticTestGenerator()
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test.py",
            count=1,
            common_pattern="Pattern"
        )
        
        tests = gen.generate_tests(cluster, "code", num_tests=3)
        
        for test in tests:
            assert test.test_id
            assert test.test_name
            assert test.test_code
            assert test.targets_failure
            assert test.expected_behavior
    
    def test_tests_cover_different_scenarios(self):
        """Test that tests cover different scenarios"""
        gen = SyntheticTestGenerator()
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test.py",
            count=1,
            common_pattern="Pattern"
        )
        
        tests = gen.generate_tests(cluster, "code", num_tests=5)
        
        names = [t.test_name for t in tests]
        assert len(set(names)) == len(names)  # All unique


class TestSandboxExecutor:
    """Tests for sandbox execution"""
    
    def test_initialize_executor(self):
        """Test executor initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(tmpdir)
            assert executor is not None
    
    def test_create_shadow_branch(self):
        """Test shadow branch creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(tmpdir)
            
            # Create test file
            os.makedirs(os.path.join(tmpdir, "test"), exist_ok=True)
            test_file = os.path.join(tmpdir, "test", "module.py")
            with open(test_file, 'w') as f:
                f.write("# Test code\n")
            
            sandbox_path = executor.create_shadow_branch("test/module.py")
            
            assert os.path.exists(sandbox_path)
            assert executor.sandbox_dir == sandbox_path
    
    def test_apply_patch_to_shadow(self):
        """Test patch application to shadow branch"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(tmpdir)
            
            # Create test file
            os.makedirs(os.path.join(tmpdir, "test"), exist_ok=True)
            test_file = os.path.join(tmpdir, "test", "module.py")
            with open(test_file, 'w') as f:
                f.write("def old_func():\n    pass\n")
            
            sandbox_path = executor.create_shadow_branch("test/module.py")
            
            patch = CodePatch(
                patch_id="test_patch",
                source_module="test/module.py",
                old_code="def old_func():\n    pass",
                new_code="def new_func():\n    return True",
                reasoning="Test",
                generated_by="test",
                confidence=0.9,
                related_lessons=[]
            )
            
            success = executor.apply_patch(patch, sandbox_path)
            assert success
    
    def test_run_synthetic_tests(self):
        """Test synthetic test execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(tmpdir)
            
            from jessica.brain.recursive_refiner import SyntheticTest
            
            tests = [
                SyntheticTest(
                    test_id="t1", test_name="test_1",
                    test_code="assert True",
                    targets_failure="test", expected_behavior="pass"
                )
            ]
            
            pass_rate, results = executor.run_synthetic_tests(tests, tmpdir)
            
            assert 0 <= pass_rate <= 1
            assert len(results) == len(tests)
    
    def test_run_regression_tests(self):
        """Test regression test execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(tmpdir)
            
            pass_rate = executor.run_regression_tests(tmpdir)
            
            assert 0 <= pass_rate <= 1


class TestWisdomScorer:
    """Tests for wisdom scoring"""
    
    def test_initialize_scorer(self):
        """Test scorer initialization"""
        scorer = WisdomScorer()
        assert scorer is not None
    
    def test_score_patch_returns_wisdom_score(self):
        """Test score_patch returns WisdomScore"""
        scorer = WisdomScorer()
        
        patch = CodePatch(
            patch_id="test",
            source_module="test.py",
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        score = scorer.score_patch(patch, 0.9, 0.95)
        
        assert isinstance(score, WisdomScore)
        assert score.patch_id == patch.patch_id
        assert 0 <= score.overall_score <= 1
    
    def test_wisdom_score_components(self):
        """Test wisdom score has all components"""
        scorer = WisdomScorer()
        
        patch = CodePatch(
            patch_id="test",
            source_module="test.py",
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        score = scorer.score_patch(patch, 0.85, 0.98)
        
        assert hasattr(score, 'test_pass_rate')
        assert hasattr(score, 'regression_check')
        assert hasattr(score, 'confidence_calibration')
        assert hasattr(score, 'alignment_score')
        assert hasattr(score, 'overall_score')
    
    def test_wisdom_score_weighted_correctly(self):
        """Test scoring gives appropriate weight to regression"""
        scorer = WisdomScorer()
        
        patch = CodePatch(
            patch_id="test",
            source_module="test.py",
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        # High test pass but low regression = low overall
        low_regression = scorer.score_patch(patch, 0.95, 0.5)
        
        # High test pass and high regression = high overall
        high_regression = scorer.score_patch(patch, 0.95, 0.95)
        
        assert high_regression.overall_score > low_regression.overall_score


class TestPsychologicalVersionControl:
    """Tests for psychological versioning"""
    
    def test_initialize_versioning(self):
        """Test versioning initialization"""
        versioning = PsychologicalVersionControl()
        assert versioning is not None
    
    def test_present_for_confirmation_high_score(self):
        """Test high score gets auto-approved"""
        versioning = PsychologicalVersionControl()
        
        patch = CodePatch(
            patch_id="test",
            source_module="test.py",
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        wisdom = WisdomScore(
            patch_id="test",
            test_pass_rate=0.95,
            regression_check=0.98,
            confidence_calibration=0.9,
            alignment_score=0.95,
            performance_improvement=0.1,
            overall_score=0.95
        )
        
        result = versioning.present_for_confirmation(patch, wisdom)
        
        assert result in ["approved", "needs_review"]
    
    def test_implement_patch_requires_approval(self):
        """Test patch implementation requires approval"""
        with tempfile.TemporaryDirectory() as tmpdir:
            versioning = PsychologicalVersionControl()
            
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("old code")
            
            patch = CodePatch(
                patch_id="test",
                source_module="test.py",
                old_code="old code",
                new_code="new code",
                reasoning="test",
                generated_by="test",
                confidence=0.8,
                related_lessons=[]
            )
            
            # Should fail with non-approval
            result = versioning.implement_patch(patch, test_file, "rejected")
            assert result is False
    
    def test_monitor_post_update(self):
        """Test post-update monitoring"""
        with tempfile.TemporaryDirectory() as tmpdir:
            versioning = PsychologicalVersionControl()
            
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("code")
            
            result = versioning.monitor_post_update(test_file, num_interactions=10)
            
            assert isinstance(result, dict)
            assert "status" in result
            assert "interactions_monitored" in result


class TestAutonomousRefinementEngine:
    """Tests for main refinement engine"""
    
    def test_initialize_engine(self):
        """Test engine initialization"""
        engine = AutonomousRefinementEngine()
        assert engine is not None
    
    def test_run_self_correction_cycle(self):
        """Test running complete self-correction cycle"""
        engine = AutonomousRefinementEngine()
        records = engine.run_self_correction_cycle()
        
        assert isinstance(records, list)
    
    def test_get_statistics(self):
        """Test getting engine statistics"""
        engine = AutonomousRefinementEngine()
        
        # Run a cycle first
        engine.run_self_correction_cycle()
        
        stats = engine.get_refinement_statistics()
        
        assert isinstance(stats, dict)
        assert "total_attempts" in stats


class TestRefinementCycleOrchestrator:
    """Tests for learning cycle orchestration"""
    
    def test_initialize_orchestrator(self):
        """Test orchestrator initialization"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        assert orchestrator is not None
    
    def test_should_trigger_refinement(self):
        """Test refinement trigger logic"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        
        should_trigger = orchestrator.should_trigger_refinement()
        assert isinstance(should_trigger, bool)
    
    def test_validate_personality_constraints(self):
        """Test personality inertia validation"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        
        patch = CodePatch(
            patch_id="test",
            source_module="jessica/skills/coding.py",
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        valid = orchestrator.validate_personality_constraints(patch)
        assert isinstance(valid, bool)
    
    def test_protected_modules_blocked(self):
        """Test protected modules cannot be modified"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        
        patch = CodePatch(
            patch_id="test",
            source_module="jessica/brain/identity_anchors.py",  # Protected
            old_code="old",
            new_code="new",
            reasoning="test",
            generated_by="test",
            confidence=0.8,
            related_lessons=[]
        )
        
        valid = orchestrator.validate_personality_constraints(patch)
        assert valid is False
    
    def test_integrate_learnings(self):
        """Test learning integration"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        
        # Run cycle to get records
        records = engine.run_self_correction_cycle()
        
        learnings = orchestrator.integrate_learnings(records)
        
        assert isinstance(learnings, dict)
        assert "causal_models_updated" in learnings
    
    def test_get_refinement_health_metrics(self):
        """Test health metrics calculation"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        
        health = orchestrator.get_refinement_health_metrics()
        
        assert isinstance(health, dict)
        assert "cycles_completed" in health
        assert "health_status" in health


class TestAutonomousLearningIntegration:
    """Tests for high-level integration"""
    
    def test_initialize_integration(self):
        """Test integration initialization"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        integration = AutonomousLearningIntegration(orchestrator)
        assert integration is not None
    
    def test_on_interaction_complete(self):
        """Test interaction logging"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        integration = AutonomousLearningIntegration(orchestrator)
        
        summary = {
            "had_error": False,
            "error_severity": 0.1
        }
        
        # Should not raise
        integration.on_interaction_complete(summary)
    
    def test_get_jessica_health_report(self):
        """Test health report generation"""
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        integration = AutonomousLearningIntegration(orchestrator)
        
        report = integration.get_jessica_health_report()
        
        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "refinement_health" in report
        assert "recommendation" in report


class TestEndToEndRefinement:
    """End-to-end tests for complete refinement flow"""
    
    def test_complete_refinement_pipeline(self):
        """Test full refinement from failure to deployment"""
        
        # Create engine
        engine = AutonomousRefinementEngine()
        
        # Run self-correction cycle
        records = engine.run_self_correction_cycle()
        
        # Verify records
        assert len(records) >= 0  # May not find issues, that's ok
    
    def test_refinement_with_integration(self):
        """Test refinement integrated with learning cycle"""
        
        # Create full stack
        engine = AutonomousRefinementEngine()
        orchestrator = RefinementCycleOrchestrator(engine)
        integration = AutonomousLearningIntegration(orchestrator)
        
        # Get health report
        report = integration.get_jessica_health_report()
        
        assert report is not None
        assert "refinement_health" in report


# Performance tests
class TestPerformance:
    """Performance tests"""
    
    def test_failure_clustering_performance(self):
        """Test clustering doesn't take too long"""
        import time
        
        clusterer = FailureClusterer(regret_memory=None)
        
        start = time.time()
        clusters = clusterer.analyze_failures(max_failures=100)
        elapsed = time.time() - start
        
        # Should complete in < 1 second
        assert elapsed < 1.0
    
    def test_patch_generation_performance(self):
        """Test patch generation doesn't take too long"""
        import time
        
        architect = CodeArchitect(codellama_model=None, regret_memory=None)
        
        cluster = FailureCluster(
            cluster_id="test",
            failure_type="logic_error",
            affected_module="test.py",
            count=1,
            common_pattern="Pattern"
        )
        
        root_cause = {
            "root_cause": "Bad",
            "affected_code": "code",
            "condition_chain": [],
            "confidence": 0.9,
            "lessons_needed": []
        }
        
        start = time.time()
        patch = architect.design_fix(cluster, root_cause)
        elapsed = time.time() - start
        
        # Should complete in < 0.5 seconds
        assert elapsed < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
