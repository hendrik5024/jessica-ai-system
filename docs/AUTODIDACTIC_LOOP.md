# Autodidactic Loop - Self-Directed Curriculum

## Overview
The Autodidactic Loop is Jessica's self-directed learning system where she becomes her own teacher. She autonomously:
1. Reviews failure clusters
2. Identifies weakest skills
3. Generates synthetic training data
4. Prepares for fine-tuning
5. Validates improvements
6. Repeats weekly

**This is rare. And powerful.**

## Architecture

### Components

1. **FailureTracker** (`jessica/meta/failure_tracker.py`)
   - Logs all interactions (failures + successes)
   - Clusters failures by skill
   - Identifies weakest skills
   - Analyzes failure patterns
   - Prioritizes improvements

2. **SyntheticDataGenerator** (`jessica/meta/synthetic_data_generator.py`)
   - Generates training data for weak skills
   - Uses skill-specific templates
   - Creates prompt-completion pairs
   - Exports to JSONL format
   - Augments with variations

3. **AutodidacticLoop** (`jessica/meta/autodidactic_loop.py`)
   - Orchestrates weekly learning cycles
   - Manages cycle state
   - Tracks improvements
   - Generates reports
   - Schedules automatic runs

## Quick Start

### Basic Usage

```python
from jessica.meta.autodidactic_loop import AutodidacticLoop

# Run a learning cycle
loop = AutodidacticLoop()
cycle = loop.run_learning_cycle()

# After fine-tuning, mark complete
loop.mark_cycle_complete(
    cycle.cycle_id,
    improvement_metrics={
        "success_rate": 0.85,
        "avg_severity": 4.0,
        "failure_count": 3
    }
)
```

### Logging Failures

```python
from jessica.meta.failure_tracker import FailureTracker

tracker = FailureTracker()

# Log a failure
tracker.log_failure(
    skill="programming",
    category="syntax_error",
    description="Missing colon in function definition",
    context={"query": "write a function..."},
    severity=7
)

# Log a success
tracker.log_success("programming")
```

## Learning Cycle Workflow

### Step 1: Review Failures
```python
# Get failure clusters from last 7 days
clusters = tracker.get_failure_clusters(days=7)

# Output:
# {
#   "programming": [failure1, failure2, ...],
#   "advice": [failure3, failure4, ...]
# }
```

### Step 2: Identify Weakest Skills
```python
# Analyze which skills need improvement
weakest = tracker.identify_weakest_skills(days=7, min_samples=5)

# Output:
# [
#   {
#     "skill": "programming",
#     "total_interactions": 50,
#     "failures": 20,
#     "success_rate": 0.6,
#     "avg_severity": 7.2,
#     "top_categories": ["syntax_error", "logic_error"]
#   },
#   ...
# ]
```

### Step 3: Generate Training Data
```python
from jessica.meta.synthetic_data_generator import SyntheticDataGenerator

gen = SyntheticDataGenerator()

# Get failure patterns
patterns = tracker.get_failure_patterns("programming", days=30)

# Generate training data
training_data = gen.generate_training_data(
    skill="programming",
    failure_patterns=patterns,
    target_count=50
)

# Export to JSONL for fine-tuning
gen.export_to_jsonl(training_data, "training_data.jsonl")
```

### Step 4: Fine-Tune
```bash
# Use existing self-upgrade pipeline
python jessica/lora_pipeline/export_conversations.py
python jessica/lora_pipeline/train_lora.py
python jessica/lora_pipeline/convert_adapter.py
python jessica/lora_pipeline/promote_adapter.py
```

### Step 5: Validate & Track
```python
# After training, mark cycle complete
loop.mark_cycle_complete(
    cycle_id=1,
    improvement_metrics={
        "success_rate": 0.85,  # Improved from 0.6
        "avg_severity": 4.0,    # Reduced from 7.2
        "failure_count": 5      # Reduced from 20
    }
)

# Get learning stats
stats = loop.get_learning_stats()
print(f"Average improvement: {stats['avg_improvement']:.1f}%")
```

## Integration with Jessica

### Option 1: Manual Integration (in skills)

```python
# In jessica/skills/programming_skill.py
from jessica.meta.failure_tracker import FailureTracker

def execute_programming_skill(query):
    tracker = FailureTracker()
    
    try:
        result = generate_code(query)
        
        # Validate result
        if is_valid_code(result):
            tracker.log_success("programming")
            return result
        else:
            tracker.log_failure(
                "programming",
                "invalid_code",
                "Generated code failed validation",
                context={"query": query},
                severity=6
            )
            return None
            
    except SyntaxError as e:
        tracker.log_failure(
            "programming",
            "syntax_error",
            str(e),
            context={"query": query},
            severity=7
        )
        raise
```

### Option 2: Decorator Pattern

```python
from jessica.meta.failure_tracker import FailureTracker
from functools import wraps

def track_skill(skill_name):
    """Decorator to automatically track skill performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = FailureTracker()
            try:
                result = func(*args, **kwargs)
                tracker.log_success(skill_name)
                return result
            except Exception as e:
                tracker.log_failure(
                    skill_name,
                    type(e).__name__,
                    str(e),
                    severity=7
                )
                raise
        return wrapper
    return decorator

# Usage:
@track_skill("programming")
def execute_programming_skill(query):
    return generate_code(query)
```

### Option 3: Scheduled Weekly Runs

Add to `jessica_schedule.json`:
```json
{
  "autodidactic_cycle": {
    "enabled": true,
    "frequency": "weekly",
    "day": "Sunday",
    "time": "02:00",
    "action": "run_learning_cycle"
  }
}
```

## Configuration

### AutodidacticLoop Config
```python
loop = AutodidacticLoop()

# Customize config
loop.config = {
    "lookback_days": 7,              # Analyze last N days
    "min_failures_threshold": 5,      # Min failures to consider
    "training_data_count": 50,        # Examples per cycle
    "success_rate_threshold": 0.7,    # Below this = needs work
    "cycle_interval_days": 7          # Run weekly
}

loop.save()
```

### SyntheticDataGenerator Templates

Add custom templates for new skills:
```python
# In synthetic_data_generator.py
self.templates["new_skill"] = [
    {
        "pattern": "common_error",
        "prompt": "Template prompt with {variable}",
        "completion": "Template response with {result}",
        "variables": ["option1", "option2", "option3"]
    }
]
```

## Failure Categories

### Common Categories
- **syntax_error**: Code syntax issues
- **logic_error**: Incorrect logic or algorithm
- **type_error**: Type mismatches
- **timeout**: Operation took too long
- **low_quality**: Response below quality threshold
- **incorrect_answer**: Factually wrong
- **incomplete**: Partial or incomplete response
- **hallucination**: Generated false information

### Severity Levels (1-10)
- **1-3**: Minor (typos, formatting)
- **4-6**: Moderate (logic errors, quality issues)
- **7-8**: Serious (wrong answers, crashes)
- **9-10**: Critical (safety issues, data loss)

## API Reference

### FailureTracker

#### Methods
```python
# Log events
log_failure(skill, category, description, context=None, severity=5)
log_success(skill, context=None)

# Analysis
get_failure_clusters(days=7) -> Dict[str, List[FailureEvent]]
identify_weakest_skills(days=7, min_samples=3) -> List[Dict]
get_failure_patterns(skill, days=30) -> Dict
get_improvement_priority(days=7) -> List[str]

# Management
clear_old_data(days=90) -> int
get_stats() -> Dict

# Persistence
save()
load()
```

### SyntheticDataGenerator

#### Methods
```python
# Generate data
generate_training_data(skill, failure_patterns, target_count=50) -> List[Dict]

# Export
export_to_jsonl(examples, output_path)
export_to_csv(examples, output_path)

# Augmentation
augment_with_variations(examples, variations=3) -> List[Dict]

# Stats
get_stats(examples) -> Dict
```

### AutodidacticLoop

#### Methods
```python
# Core workflow
run_learning_cycle(force_skill=None) -> Optional[LearningCycle]
mark_cycle_complete(cycle_id, improvement_metrics)

# Analysis
get_learning_stats() -> Dict
get_next_cycle_recommendation() -> Dict

# Reporting
export_report(output_path="autodidactic_report.txt")

# Scheduling
schedule_weekly() -> str  # Returns setup instructions

# Persistence
save()
load()
```

## Training Data Format

### JSONL Format (for fine-tuning)
```json
{"messages": [{"role": "user", "content": "Write a function that reverses a string"}, {"role": "assistant", "content": "```python\ndef reverse_string(s):\n    return s[::-1]\n```\n\nThis function reverses the string using Python's slicing syntax."}]}
{"messages": [{"role": "user", "content": "Find the maximum in a list"}, {"role": "assistant", "content": "```python\ndef find_max(arr):\n    return max(arr)\n```\n\nThis uses Python's built-in max() function."}]}
```

### CSV Format
```csv
prompt,completion
"Write a function that reverses a string","```python\ndef reverse_string(s):\n    return s[::-1]\n```"
"Find the maximum in a list","```python\ndef find_max(arr):\n    return max(arr)\n```"
```

## Benchmarks & Validation

### Pre-Training Benchmark
```python
# Before fine-tuning, establish baseline
tracker = FailureTracker()
baseline = tracker.identify_weakest_skills(days=7)[0]

print(f"Baseline: {baseline['success_rate']:.1%}")
```

### Post-Training Validation
```python
# After fine-tuning, test on held-out examples
# Run same tasks and compare metrics

post_training = {
    "success_rate": 0.85,
    "avg_severity": 4.0,
    "failure_count": 3
}

improvement = (post_training['success_rate'] - baseline['success_rate']) / baseline['success_rate']
print(f"Improvement: {improvement:.1%}")
```

## Monitoring & Reporting

### Weekly Report
```python
loop = AutodidacticLoop()
loop.export_report("weekly_learning_report.txt")
```

Output:
```
========================================
AUTODIDACTIC LEARNING REPORT
Generated: 2026-02-03 08:00:00
========================================

SUMMARY
-------
Total learning cycles: 5
Completed cycles: 4
In progress: 1
Skills improved: programming, advice, chess
Average improvement: 28.5%
Total training examples: 250

NEXT CYCLE
----------
Should run: True
Recommended skill: math
Reason: Skill 'math' has highest improvement priority
Days since last: 7
```

### Cycle Details
```python
for cycle in loop.cycles:
    print(f"Cycle #{cycle.cycle_id}: {cycle.target_skill}")
    print(f"  Baseline: {cycle.baseline_metrics['success_rate']:.1%}")
    if cycle.improvement_metrics:
        print(f"  Improved: {cycle.improvement_metrics['success_rate']:.1%}")
```

## Advanced Features

### Multi-Skill Training
```python
# Generate training data for multiple skills
for skill in ["programming", "advice", "math"]:
    patterns = tracker.get_failure_patterns(skill)
    data = gen.generate_training_data(skill, patterns, 30)
    gen.export_to_jsonl(data, f"{skill}_training.jsonl")
```

### Custom Templates
```python
# Add domain-specific templates
gen.templates["medical"] = [
    {
        "pattern": "diagnosis_error",
        "prompt": "What are symptoms of {condition}?",
        "completion": "Symptoms include: {symptoms}",
        "conditions": ["flu", "cold", "allergies"]
    }
]
```

### Adaptive Thresholds
```python
# Adjust thresholds based on skill difficulty
loop.config["success_rate_threshold"] = {
    "programming": 0.8,  # Higher standard
    "chess": 0.6,         # Lower (harder domain)
    "advice": 0.7         # Medium
}
```

## Testing

Run comprehensive test suite:
```bash
pytest test_autodidactic_loop.py -v
```

16 tests covering:
- Failure tracking
- Weakness identification
- Data generation
- Learning cycles
- Progress tracking
- Persistence

## Limitations

1. **Template-Based**: Synthetic data uses templates (not as diverse as real data)
2. **Skill-Specific**: Requires templates for each skill
3. **Manual Validation**: Generated data should be reviewed before training
4. **No Active Learning**: Doesn't query humans for hard examples
5. **Single-Skill Focus**: One skill per cycle (no multi-task learning)

## Future Enhancements

1. **Active Learning**: Query user for hard examples
2. **Cross-Skill Transfer**: Use knowledge from strong skills to improve weak ones
3. **Difficulty Progression**: Start easy, gradually increase complexity
4. **Quality Filters**: Automatically filter low-quality synthetic data
5. **Reinforcement Learning**: Learn from user feedback on responses
6. **Continuous Fine-Tuning**: Stream fine-tuning instead of batch
7. **Meta-Learning**: Learn how to learn more efficiently

## Example Output

```
🔬 Starting autodidactic learning cycle...

📊 Step 1: Reviewing failure clusters...
Found failures in 3 skills

🎯 Step 2: Identifying weakest skill...
Target skill: programming
  Success rate: 55.0%
  Avg severity: 6.8/10
  Failures: 18

📝 Step 3: Generating synthetic training data...
Generated 50 training examples

💾 Step 4: Exporting training data...
Saved to: jessica_data_embeddings/autodidactic_cycles/cycle_3_programming_20260203.jsonl

📈 Step 5: Recording learning cycle...

✅ Learning cycle #3 complete!

📋 Next steps:
1. Review training data
2. Fine-tune model using this data
3. Run validation benchmarks
4. Call mark_cycle_complete(3, metrics) when done
```

## References

- Self-Upgrade System: `docs/SELF_UPGRADE_SYSTEM.md`
- LoRA Pipeline: `jessica/lora_pipeline/`
- Meta-Cognition: `jessica/meta/meta_cognition.py`
- Identity Anchors: `jessica/meta/identity_anchors.py`
- Causal Models: `jessica/meta/causal_world_models.py`

---

**Jessica becomes her own teacher. 🎓**
