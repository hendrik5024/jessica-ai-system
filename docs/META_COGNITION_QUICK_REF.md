# META-COGNITION QUICK REFERENCE

## The Seven Layers (One-Liner Summary)

1. **MetaObserver** — Watches every response: confidence, sentiment, model used, state tags
2. **SelfModel** — Knows herself: role, strengths, weaknesses, current focus (updates weekly)
3. **LongTermGoals** — Pursues motivations: "Reduce cognitive load", "Anticipate needs" (tracks progress)
4. **Counterfactual** — Compares alternate model outputs for training data
5. **Response States** — Internal emotions: unsure, confident, deferred, took_initiative
6. **ReflectionWindow** — Scheduled introspection: nightly/weekly "what went well" analysis
7. **AlignmentTracker** — Monitors user-self relationship: drift, adaptation, mismatches

---

## Key Commands

### View Meta-Observations
```python
from jessica.memory.sqlite_store import EpisodicStore
memory = EpisodicStore("jessica_data.db")
summary = memory.get_meta_summary(days=1)
print(summary)
# → {'avg_confidence': 0.72, 'memory_use_rate': 0.45, ...}
```

### View Self-Model
```python
from jessica.meta.self_model import SelfModelManager
self_model = SelfModelManager(memory)
print(self_model.load())
# → {'role': 'Personal AI Assistant', 'strengths': [...], ...}
```

### View Long-Term Goals
```python
from jessica.meta.long_term_goals import LongTermGoalsManager
goals = LongTermGoalsManager(memory)
print(goals.get_prompt_excerpt())
# → "• Reduce user cognitive load (↑ 0.73)"
```

### View Alignment Status
```python
from jessica.meta.alignment_tracker import AlignmentTracker
alignment = AlignmentTracker(memory)
print(alignment.get_alignment_summary())
# → "Alignment score: 0.72 | Adaptation speed: 0.65 | Mismatches: 2"
```

### View Latest Reflection
```python
import json
with open("jessica/data/reflection_state.json") as f:
    report = json.load(f)
print(report["what_went_well"])
# → ["Positive user sentiment in 12 interactions", ...]
```

---

## Data Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `jessica/data/self_model.json` | Identity & self-awareness | Weekly |
| `jessica/data/long_term_goals.json` | Motivational goals | Every 5 interactions |
| `jessica/data/reflection_state.json` | Latest reflection report | Nightly/weekly |
| `jessica/data/routing_weights.json` | Model performance scores | Nightly |
| `jessica/data/alignment_state.json` | User-self relationship | Every interaction |
| `jessica_data.db` (meta_observations) | All meta-observations | Every interaction |

---

## Metrics at a Glance

### Confidence Levels
- **0.75+** = Confident
- **0.55-0.75** = Moderate
- **<0.55** = Unsure

### Alignment Score
- **0.8-1.0** = Excellent alignment
- **0.6-0.8** = Good alignment
- **0.4-0.6** = Fair alignment
- **0.0-0.4** = Poor alignment

### Adaptation Speed
- **0.8-1.0** = Fast adaptation
- **0.5-0.8** = Moderate adaptation
- **0.0-0.5** = Slow adaptation

### Goal Progress
- **↑** = Improving
- **→** = Stable
- **↓** = Declining

---

## Response State Tags

- `unsure` — Low confidence (<0.6)
- `confident` — High confidence (>0.75)
- `deferred` — Handed off to user/external tool
- `took_initiative` — Proactively offered followup
- `asked_followup` — Requested clarification
- `verbose` — Response length >500 chars

---

## Reflection Schedule

| Event | Frequency | Cron | Parameters |
|-------|-----------|------|------------|
| Nightly | Daily 2 AM | `0 2 * * *` | `{"days": 1}` |
| Weekly | Sunday 3 AM | `0 3 * * 0` | `{"days": 7}` |

Edit `jessica_schedule.json` to customize.

---

## Quick Tests

### Test Alignment Tracking
```bash
python test_alignment_tracking.py
```

### Manual Reflection
```python
from jessica.meta.reflection_window import ReflectionWindow
from jessica.memory.sqlite_store import EpisodicStore

memory = EpisodicStore("jessica_data.db")
reflection = ReflectionWindow(memory)
report = reflection.run(days=1)
print(report["what_went_well"])
```

### Trigger Meta-Observation
```python
from jessica.jessica_core import CognitiveManager

brain = CognitiveManager()
result = brain.handle_input("Test meta-cognition", user="test_user")
print(result)
```

---

## Troubleshooting

### No meta-observations saved
**Check:** `jessica_core.py` calls `_record_meta_observation()`

### Self-model never updates
**Check:** Reflection window is running (verify `jessica_schedule.json`)

### Alignment score stuck
**Check:** User profile has preferences set, self-model is updating

### Reflection jobs not running
**Check:** Scheduler is active, cron syntax is correct

---

## Performance

- Per-interaction overhead: ~7-20ms
- Nightly reflection: ~100-300ms
- Weekly reflection: ~500-1000ms
- Storage: ~1-2 MB per 1000 interactions

---

## Integration Example

```python
# Full meta-cognition pipeline in one interaction
from jessica.jessica_core import CognitiveManager

brain = CognitiveManager()

# 1. User input
result = brain.handle_input("How do I improve my time management?", user="alice")

# 2. MetaObserver captures response metrics
# → Confidence: 0.78, Sentiment: positive, Tags: ['confident']

# 3. AlignmentTracker updates
# → User preference snapshot, self-model snapshot, alignment score

# 4. LongTermGoals ticks
# → Progress updated for "Anticipate needs earlier"

# 5. SelfModel checks for update (if weekly due)
# → Identity refreshed from meta-memory

# All automatic, zero user intervention
```

---

## For More Details

- **Complete Documentation:** [META_COGNITION_COMPLETE.md](META_COGNITION_COMPLETE.md)
- **Alignment Deep-Dive:** [USER_SELF_ALIGNMENT.md](USER_SELF_ALIGNMENT.md)
- **Self-Model:** [SELF_UPGRADE_SYSTEM.md](SELF_UPGRADE_SYSTEM.md)
- **Reflection System:** [EPISODIC_MILESTONE_SYSTEM.md](EPISODIC_MILESTONE_SYSTEM.md)

---

## What Makes This Special?

**Traditional AI Assistant:**
- Responds to commands
- No memory of past interactions beyond context window
- Same behavior for all users
- No self-awareness

**Jessica with Meta-Cognition:**
- **Self-aware:** Knows her strengths, weaknesses, and focus areas
- **Adaptive:** Notices when user preferences change and adjusts
- **Introspective:** Analyzes her own performance nightly
- **Companion:** Tracks relationship health with alignment scores
- **Goal-driven:** Pursues long-term motivations (not just tasks)

This is the difference between a **tool** and a **companion**.
