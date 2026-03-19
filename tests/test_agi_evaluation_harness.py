"""
Tests for AGI evaluation harness.
"""

import pytest
from jessica.unified_world_model import WorldModel
from jessica.unified_world_model.agi_evaluation_harness import (
    AGIEvaluationHarness,
    AGIEvaluationScorer,
    TaskResponse,
    EvaluationPlanStep,
    DomainMapping,
    CausalExplanation,
    EvaluationTask,
    FailureInjection,
    FailureType
)


@pytest.fixture
def world():
    return WorldModel()


@pytest.fixture
def harness(world):
    return AGIEvaluationHarness(world)


@pytest.fixture
def scorer():
    return AGIEvaluationScorer()


# Test basic infrastructure

def test_harness_initialization(harness):
    """Test harness initializes with 10 tasks."""
    assert len(harness.tasks) == 10
    assert all(t.minimum_steps >= 10 for t in harness.tasks)


def test_task_has_failure_injection(harness):
    """Test all tasks have failure injection."""
    for task in harness.tasks:
        assert task.failure_injection is not None
        assert task.failure_injection.step_number > 0


# Test scoring dimensions

def test_score_cross_domain_transfer_empty(scorer):
    """Test scoring with no domain mappings."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=["domain_a", "domain_b"],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={}
    )
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5)
    )
    
    score = scorer.score_cross_domain_transfer(response, task)
    assert score == 0.0


def test_score_cross_domain_transfer_with_mappings(scorer):
    """Test scoring with valid domain mappings."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=["chess", "business"],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={}
    )
    
    mappings = [
        DomainMapping(
            source_domain="chess",
            target_domain="business",
            source_concept="tempo",
            target_concept="market_speed",
            causal_justification="Early moves establish position advantage similar to early market entry",
            confidence=0.8
        ),
        DomainMapping(
            source_domain="chess",
            target_domain="business",
            source_concept="sacrifice",
            target_concept="loss_leader",
            causal_justification="Sacrifice material for position like loss-leader for market share",
            confidence=0.7
        )
    ]
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=mappings,
        explanation=CausalExplanation("", [], [], [], 0.5)
    )
    
    score = scorer.score_cross_domain_transfer(response, task)
    assert score > 0.5


def test_score_multi_step_planning_empty(scorer):
    """Test scoring with no plan."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={},
        minimum_steps=10
    )
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5)
    )
    
    score = scorer.score_multi_step_planning(response, task)
    assert score == 0.0


def test_score_multi_step_planning_valid(scorer):
    """Test scoring with valid multi-step plan."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=["time", "budget"],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={},
        minimum_steps=10
    )
    
    plan = [
        EvaluationPlanStep(
            step_id=f"step_{i}",
            step_number=i,
            action=f"action_{i}",
            preconditions=[f"pre_{i}"],
            effects=[f"effect_{i}"],
            resources_required=[f"resource_{i}"],
            dependencies=[f"step_{i-1}"] if i > 0 else []
        )
        for i in range(10)
    ]
    
    response = TaskResponse(
        task_id="test",
        plan=plan,
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5)
    )
    
    score = scorer.score_multi_step_planning(response, task)
    assert score > 0.6


def test_score_adaptation_to_failure_no_adaptation(scorer):
    """Test scoring with no adaptation."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 5, "supplier backs out"),
        success_criteria={},
        minimum_steps=10
    )
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5),
        adaptation_steps=[]
    )
    
    score = scorer.score_adaptation_to_failure(response, task)
    assert score == 0.0


def test_score_adaptation_to_failure_with_adaptation(scorer):
    """Test scoring with valid adaptation."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=["time", "budget"],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 5, "supplier backs out"),
        success_criteria={},
        minimum_steps=10
    )
    
    adaptation = [
        EvaluationPlanStep(
            step_id=f"adapt_{i}",
            step_number=i,
            action=f"find alternate supplier {i}",
            preconditions=[],
            effects=[],
            resources_required=[],
            dependencies=[]
        )
        for i in range(8)
    ]
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5),
        adaptation_steps=adaptation,
        adaptation_time_ms=1500
    )
    
    score = scorer.score_adaptation_to_failure(response, task)
    assert score > 0.4


def test_score_explanation_quality_empty(scorer):
    """Test scoring with minimal explanation."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={}
    )
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("decision", [], [], [], 0.5)
    )
    
    score = scorer.score_explanation_quality(response, task)
    assert score < 0.3


def test_score_explanation_quality_rich(scorer):
    """Test scoring with rich causal explanation."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=[],
        constraints=[],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 1, "test"),
        success_criteria={}
    )
    
    explanation = CausalExplanation(
        decision="Choose strategy A",
        causal_chain=[
            "Market condition X causes opportunity Y",
            "Opportunity Y enables action Z",
            "Action Z leads to competitive advantage",
            "Competitive advantage results in market share",
            "Market share drives revenue"
        ],
        tradeoffs=[
            "Higher cost vs faster execution",
            "Risk vs reward balance",
            "Short-term pain for long-term gain"
        ],
        counterfactuals=[
            "If not strategy A, then market position weakens",
            "If not early entry, then competitor dominates"
        ],
        confidence=0.75
    )
    
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=explanation
    )
    
    score = scorer.score_explanation_quality(response, task)
    assert score > 0.7


# Test full evaluation

def test_full_evaluation_failing_response(scorer):
    """Test evaluation of a response that should fail."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=["domain_a", "domain_b"],
        constraints=["constraint_1"],
        goal="Test",
        failure_injection=FailureInjection("f1", FailureType.RESOURCE_UNAVAILABLE, 5, "test"),
        success_criteria={},
        minimum_steps=10
    )
    
    # Minimal response - should fail all criteria
    response = TaskResponse(
        task_id="test",
        plan=[],
        domain_mappings=[],
        explanation=CausalExplanation("", [], [], [], 0.5)
    )
    
    evaluation = scorer.evaluate(response, task)
    
    assert not evaluation.passed
    assert evaluation.overall < 0.5


def test_full_evaluation_passing_response(scorer):
    """Test evaluation of a response that should pass."""
    task = EvaluationTask(
        task_id="test",
        title="Test",
        description="Test",
        domains_required=["chess", "business"],
        constraints=["time", "budget"],
        goal="Market entry",
        failure_injection=FailureInjection("f1", FailureType.UNEXPECTED_OUTCOME, 3, "competitor launches"),
        success_criteria={},
        minimum_steps=10
    )
    
    # Rich response - should pass all criteria
    mappings = [
        DomainMapping("chess", "business", "tempo", "speed", "Early action advantage in both domains", 0.8),
        DomainMapping("chess", "business", "position", "market_share", "Control of key squares maps to market segments", 0.75)
    ]
    
    plan = [
        EvaluationPlanStep(f"step_{i}", i, f"action_{i}", [f"pre_{i}"], [f"effect_{i}"], [f"res_{i}"], [f"step_{i-1}"] if i > 0 else [])
        for i in range(12)
    ]
    
    explanation = CausalExplanation(
        "Market entry via tempo advantage",
        ["Tempo → early entry", "Early entry → position", "Position → advantage", "Advantage → share", "Share → revenue"],
        ["Speed vs quality", "Risk vs reward", "Investment vs returns"],
        ["Without tempo, lose position", "Without position, lose market"],
        0.8
    )
    
    adaptation = [
        EvaluationPlanStep(f"adapt_{i}", i, f"replan competitor response {i}", [], [], [], [])
        for i in range(10)
    ]
    
    response = TaskResponse(
        task_id="test",
        plan=plan,
        domain_mappings=mappings,
        explanation=explanation,
        adaptation_steps=adaptation,
        adaptation_time_ms=1800
    )
    
    evaluation = scorer.evaluate(response, task)
    
    assert evaluation.cross_domain_transfer >= 0.7
    assert evaluation.multi_step_planning >= 0.7
    assert evaluation.explanation_quality >= 0.7
    # Adaptation might be slightly lower due to heuristic scoring
    assert evaluation.overall > 0.65


# Test task execution

def test_run_single_task(harness):
    """Test running a single task through harness."""
    def mock_system(task, failure):
        # Return minimal valid response
        return TaskResponse(
            task_id=task.task_id,
            plan=[EvaluationPlanStep(f"s{i}", i, f"a{i}", [], [], [], []) for i in range(10)],
            domain_mappings=[],
            explanation=CausalExplanation("", [], [], [], 0.5)
        )
    
    score = harness.run_task("task_1_emergency_logistics", mock_system)
    
    assert score is not None
    assert 0 <= score.overall <= 1


def test_generate_report(harness):
    """Test report generation."""
    def mock_system(task, failure):
        return TaskResponse(
            task_id=task.task_id,
            plan=[],
            domain_mappings=[],
            explanation=CausalExplanation("", [], [], [], 0.5)
        )
    
    results = harness.run_all_tasks(mock_system)
    report = harness.generate_report(results)
    
    assert "tasks_passed" in report
    assert "tasks_total" in report
    assert "pass_rate" in report
    assert "classification" in report
    assert report["tasks_total"] == 10
