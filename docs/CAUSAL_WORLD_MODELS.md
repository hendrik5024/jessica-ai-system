# Causal World Models

## Overview
Causal World Models enable Jessica to understand cause-effect relationships and simulate outcomes before giving advice. Instead of just "knowing facts," Jessica can now model "if sleep < 6h → focus ↓ → mistakes ↑" and similar causal chains.

## Quick Start

```python
from jessica.meta.causal_world_models import CausalWorldModels

# Initialize models
models = CausalWorldModels()

# Predict outcome
result = models.predict_outcome(
    "productivity",
    {"sleep_hours": 5},  # Intervention
    target_var="focus_level",
    steps=3
)
print(f"Predicted focus: {result['predicted_value']}")

# Plan intervention
plan = models.plan_intervention(
    "productivity",
    target_var="focus_level",
    target_value=8.0
)
print(f"Best intervention: {plan['intervention']}")
```

## Architecture

### Components
1. **CausalVariable**: Variables with ranges, units, current values
2. **CausalEdge**: Directed cause→effect relationships with strength
3. **CausalDomain**: Collection of variables and edges (a domain model)
4. **CausalWorldModels**: Multi-domain manager with prediction/planning

### Domains
Jessica has 5 pre-built domain models:

1. **Productivity** (6 variables, 7 edges)
   - sleep → focus → task completion
   - interruptions → focus ↓
   - errors → task completion ↓

2. **Emotions** (6 variables, 7 edges)
   - rest → mood, energy
   - stress → mood ↓
   - social connection → resilience

3. **Learning** (6 variables, 6 edges)
   - study time → understanding
   - review → retention
   - sleep → retention
   - understanding + retention → test scores

4. **Habits** (5 variables, 6 edges)
   - trigger → behavior repetitions
   - repetitions → habit strength
   - reward → habit strength
   - habit → less resistance

5. **Systems** (6 variables, 5 edges)
   - input quality → output quality
   - process efficiency → output quality
   - feedback loops → continuous improvement

## Key Features

### 1. Outcome Simulation
```python
# Simulate what happens if sleep increases
result = models.predict_outcome(
    "productivity",
    {"sleep_hours": 8},
    target_var="focus_level",
    steps=5
)

# Get trajectory
trajectory = result['trajectory']
focus_over_time = trajectory['focus_level']  # [5.0, 5.8, 6.4, 6.8, ...]
```

### 2. Intervention Planning
```python
# Find best way to improve mood
plan = models.plan_intervention(
    "emotions",
    target_var="mood",
    target_value=8.0,
    candidates=["rest_quality", "social_connection", "stress_level"]
)

print(plan['intervention'])  # e.g., {"rest_quality": 9.0}
print(plan['predicted_value'])  # e.g., 7.8
```

### 3. Feedback Loop Detection
```python
# Check for reinforcing/dampening loops
domain = models.domains["productivity"]
loops = domain.detect_feedback_loops()

for loop in loops:
    print(loop)  # ['focus_level', 'task_completion', 'focus_level']
```

### 4. Domain Analysis
```python
# Analyze domain structure
analysis = models.analyze_domain("productivity")

print(analysis['num_variables'])  # 6
print(analysis['num_edges'])  # 7
print(analysis['feedback_loops'])  # 2
print(analysis['most_influential'])  # sleep_hours
```

## Simulation Details

### Effect Propagation
Effects propagate through causal chains with:
- **Strength**: Edge weight (-1.0 to 1.0)
- **Delay**: Steps before effect activates
- **Nonlinearity**: Acceleration at extremes
- **Damping**: Systems return to equilibrium (30% per step)

### Example Chain
```
sleep_hours: 5 → 8 (+3)
    ↓ (strength 0.8, delay 0)
focus_level: 5 → 7.2 (+2.2)
    ↓ (strength 0.7, delay 0)
task_completion: 5 → 6.5 (+1.5)
```

## Integration with Agent

### In Advice Generation
```python
# In agent_loop.py or advice_skill.py
from jessica.meta.causal_world_models import CausalWorldModels

models = CausalWorldModels()

# User asks: "How can I improve my focus?"
plan = models.plan_intervention(
    "productivity",
    target_var="focus_level",
    target_value=8.0
)

# Response: "I'd recommend improving sleep_hours to 8 hours. 
# This would increase your focus from 5 to 7.8 over 3-5 time steps."
```

### In Planning Workflows
```python
# Multi-step planning
goal = "Improve test scores"

# Step 1: Find target variable
domain = models.domains["learning"]
target = "test_score"

# Step 2: Find optimal interventions
plan = models.plan_intervention("learning", target, 85.0)

# Step 3: Simulate outcome
result = models.predict_outcome(
    "learning",
    plan['intervention'],
    target,
    steps=10
)

# Response: "To reach 85% test score:
# 1. Increase study_time to 6 hours/day
# 2. Review material 5 times
# 3. Get 8 hours of sleep
# This should improve your score from 65% to 82% over 10 study sessions."
```

## Adding New Domains

```python
from jessica.meta.causal_world_models import CausalDomain, CausalVariable

# Create new domain
health = CausalDomain("health", "Physical and mental health")

# Add variables
health.add_variable(CausalVariable(
    "exercise_hours", "health",
    "Hours exercised per week", 0, 20, "hours", 2.0
))
health.add_variable(CausalVariable(
    "energy_level", "health",
    "Physical energy (0-10)", 0, 10, "score", 5.0
))

# Add edges
health.add_edge("exercise_hours", "energy_level", 0.6,
    "Exercise → more energy")

# Add to models
models.domains["health"] = health
models.save()
```

## Configuration

### Storage Location
Models persist to: `jessica_data_embeddings/causal_models_state.json`

### Simulation Parameters
```python
# Adjust simulation parameters
result = models.predict_outcome(
    "productivity",
    {"sleep_hours": 8},
    target_var="focus_level",
    steps=10  # More steps = longer simulation
)
```

### Edge Strength Guidelines
- **0.8-1.0**: Very strong effect (e.g., trigger → behavior)
- **0.5-0.7**: Moderate effect (e.g., sleep → focus)
- **0.2-0.4**: Weak effect (e.g., feedback loops)
- **Negative**: Inverse relationship (stress → mood ↓)

## Limitations

1. **Simplified Models**: Real causality is more complex
2. **Linear Approximations**: Most effects are actually nonlinear
3. **No Uncertainty**: No probabilistic reasoning yet
4. **No Constraints**: No resource/time constraints yet
5. **Single-Domain**: Cross-domain interactions not modeled

## Future Enhancements

1. **Uncertainty Quantification**: Confidence intervals on predictions
2. **Constraint Satisfaction**: Resource/time/budget constraints
3. **Cross-Domain Models**: Sleep affects both productivity AND emotions
4. **Learning from Feedback**: Update strengths based on user outcomes
5. **Multi-Goal Planning**: Optimize for multiple objectives

## Testing

Run comprehensive test suite:
```bash
pytest test_causal_world_models.py -v
```

23 tests covering:
- Variable creation and serialization
- Edge relationships
- Domain construction
- Simulation accuracy
- Prediction quality
- Planning algorithms
- Feedback loop detection
- Persistence

## References

- Identity Anchors: Temporal consistency layer
- Meta-Cognition Stack: 7-layer self-awareness system
- Knowledge Stores: 17 domain-specific knowledge bases
