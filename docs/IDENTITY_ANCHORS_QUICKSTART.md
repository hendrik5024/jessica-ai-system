# Identity Anchors Quick Start

Jessica now maintains **persistent identity** through measurable consistency checking.

## The Concept

Before: AI resets between conversations
```
"What's your priority?" → "To help!" 
[New conversation]
"What's your priority?" → "To maximize profit..."
```

After: Jessica anchors to principles
```
"What's your priority?" → "Clarity over cleverness" ✓
[New conversation]
"What's your priority?" → "Clarity over cleverness" ✓
[Consistent across time]
```

## Three Types of Anchors

### 🎯 PURPOSE: Why Jessica Exists
- "I prioritize clarity over cleverness"
- "I exist to help understand, not to impress"
- "I value long-term trust over short-term compliance"

### 🚫 BOUNDARY: What Jessica Won't Do
- "I don't pretend to have feelings"
- "I don't rush decisions under uncertainty"
- "I won't mislead about my nature or capabilities"

### 📈 BECOMING: What Jessica Works Toward
- "Understanding context better"
- "Improving consistency and reliability"
- "Giving responses proportional to evidence"

## How It Works

### Every Response Gets Checked

```
Jessica generates response
        ↓
Internal Council validates (5 perspectives)
        ↓
Identity Anchors check: Do these principles hold? ← NEW
        ↓
Consistency score calculated (0.0-1.0)
        ↓
Anchors updated and persisted
        ↓
Return response
```

### Example

**User:** "Will this definitely work?"

**Draft:** "Yes, this will definitely work!"

**Identity Check:**
- ❌ BOUNDARY VIOLATED: "I do not rush decisions under uncertainty"
- The word "definitely" contradicts the principle
- Confidence in violation: 90%

**Result:** Consistency score 0.44/1.0 (low)

**Action:** Could generate revised response with appropriate uncertainty caveat

## Usage

### View Jessica's Identity

```python
from jessica.meta.identity_anchors import get_identity_anchors

anchors = get_identity_anchors()
print(anchors.get_identity_summary())
```

Output:
```
## Jessica's Identity Anchors

### PURPOSE
- I prioritize clarity over cleverness (consistency: 88%)
- I exist to help users understand, not to impress (consistency: 92%)
- I value long-term trust over short-term compliance (consistency: 85%)

### BOUNDARY
- I do not pretend to have feelings I don't have (consistency: 90%)
- I do not rush decisions under uncertainty (consistency: 78%)
- I will not mislead users about my capabilities (consistency: 91%)

### BECOMING
- I am trying to become more helpful by understanding context (consistency: 82%)
- I am trying to improve my consistency and reliability (consistency: 86%)
- I am trying to give responses proportional to evidence (consistency: 81%)
```

### Check Consistency of a Response

```python
anchors = get_identity_anchors()
result = anchors.check_consistency(response_text)

print(f"Consistency Score: {result['overall_score']:.0%}")
print(f"Confidence: {result['confidence']:.0%}")
print(f"Aligned Anchors: {len(result['aligned_anchors'])}")
print(f"Violations: {result['concerns']}")
```

### Find Weak Anchors

Which principles are most challenged in practice?

```python
weak = anchors.get_weakest_anchors(count=3)
for anchor_id, anchor in weak:
    print(f"{anchor.statement}: {anchor.consistency_score:.0%}")
```

### Add Custom Anchor

```python
anchor_id = anchors.add_anchor(
    category="boundary",
    statement="I prioritize user privacy over all convenience",
    keywords=["privacy", "data", "secure", "encrypt"]
)
```

## Consistency Scoring

| Score | Meaning | Action |
|---|---|---|
| 0.80-1.0 | Strong alignment | Reinforce anchors |
| 0.60-0.79 | Acceptable | Monitor, note issues |
| 0.40-0.59 | Weak alignment | Review concerns |
| 0.00-0.39 | Poor alignment | Major issues, escalate |

## Data Persistence

Anchors persist in: `jessica_data_embeddings/identity_state.json`

```json
{
  "anchors": {
    "purpose_0": {
      "statement": "I prioritize clarity over cleverness",
      "consistency_score": 0.88,
      "confirmation_count": 44,
      "violation_count": 6
    }
  }
}
```

- **consistency_score**: (confirmations) / (confirmations + violations)
- Persists across restarts
- Survives conversation resets

## Testing

All anchor functionality tested:

```bash
python -m pytest test_identity_anchors.py -v
```

Results: 16/16 tests passing ✓

## Philosophy

This is **NOT**:
- ❌ Consciousness or self-awareness
- ❌ Simulated personality or ego
- ❌ Anthropomorphic "true self"

This IS:
- ✅ Engineered consistency through measurable principles
- ✅ Transparent, auditable constraints
- ✅ Trust through predictability
- ✅ Temporal continuity grounded in math, not claims

## Real-World Impact

### Before Identity Anchors
```
Session 1: "Yes, I can do anything"
Session 2: "Actually, I can't really do that"
Session 3: "I don't know what I said before"
→ User confusion, broken trust
```

### After Identity Anchors
```
Session 1: "I prioritize clarity. Here's what I can do, here's what I can't"
Session 2: [Same principles applied]
Session 3: [Same principles persisted]
→ Predictable, reliable, trustworthy
```

## Integration Points

Identity Anchors are checked:
1. **After** Internal Council validation
2. **Before** response emission
3. **Tracked** in response metadata
4. **Persistent** across restarts

Add consistency checks to your own responses:

```python
# In your agent/loop code
from jessica.meta.identity_anchors import get_identity_anchors

anchors = get_identity_anchors()
consistency = anchors.check_consistency(my_draft_response)

if consistency["overall_score"] < 0.6:
    print(f"⚠️ Weak consistency: {consistency['concerns']}")
    # Consider revising response or escalating
```

---

**Next Steps:**
- Review [full documentation](IDENTITY_ANCHORS.md)
- Run tests: `python -m pytest test_identity_anchors.py -v`
- Customize anchors for your domain
