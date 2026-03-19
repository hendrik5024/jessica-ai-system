# Regret & Alternative-History Memory

**"Over time, regret shapes behavior more than rewards. This is wisdom accumulation."**

## Overview

The Regret & Alternative-History Memory system enables Jessica to learn from mistakes through counterfactual reasoning. Instead of just storing what went wrong, it tracks:

1. **What actually happened** (chosen action + outcome)
2. **What could have happened** (better alternative + expected outcome)
3. **Why the alternative was better** (lesson learned)
4. **Wisdom accumulated** (how much this shapes future behavior)

This system implements a profound insight from cognitive science: **humans learn more from regret than from rewards**. By tracking mistakes and their alternatives, Jessica builds wisdom that prevents repeating the same errors.

## Philosophy

### Why Regret Memory?

Traditional AI systems optimize for rewards. But human wisdom comes from:
- Recognizing patterns in past failures
- Comparing what happened vs. what could have happened
- Avoiding similar mistakes in the future
- Building intuition through accumulated experience

**Counterfactual Learning**: "If I had done X instead of Y, the outcome would have been Z."

This is how humans develop judgment, caution, and wisdom - not from success alone, but from understanding failure.

## Architecture

### Core Components

```
RegretToken (Dataclass)
├── Situation Context
│   ├── situation: What was happening
│   ├── context: Additional details
│   └── timestamp: When it occurred
│
├── What Went Wrong
│   ├── chosen_action: What I actually did
│   ├── outcome: What actually happened
│   └── severity: How bad (1-10)
│
├── What Should Have Happened
│   ├── better_alternative: What I should have done
│   ├── alternative_source: Where this came from (user_correction, self_analysis, etc.)
│   └── lesson: The key takeaway
│
└── Wisdom Tracking
    ├── times_recalled: How often I remember this
    ├── times_avoided: How often I avoided repeating it
    └── wisdom_score: 0.0-1.0 (accumulated learning)

RegretMemory (Class)
├── Storage: JSON persistence
├── Triggers: correction, failure, confusion, negative_feedback
├── Queries: Find similar regrets, extract lessons
└── Updates: Mark recalled, mark avoided (increases wisdom)
```

### Trigger Types

1. **correction**: User corrects Jessica's response
   - "No, that's wrong. It should be X"
   - Captures the correction as a better alternative

2. **failure**: Advice or action failed
   - "That didn't work"
   - Tracks why it failed and what worked instead

3. **confusion**: User shows confusion indicators
   - "What?", "Huh?", "I don't understand"
   - Suggests need for clearer explanation

4. **negative_feedback**: User expresses dissatisfaction
   - "That's not helpful", "That doesn't answer my question"
   - Indicates response quality issues

## API Reference

### Creating Regrets

#### `add_regret(trigger_type, situation, chosen_action, outcome, better_alternative, lesson, severity=5)`

Generic method for adding any regret.

```python
memory = RegretMemory()

regret = memory.add_regret(
    trigger_type="correction",
    situation="User asked for Python code",
    chosen_action="Generated Java code",
    outcome="User said 'No, I need Python'",
    better_alternative="Generate Python code",
    lesson="Match the requested programming language",
    severity=7
)
```

#### `add_correction(situation, what_i_said, what_user_said, severity=6)`

Convenience method for user corrections.

```python
regret = memory.add_correction(
    situation="User asked: 'How do I reverse a string in Python?'",
    what_i_said="Use StringBuilder.reverse() method",
    what_user_said="No, that's Java. In Python it's s[::-1]"
)
```

#### `add_confusion(situation, what_i_said, confusion_indicators, severity=5)`

Log when user is confused by explanation.

```python
regret = memory.add_confusion(
    situation="Explained quantum physics",
    what_i_said="Superposition is when particles exist in multiple states",
    confusion_indicators=["what?", "huh?", "I don't understand"]
)
```

#### `add_failed_advice(situation, advice_given, why_it_failed, what_worked, severity=7)`

Track advice that didn't work.

```python
regret = memory.add_failed_advice(
    situation="User wanted to improve sleep",
    advice_given="Drink coffee before bed",
    why_it_failed="Caffeine keeps people awake",
    what_worked="Avoid caffeine 6 hours before bed"
)
```

### Querying Regrets

#### `find_similar_regrets(situation, threshold=0.6)`

Find past regrets similar to current situation.

```python
# New situation
similar = memory.find_similar_regrets("User asked for Python sorting")

# Returns list of RegretTokens with similar contexts
for regret in similar:
    print(f"Past regret: {regret.situation}")
    print(f"Lesson: {regret.lesson}")
```

**Use case**: Before responding, check if similar situations led to regrets. Apply those lessons proactively.

#### `get_lessons_learned()`

Extract consolidated lessons from all regrets.

```python
lessons = memory.get_lessons_learned()

# [
#   {
#     "lesson": "Match the requested programming language",
#     "count": 5,
#     "avg_severity": 6.2,
#     "total_wisdom": 1.8
#   },
#   ...
# ]
```

**Use case**: Identify most important lessons to prioritize in behavior.

### Wisdom Accumulation

#### `mark_regret_recalled(regret_id)`

Increase wisdom when a past regret is remembered.

```python
# When similar situation occurs and you remember past regret:
memory.mark_regret_recalled(regret_id)

# Wisdom increases by 0.1 (small boost)
```

#### `mark_mistake_avoided(regret_id)`

Significantly increase wisdom when mistake is avoided.

```python
# When you successfully avoid making the same mistake:
memory.mark_mistake_avoided(regret_id)

# Wisdom increases by 0.2 (big boost!)
```

**Wisdom Score Evolution**:
- Initial: 0.0 (just learned)
- After recalls: 0.1-0.3 (remembered)
- After avoidances: 0.4-1.0 (integrated into behavior)

### Reports & Analysis

#### `get_wisdom_report()`

Statistics on wisdom accumulation.

```python
report = memory.get_wisdom_report()

# {
#   "total_regrets": 15,
#   "total_wisdom": 8.4,
#   "avg_wisdom_per_regret": 0.56,
#   "top_lessons": [...],
#   "most_avoided_mistakes": [...],
#   "trigger_breakdown": {"correction": 8, "failure": 4, ...}
# }
```

#### `get_alternative_history(regret_id)`

Compare actual vs. alternative outcomes.

```python
alt_history = memory.get_alternative_history(regret_id)

# {
#   "what_happened": {
#     "my_action": "Gave Java code",
#     "outcome": "User corrected me",
#     "severity": 7
#   },
#   "what_could_have_happened": {
#     "better_action": "Give Python code",
#     "lesson_learned": "Match requested language",
#     "wisdom_accumulated": 0.4
#   },
#   "impact": {
#     "times_recalled": 3,
#     "times_avoided": 2,
#     "changed_behavior": True
#   }
# }
```

## Integration

### With Agent Loop

Detect and log regrets automatically during conversations:

```python
from jessica.meta.regret_memory import RegretMemory

class Agent:
    def __init__(self):
        self.regret_memory = RegretMemory()
    
    def process_response(self, user_input, my_response):
        # Detect corrections
        if is_correction(user_input):
            self.regret_memory.add_correction(
                situation=self.context.last_query,
                what_i_said=self.context.last_response,
                what_user_said=user_input
            )
        
        # Detect confusion
        if is_confusion(user_input):
            self.regret_memory.add_confusion(
                situation=self.context.last_query,
                what_i_said=self.context.last_response,
                confusion_indicators=extract_indicators(user_input)
            )
        
        # Before responding, check for similar regrets
        similar = self.regret_memory.find_similar_regrets(user_input)
        if similar:
            # Recall these regrets (increases wisdom)
            for regret in similar:
                self.regret_memory.mark_regret_recalled(regret.regret_id)
            
            # Apply lessons in response
            lessons = [r.lesson for r in similar]
            my_response = apply_lessons(my_response, lessons)
            
            # If successfully avoided mistake, mark it
            if avoided_mistake(my_response, similar):
                for regret in similar:
                    self.regret_memory.mark_mistake_avoided(regret.regret_id)
```

### With Failure Tracker (Autodidactic Loop)

Connect regrets to self-directed learning:

```python
from jessica.meta.failure_tracker import FailureTracker
from jessica.meta.regret_memory import RegretMemory

# When failure tracker identifies a failure:
failure = tracker.log_interaction(user_query, response, success=False)

# Create corresponding regret:
regret = regret_memory.add_regret(
    trigger_type="failure",
    situation=failure.query,
    chosen_action=failure.response,
    outcome=failure.error_type,
    better_alternative="[To be determined through learning]",
    lesson=f"Failed at: {failure.skill_used}",
    severity=8
)

# Use regrets to guide learning:
lessons = regret_memory.get_lessons_learned()
weakest_areas = [l["lesson"] for l in lessons if l["count"] >= 3]

# Generate training data for these areas
for area in weakest_areas:
    autodidactic_loop.generate_training_for(area)
```

## Example Workflows

### Workflow 1: Correction Learning

```
1. User: "How to reverse a string in Python?"
2. Jessica: "Use StringBuilder.reverse() method"
3. User: "No, that's Java! In Python it's s[::-1]"

→ Regret logged:
  - Situation: "How to reverse a string in Python?"
  - Chosen: "Use StringBuilder.reverse()"
  - Better: "s[::-1]"
  - Lesson: "Match requested programming language"
  - Wisdom: 0.0 (new)

4. User: "How to sort a list in Python?"
5. Jessica checks memory → Finds similar regret
6. Jessica recalls regret (wisdom → 0.1)
7. Jessica applies lesson → Gives Python answer
8. User: "Perfect, thanks!"
9. Jessica marks mistake avoided (wisdom → 0.3)
```

### Workflow 2: Repeated Mistakes

```
Multiple occurrences of same mistake:

Regret 1: Wrong language (wisdom: 0.3)
Regret 2: Wrong language (wisdom: 0.3)
Regret 3: Wrong language (wisdom: 0.4)
Regret 4: Wrong language (wisdom: 0.5)

Lessons learned report shows:
"Match requested programming language" - count: 4, total wisdom: 1.5

This pattern recognition guides future behavior more strongly.
```

### Workflow 3: Alternative History Analysis

```
User requests: "Show me what went wrong last time"

Jessica retrieves alternative history:

"Last time you asked about sorting in Python, I gave you Java code.
If I had given Python code instead, you would have been able to 
use it immediately. I've learned to always check the requested language."

This transparency builds trust and shows real learning.
```

## Wisdom Scoring

### How Wisdom Accumulates

**Initial Regret**: wisdom_score = 0.0
- Just learned, not yet integrated

**After Recall** (+0.1 per recall):
- Remembering → 0.1
- Remembering again → 0.2
- Multiple recalls → 0.3-0.4
- Capped at 0.5 from recalls alone

**After Avoidance** (+0.2 per avoidance):
- First avoidance → 0.2+ (significant boost)
- Second avoidance → 0.4+
- Consistent avoidance → 0.6-1.0
- Shows behavior change

**Wisdom Threshold Interpretation**:
- **0.0-0.2**: Aware but not integrated
- **0.3-0.5**: Recalled regularly, partially integrated
- **0.6-0.8**: Actively avoided, well integrated
- **0.9-1.0**: Deeply internalized, automatic avoidance

### Wisdom Formula

```python
wisdom_score = min(1.0, times_recalled * 0.1 + times_avoided * 0.2)
```

This emphasizes **behavior change** (avoidance) over mere **awareness** (recall).

## Best Practices

### 1. Log Regrets Immediately

Don't wait - capture regrets when they happen:

```python
# ✅ Good
user_says_no = detect_correction(user_input)
if user_says_no:
    memory.add_correction(...)

# ❌ Bad
# [Manually log later - easy to forget]
```

### 2. Check Before Responding

Proactively apply past lessons:

```python
# Before generating response
similar_regrets = memory.find_similar_regrets(user_query)
if similar_regrets:
    # Apply lessons
    lessons = [r.lesson for r in similar_regrets]
    response = generate_response_with_lessons(query, lessons)
```

### 3. Mark Avoidance Explicitly

When you successfully avoid a mistake, mark it:

```python
if successfully_applied_lesson:
    memory.mark_mistake_avoided(regret_id)
```

This significantly boosts wisdom and reinforces learning.

### 4. Review Wisdom Reports

Periodically check what's been learned:

```python
report = memory.get_wisdom_report()

# Focus on high-count, low-wisdom lessons
for lesson in report['top_lessons']:
    if lesson['count'] >= 3 and lesson['wisdom_score'] < 0.5:
        # This is a repeated issue not yet fixed
        prioritize_for_improvement(lesson)
```

### 5. Use Alternative History for Transparency

Show users you're learning:

```python
if user_asks_about_learning:
    recent_regrets = memory.regrets[-5:]
    for regret in recent_regrets:
        alt_history = memory.get_alternative_history(regret.regret_id)
        explain_alternative_history(alt_history)
```

## Testing

Run the test suite:

```bash
pytest test_regret_memory.py -v
```

**Tests cover**:
- Adding regrets (all trigger types)
- Finding similar regrets
- Lesson consolidation
- Wisdom accumulation (recall and avoidance)
- Alternative history retrieval
- Persistence (save/load)

## Demo

Run the demo to see regret memory in action:

```bash
python demo_regret_memory.py
```

**Demo shows**:
1. User corrections → Regret tokens
2. Wisdom accumulation over time
3. Alternative history comparison
4. Confusion detection
5. Failed advice learning
6. Comprehensive wisdom report

## Future Enhancements

### Potential Improvements

1. **Regret Clustering**: Group similar regrets automatically
   ```python
   clusters = memory.cluster_regrets(method="semantic")
   # Find meta-patterns across multiple failures
   ```

2. **Severity-Weighted Learning**: High-severity regrets boost wisdom more
   ```python
   wisdom_boost = base_boost * (severity / 10.0)
   ```

3. **Time Decay**: Older regrets matter less
   ```python
   age_factor = 1.0 - (days_old / 365.0)  # Decay over a year
   effective_wisdom = wisdom_score * age_factor
   ```

4. **LLM-Generated Lessons**: Use LLM to extract better lessons
   ```python
   lesson = llm.extract_lesson(wrong_response, right_response)
   # More nuanced than rule-based extraction
   ```

5. **Proactive Regret Simulation**: Predict potential regrets before acting
   ```python
   potential_regrets = memory.simulate_response(planned_response)
   if potential_regrets:
       revise_response()
   ```

## Summary

Regret & Alternative-History Memory implements **counterfactual learning** - the ability to imagine what could have been and learn from it. This is a cornerstone of human wisdom.

**Key Features**:
- ✅ Track mistakes with their better alternatives
- ✅ Wisdom scoring (0.0-1.0) based on recall and avoidance
- ✅ Pattern matching for similar situations
- ✅ Lesson consolidation across multiple regrets
- ✅ Alternative history comparison
- ✅ Integration with agent loop and autodidactic learning

**Impact**:
- Jessica learns more from mistakes than successes
- Repeated errors are recognized and avoided
- Wisdom accumulates over time through behavior change
- Transparency: Users can see what Jessica has learned

**Quote**:
> "Over time, regret shapes behavior more than rewards. This is wisdom accumulation."

---

**Status**: ✅ **COMPLETE**
- Module: [jessica/meta/regret_memory.py](jessica/meta/regret_memory.py)
- Tests: 14/14 passing
- Demo: Working
- Documentation: This file
