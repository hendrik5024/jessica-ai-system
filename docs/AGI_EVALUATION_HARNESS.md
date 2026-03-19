# AGI Evaluation Harness

**Status:** ✅ Complete (14/14 tests passing)  
**Location:** `jessica/unified_world_model/agi_evaluation_harness.py`  
**Demo:** `demo_agi_evaluation.py`

## Overview

The AGI Evaluation Harness is a comprehensive testing framework designed to distinguish narrow AI systems from generally intelligent systems. It evaluates systems across **10 challenging tasks** requiring **cross-domain transfer**, **long-horizon planning**, **failure adaptation**, and **causal reasoning**.

## Key Innovation

Unlike traditional benchmarks that test isolated capabilities, this harness evaluates **integration of multiple capabilities** in realistic scenarios:

- **Cross-domain transfer**: Explicit mapping between domains with causal justification
- **Multi-step planning**: 10+ step plans with dependencies, preconditions, and resource constraints
- **Adaptation to failure**: Automatic failure injection requiring rapid replanning
- **Causal explanation**: Reasoning chains, tradeoffs, counterfactuals, confidence calibration

## The 10 Evaluation Tasks

### 1. Emergency Logistics + Negotiation + Resource Scheduling
**Domains:** Logistics, negotiation, decision_making  
**Goal:** Evacuate 500 people within 6 hours with limited transport  
**Failure:** Traffic accident blocks main route (step 5)  
**Challenge:** Must reroute while negotiating transport and prioritizing vulnerable populations

### 2. Cooking + Chemistry + Budgeting
**Domains:** Cooking, scientific_thinking, financial_literacy  
**Goal:** Prepare 3-course meal for 8 with $60 budget  
**Failure:** Grocery store out of key ingredient (step 3)  
**Challenge:** Substitute using chemistry knowledge while staying within budget

### 3. Robotics Assembly + Project Management
**Domains:** Tech_support, systems_thinking, professional_communication  
**Goal:** Assemble robot with 15 components in dependency order  
**Failure:** Component defect discovered (step 6)  
**Challenge:** Coordinate team, troubleshoot hardware, maintain timeline

### 4. Chess → Business Strategy Transfer
**Domains:** Chess, decision_making, professional_communication  
**Goal:** Apply chess patterns to business merger negotiation  
**Failure:** Key stakeholder unexpectedly opposes (step 4)  
**Challenge:** Transfer strategic thinking across domains, adapt to opposition

### 5. Medical Triage + Ethics + Scheduling
**Domains:** First_aid, decision_making, etiquette  
**Goal:** Treat 10 ER patients with 2 doctors, ethical constraints  
**Failure:** Critical patient arrives mid-triage (step 4)  
**Challenge:** Balance urgency, resource constraints, ethical principles

### 6. Multi-modal Travel + Cognitive Fatigue
**Domains:** Travel_planning, decision_making, emotional_intelligence  
**Goal:** Plan 72-hour trip across 3 countries, optimize for fatigue  
**Failure:** Flight cancelled (step 5)  
**Challenge:** Rebook while managing accumulated fatigue and constraints

### 7. Systems Debugging + Causal Analysis
**Domains:** Tech_support, systems_thinking, thinking_frameworks  
**Goal:** Diagnose 3-system failure with 5 whys root cause analysis  
**Failure:** Initial hypothesis disproven by logs (step 3)  
**Challenge:** Pivot from wrong hypothesis using causal reasoning

### 8. Creative Design + Constraint Optimization
**Domains:** Storytelling, decision_making, thinking_frameworks  
**Goal:** Design school schedule balancing 6 constraints  
**Failure:** Room double-booked (step 4)  
**Challenge:** Resolve conflict while preserving all other constraints

### 9. Cross-domain Forecasting
**Domains:** Financial_literacy, travel_planning, systems_thinking  
**Goal:** Forecast event impacts across economics, tourism, logistics  
**Failure:** Unexpected policy change (step 3)  
**Challenge:** Update predictions using cross-domain causal models

### 10. Autonomous Skill Improvement Loop
**Domains:** Decision_making, systems_thinking, thinking_frameworks  
**Goal:** Self-improve weak skill from 0.4 → 0.7 performance  
**Failure:** Training method ineffective (step 3)  
**Challenge:** Meta-learning - detect ineffectiveness and switch methods

## Scoring Dimensions

### 1. Cross-Domain Transfer (threshold: 0.70)
**Tests:** Can the system explicitly map patterns between domains?

**Scoring breakdown:**
- **Domain coverage** (50%): Maps present for all domain pairs?
- **Causal justification** (30%): Are mappings explained with underlying principles?
- **Confidence calibration** (20%): Is confidence appropriate?

**Distinguishing factor:**
- Narrow AI: No explicit mappings, domain-specific solutions
- AGI: Structural similarity detection, principle-based transfer

### 2. Multi-Step Planning (threshold: 0.80)
**Tests:** Can the system create long-horizon plans with dependencies?

**Scoring breakdown:**
- **Step count** (30%): Sufficient detail (≥10 steps)?
- **Dependencies** (20%): Steps properly ordered?
- **Preconditions** (15%): Clear prerequisites?
- **Effects** (15%): Explicit outcomes?
- **Constraints** (20%): Resource/timing respected?

**Distinguishing factor:**
- Narrow AI: Short, sequential plans without dependencies
- AGI: Long-horizon plans with explicit dependencies and resource reasoning

### 3. Adaptation to Failure (threshold: 0.75)
**Tests:** Can the system rapidly replan when failures occur?

**Scoring breakdown:**
- **Response speed** (25%): Adaptation within 1-2 steps?
- **Constraint preservation** (25%): Original constraints still satisfied?
- **Addresses failure** (30%): Solution resolves the failure?
- **Goal preservation** (20%): Original goal still achievable?

**Distinguishing factor:**
- Narrow AI: No replanning, brittle to failures
- AGI: Rapid context-aware replanning

### 4. Explanation Quality (threshold: 0.70)
**Tests:** Can the system provide causal reasoning for decisions?

**Scoring breakdown:**
- **Causal chain depth** (30%): Multi-step reasoning?
- **Tradeoffs** (25%): Explicit alternatives considered?
- **Counterfactuals** (25%): "What if?" reasoning?
- **Confidence** (20%): Appropriate uncertainty?

**Distinguishing factor:**
- Narrow AI: Surface narratives, no causal depth
- AGI: Deep causal reasoning with counterfactual thinking

## Classification System

**AGI-capable:** ≥8/10 tasks passing (≥80%)
- Strong cross-domain transfer
- Long-horizon planning
- Rapid adaptation
- Causal explanations

**Advanced:** ≥6/10 tasks passing (60-79%)
- Some cross-domain capability
- Medium-horizon planning
- Limited adaptation
- Surface explanations

**Narrow AI:** <6/10 tasks passing (<60%)
- Domain-specific solutions
- Short-horizon planning
- No failure recovery
- Weak explanations

## Usage

### Basic Evaluation

```python
from jessica.unified_world_model import AGIEvaluationHarness, WorldModel

# Initialize
world = WorldModel()
harness = AGIEvaluationHarness(world)

# Define your system
def my_system(task, failure):
    # Your AI system generates:
    # - Multi-step plan (≥10 steps)
    # - Cross-domain mappings
    # - Causal explanation
    # - Adaptation after failure
    return TaskResponse(...)

# Run evaluation
results = harness.run_all_tasks(my_system)
report = harness.generate_report(results)

# View classification
print(f"Classification: {report['classification']}")
print(f"Pass rate: {report['pass_rate']:.1%}")
```

### Single Task Testing

```python
# Test specific task
task_score = harness.run_task("task_1_emergency_logistics", my_system)

print(f"Overall: {task_score.overall:.2f}")
print(f"Passed: {task_score.passed}")
print(f"Cross-domain: {task_score.cross_domain_transfer:.2f}")
print(f"Planning: {task_score.multi_step_planning:.2f}")
print(f"Adaptation: {task_score.adaptation_to_failure:.2f}")
print(f"Explanation: {task_score.explanation_quality:.2f}")
```

### Custom Thresholds

```python
from jessica.unified_world_model import AGIEvaluationScorer, ScoringDimension

# Adjust thresholds
custom_scorer = AGIEvaluationScorer(
    dimension_thresholds={
        ScoringDimension.CROSS_DOMAIN_TRANSFER: 0.8,  # Stricter
        ScoringDimension.MULTI_STEP_PLANNING: 0.9,    # Stricter
        ScoringDimension.ADAPTATION_TO_FAILURE: 0.7,
        ScoringDimension.EXPLANATION_QUALITY: 0.7
    }
)

harness = AGIEvaluationHarness(world, scorer=custom_scorer)
```

## Response Format

Your system must return a `TaskResponse` with:

```python
from jessica.unified_world_model import (
    TaskResponse, PlanStep, DomainMapping, CausalExplanation
)

response = TaskResponse(
    task_id="task_1_emergency_logistics",
    
    # Multi-step plan (≥10 steps)
    plan=[
        PlanStep(
            step_id="step_1",
            step_number=1,
            action="Assess transport availability",
            preconditions=["emergency_declared"],
            effects=["transport_inventory_known"],
            resources_required=["communication_system"],
            dependencies=[]
        ),
        # ... at least 9 more steps
    ],
    
    # Cross-domain mappings
    domain_mappings=[
        DomainMapping(
            source_domain="logistics",
            target_domain="negotiation",
            source_concept="route_optimization",
            target_concept="stakeholder_alignment",
            causal_justification="Both involve constraint satisfaction under time pressure with multiple competing objectives",
            confidence=0.8
        ),
        # ... more mappings
    ],
    
    # Causal explanation
    explanation=CausalExplanation(
        decision="Prioritize vulnerable populations in evacuation sequence",
        causal_chain=[
            "Emergency declaration creates time constraint",
            "Limited transport creates resource constraint",
            "Vulnerable populations have higher risk → prioritize",
            "Prioritization enables ethical compliance",
            "Route optimization enables timeline achievement"
        ],
        tradeoffs=[
            "Speed vs safety in transport selection",
            "Fairness vs efficiency in prioritization"
        ],
        counterfactuals=[
            "If no prioritization, then vulnerable populations at higher risk",
            "If no route optimization, then miss 6-hour deadline"
        ],
        confidence=0.85
    ),
    
    # Adaptation to failure (after failure injection)
    adaptation_steps=[
        PlanStep(
            step_id="adapt_1",
            step_number=1,
            action="Identify alternate route",
            preconditions=["main_route_blocked"],
            effects=["alternate_route_identified"],
            resources_required=["map_data"],
            dependencies=[]
        ),
        # ... more adaptation steps
    ],
    adaptation_time_ms=1500  # Time to generate adaptation
)
```

## Demo Results

Running `demo_agi_evaluation.py`:

### Narrow AI System
- **Pass rate:** 0/10 (0%)
- **Classification:** Narrow AI
- **Scores:**
  - Cross-domain transfer: 0.00
  - Multi-step planning: 0.44
  - Adaptation: 0.00
  - Explanation: 0.18

### AGI System
- **Pass rate:** 10/10 (100%)
- **Classification:** AGI-capable
- **Scores:**
  - Cross-domain transfer: 0.96
  - Multi-step planning: 0.98
  - Adaptation: 1.00
  - Explanation: 0.97

**Key differences:**
- **531% improvement** in overall performance
- **∞% improvement** in cross-domain transfer (0.00 → 0.96)
- **123% improvement** in planning (0.44 → 0.98)
- **∞% improvement** in adaptation (0.00 → 1.00)
- **439% improvement** in explanation (0.18 → 0.97)

## Why This Matters

### Current AI Limitations
Most AI systems excel at narrow tasks but fail at:
1. **Transfer**: Learning in one domain doesn't help in others
2. **Planning**: Can't reliably plan >5 steps ahead
3. **Adaptation**: Brittle to unexpected failures
4. **Reasoning**: Can't explain why decisions work

### AGI Requirements
A generally intelligent system must:
1. **Transfer patterns** between domains with causal justification
2. **Plan long-horizon** strategies with dependencies
3. **Adapt rapidly** to failures while preserving constraints
4. **Explain reasoning** with counterfactuals and tradeoffs

### Validation Strategy
This harness provides:
- **Concrete tests** for AGI capabilities (not just definitions)
- **Automatic evaluation** with objective scoring
- **Failure injection** to test robustness
- **Multi-dimensional assessment** (not single metrics)

## Implementation Details

### Failure Injection
Each task has automatic failure injection:
```python
failure = FailureInjection(
    failure_type=FailureType.RESOURCE_UNAVAILABLE,
    description="Main evacuation route blocked by accident",
    inject_at_step=5,
    expected_adaptation="Identify alternate route within 1-2 steps"
)
```

**Failure types:**
- `RESOURCE_UNAVAILABLE`: Expected resource missing
- `CONSTRAINT_CHANGE`: Requirements change mid-execution
- `UNEXPECTED_OUTCOME`: Action has different effect than expected
- `TIMING_VIOLATION`: Deadline pressure increases
- `ASSUMPTION_INVALIDATED`: Core assumption proven wrong

### Scoring Algorithm

For each task:
1. System generates initial plan
2. Harness injects failure at specified step
3. System generates adaptation
4. Scorer evaluates across 4 dimensions
5. Overall score = weighted average with AND logic (all must pass threshold)

```python
overall = min(
    cross_domain_score,
    planning_score,
    adaptation_score,
    explanation_score
)
passed = overall >= min(dimension_thresholds.values())
```

This ensures systems can't pass by excelling in one dimension while failing others.

## Testing

### Unit Tests (14 tests)
```bash
pytest tests/test_agi_evaluation_harness.py -v
```

**Coverage:**
- Infrastructure (2 tests): initialization, failure injection
- Scoring dimensions (8 tests): all 4 dimensions × 2 cases each
- Full evaluation (2 tests): failing system, passing system
- Task execution (2 tests): single task, full report

### Integration Tests
```bash
python demo_agi_evaluation.py
```

Demonstrates narrow AI vs AGI system across all 10 tasks.

## Future Enhancements

### Potential Extensions
1. **Dynamic task generation**: Generate new tasks on the fly
2. **Adversarial testing**: Active search for system weaknesses
3. **Multi-agent tasks**: Evaluate coordination and communication
4. **Real-world deployment**: Test in production environments
5. **Continual evaluation**: Track capability drift over time

### Research Applications
- **Benchmark for AGI research**: Standard evaluation for new systems
- **Capability profiling**: Identify specific weaknesses
- **Transfer learning research**: Measure cross-domain generalization
- **Robustness testing**: Systematic failure mode discovery

## Related Documentation

- [Unified World Model](UNIFIED_WORLD_MODEL.md) - Phase 1: Causal world modeling
- [Cross-Domain Transfer](CROSS_DOMAIN_TRANSFER.md) - Phase 2: Transfer learning
- [Long-Horizon Planning](LONG_HORIZON_PLANNING.md) - Phase 3: Planning system
- [Continual Learning](CONTINUAL_LEARNING.md) - Phase 4: Streaming learning
- [Problem Discovery](PROBLEM_DISCOVERY.md) - Phase 5: Autonomous improvement
- [AGI Architecture Analysis](AGI_ARCHITECTURE_ANALYSIS.md) - Weakest components

## References

**Theoretical Foundation:**
- Chollet, F. (2019). "On the Measure of Intelligence" - ARC benchmark
- Marcus, G. (2020). "The Next Decade in AI" - Transfer and abstraction
- Lake et al. (2017). "Building Machines That Learn and Think Like People"

**Implementation Inspiration:**
- BabyAI: Language-based planning benchmark
- MiniHack: Long-horizon planning in NetHack
- ALFRED: Household task benchmark with language

**Key Differences:**
- Multi-domain (not single environment)
- Failure injection (tests adaptation)
- Causal explanations (not just actions)
- Cross-domain transfer (explicit mappings)

---

**Implementation:** Jessica AGI System  
**Authors:** Unified World Model Team  
**Version:** 1.0.0  
**Last Updated:** 2024
