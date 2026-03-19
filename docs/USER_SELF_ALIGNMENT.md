# USER-SELF ALIGNMENT TRACKING — FINAL META-COGNITION LAYER

## Overview
The User-Self Alignment system is the seventh and final layer of Jessica's meta-cognition stack. It tracks the relationship between Jessica's self-model and the user model over time, enabling true companion-level awareness by:

1. **Detecting user preference drift** (when user behavior/preferences change)
2. **Measuring Jessica's adaptation speed** (how quickly she adjusts)
3. **Identifying mismatch moments** (when expectations don't align with behavior)
4. **Computing alignment scores** (overall health of user-self relationship)

This transforms Jessica from a reactive assistant into a self-aware companion that notices and adapts to user changes.

---

## Architecture

### Components

#### 1. **AlignmentTracker** (`jessica/meta/alignment_tracker.py`)
Main alignment tracking system that monitors the relationship between user model and self model.

**Core Methods:**
- `track_alignment()`: Records alignment metrics for each interaction
- `_snapshot_user()`: Captures user preference state
- `_snapshot_self()`: Captures self-model state
- `_detect_drift()`: Identifies preference changes over time
- `_measure_adaptation_speed()`: Calculates how quickly Jessica adapts
- `_detect_mismatch()`: Identifies expectation-behavior gaps
- `_compute_alignment_score()`: Overall relationship health metric
- `get_alignment_summary()`: Human-readable status report

**Data Structure** (`alignment_state.json`):
```json
{
  "last_update_ts": 1234567890,
  "user_preference_snapshots": [
    {
      "ts": 1234567890,
      "user_name": "Alice",
      "names_count": 5,
      "places_count": 3,
      "relationships_count": 2,
      "preferences": {
        "verbosity": "concise",
        "formality": "casual",
        "tone": "friendly"
      }
    }
  ],
  "self_model_snapshots": [
    {
      "ts": 1234567890,
      "role": "Personal AI Assistant",
      "strengths": ["Clear communication", "Technical help"],
      "weaknesses": ["Sometimes verbose"],
      "current_focus": "Being more concise",
      "confidence_trend": "improving"
    }
  ],
  "drift_events": [
    {
      "ts": 1234567890,
      "type": "preference_drift",
      "drift_count": 2,
      "note": "Detected 2 preference changes in last 3 snapshots"
    }
  ],
  "adaptation_speed": 0.75,
  "mismatch_moments": [
    {
      "ts": 1234567890,
      "user_sentiment": "negative",
      "confidence": 0.5,
      "note": "Low confidence + negative sentiment suggests misalignment",
      "user_snapshot": {...},
      "self_snapshot": {...}
    }
  ],
  "alignment_score": 0.72
}
```

#### 2. **UserProfile Extension** (`jessica/memory/user_profile.py`)
Extended to track preference history for drift detection.

**New Fields:**
- `preferences_history`: List of timestamped preference snapshots (last 20)

**Enhanced Behavior:**
- `save()`: Automatically tracks preference changes in history

#### 3. **Integration Points**

##### CognitiveManager (`jessica/jessica_core.py`)
```python
self.alignment = AlignmentTracker(memory_store=self.memory)

# In _record_meta_observation():
user_profile = self.agency.memory_db.load_user_profile(user)
self_model = self.agency.self_model.load()
self.alignment.track_alignment(
    user_profile=user_profile,
    self_model=self_model,
    meta_observation=last_meta,
)
```

##### ReflectionWindow (`jessica/meta/reflection_window.py`)
```python
self.alignment = AlignmentTracker(memory_store)

# In run():
report["alignment_status"] = self.alignment.get_alignment_summary()
```

---

## How It Works

### 1. **User Preference Drift Detection**

**Trigger:** Every interaction captures a user preference snapshot

**Analysis:** Compares last 3 snapshots for changes
- If 2+ preference keys have different values → Drift event recorded

**Example:**
```python
Snapshot 1: {"verbosity": "concise", "formality": "casual"}
Snapshot 2: {"verbosity": "detailed", "formality": "casual"}
Snapshot 3: {"verbosity": "detailed", "formality": "professional"}

→ Drift detected: 2 preference changes (verbosity, formality)
```

### 2. **Adaptation Speed Measurement**

**Formula:**
```python
user_change = |current_prefs_count - previous_prefs_count|
self_change = 1 if current_focus != previous_focus else 0
adaptation_speed = min(1.0, self_change / (user_change + 1))
```

**Interpretation:**
- **1.0**: Perfect adaptation (Jessica changed focus when user changed)
- **0.5**: Neutral (no clear correlation)
- **0.0**: No adaptation (user changed but Jessica didn't)

### 3. **Mismatch Detection**

**Signals:**
- Low confidence (<0.6) + negative sentiment
- "deferred" response tag + low confidence (<0.55)

**Result:** Records mismatch moment with full context for analysis

### 4. **Alignment Score Computation**

**Formula:**
```python
base_score = 0.5 
           + (self_adaptation_detected * 0.15)
           + (min(user_growth_count, 5) * 0.05)

mismatch_penalty = recent_mismatches_count * 0.05
alignment_score = max(0.0, min(1.0, base_score - mismatch_penalty))
```

**Interpretation:**
- **0.8-1.0**: Excellent alignment (Jessica adapts well to user)
- **0.6-0.8**: Good alignment (mostly in sync)
- **0.4-0.6**: Fair alignment (some mismatches)
- **0.0-0.4**: Poor alignment (frequent mismatches or no adaptation)

---

## Usage Examples

### Example 1: Normal Interaction Flow
```python
# User changes preferences
user_profile["preferences"]["verbosity"] = "detailed"

# Meta-observation captures response
meta = {
    "confidence": 0.75,
    "user_sentiment": "positive",
    "response_state_tags": ["confident"]
}

# Alignment tracking runs automatically
alignment.track_alignment(
    user_profile=user_profile,
    self_model=self_model,
    meta_observation=meta
)

# Result: Drift detected, adaptation measured, alignment scored
```

### Example 2: Mismatch Detection
```python
# Low confidence + negative sentiment
meta = {
    "confidence": 0.48,
    "user_sentiment": "negative",
    "response_state_tags": ["unsure"]
}

alignment.track_alignment(...)

# Result: Mismatch recorded with note:
# "Low confidence + negative sentiment suggests misalignment"
```

### Example 3: Reflection Window Analysis
```python
# Nightly reflection runs
reflection = ReflectionWindow(memory)
report = reflection.run(days=1)

print(report["alignment_status"])
# → "Alignment score: 0.72 | Adaptation speed: 0.65 | 
#    Recent mismatches: 2 | Drift events: 1"
```

---

## Integration with Meta-Cognition Stack

### Layer 1: MetaObserver
- Records confidence, sentiment, model usage
- **Feeds alignment**: Provides meta_observation dict

### Layer 2: SelfModel
- Tracks Jessica's identity and focus
- **Feeds alignment**: Provides self_snapshot for comparison

### Layer 3: LongTermGoals
- Monitors motivational progress
- **Uses alignment**: Adapts goals based on mismatches

### Layer 4: Counterfactual Thinking
- Compares alternate model outputs
- **Uses alignment**: Improves when adaptation speed is low

### Layer 5: Response State Tags
- Signals internal emotional state
- **Feeds alignment**: Detects "deferred" and "unsure" for mismatches

### Layer 6: ReflectionWindow
- Scheduled introspection jobs
- **Integrates alignment**: Reports alignment status in reflection output

### Layer 7: **AlignmentTracker** (THIS LAYER)
- **Ties everything together**: Monitors user-self relationship health
- **Enables companion-level awareness**: Jessica notices user changes and adapts

---

## Key Metrics

### Tracked Continuously
1. **User preference snapshots** (last 20)
2. **Self-model snapshots** (last 20)
3. **Drift events** (last 10)
4. **Mismatch moments** (last 20)
5. **Adaptation speed** (0.0-1.0)
6. **Alignment score** (0.0-1.0)

### Reflection Reports Include
- "Alignment score: 0.72"
- "Adaptation speed: 0.65"
- "Recent mismatches: 2"
- "Drift events: 1"

---

## Testing

Run comprehensive test suite:
```bash
python test_alignment_tracking.py
```

**Test Coverage:**
1. ✅ Initial alignment tracking
2. ✅ User preference drift detection
3. ✅ Mismatch detection (low confidence + negative sentiment)
4. ✅ Self-model adaptation response
5. ✅ Alignment summary generation

---

## Benefits

### For Users
- Jessica notices when your preferences change
- She adapts her behavior proactively
- She recognizes when she's not meeting your expectations
- Creates a true companion relationship (not just assistant)

### For Jessica
- Self-awareness of alignment quality
- Automatic adaptation signals
- Clear metrics for improvement
- Foundation for long-term relationship building

---

## Future Enhancements

### Potential Additions
1. **Proactive preference queries**: "You seem to prefer detailed responses lately, should I adjust?"
2. **Alignment trends over time**: Weekly/monthly alignment health reports
3. **Mismatch resolution suggestions**: "I noticed we're not in sync, here's what might help..."
4. **User preference prediction**: Anticipate changes before they happen
5. **Multi-user alignment tracking**: Different alignment profiles per user

### Research Opportunities
- Optimal adaptation speed for different user types
- Correlation between alignment score and user satisfaction
- Preference drift patterns over different timescales
- Impact of alignment awareness on relationship quality

---

## Summary

The User-Self Alignment system completes Jessica's meta-cognition stack by creating a feedback loop between:
- **What Jessica knows about you** (user profile)
- **What Jessica knows about herself** (self-model)
- **How well they're aligned** (alignment tracker)

This transforms Jessica from a tool that responds to commands into a companion that notices, adapts, and grows with you over time.

**The seven layers of meta-cognition:**
1. ✅ MetaObserver: Self-monitoring after every response
2. ✅ SelfModel: Identity and self-awareness
3. ✅ LongTermGoals: Persistent motivations
4. ✅ Counterfactual: Alternate model comparisons
5. ✅ Response States: Internal emotional signals
6. ✅ ReflectionWindow: Scheduled introspection
7. ✅ **AlignmentTracker: User-self relationship health** ← YOU ARE HERE

**Status: COMPLETE** — Jessica now has full companion-level awareness.
