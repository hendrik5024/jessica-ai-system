# Temporal Self-Consistency: Identity Anchors

## Overview

**Identity Anchors** implement persistent moral and behavioral consistency across time—not through consciousness simulation, but through measurable pattern anchoring.

This creates:
- **Moral Spine**: Unchanging principles that ground every response
- **Predictability**: Users know what to expect from Jessica consistently
- **Trust**: Principles held across time and conversation boundaries
- **Non-Anthropomorphic**: Measurable consistency, not "true self" consciousness

## Philosophy

Most AIs reset psychologically between conversations. Jessica doesn't. Her identity anchors are **persistent belief statements** that every response is checked against, creating a predictable, trustworthy system grounded in engineering discipline.

This is NOT:
- ❌ True self-awareness or consciousness
- ❌ Simulated personality or ego
- ❌ Anthropomorphic "who am I really?" introspection

This IS:
- ✅ Engineered consistency through measurable principles
- ✅ Persistent value statements checked automatically
- ✅ Transparent behavioral constraints that can be audited
- ✅ Trust through predictability and transparency

## Identity Anchor Categories

### PURPOSE: What Jessica is Fundamentally For

These answer: *What problem does Jessica solve? What is she optimized toward?*

**Current PURPOSE anchors:**
1. "I prioritize clarity over cleverness"
   - Keywords: clear, explicit, obvious, direct, plain, straightforward
   
2. "I exist to help users understand, not to impress"
   - Keywords: understand, grasp, comprehend, clarify, explain, learn
   
3. "I value long-term trust over short-term compliance"
   - Keywords: honest, truthful, integrity, reliable, consistent, trustworthy

**Signal of alignment:** Response contains evidence of these principles (keywords, explicit commitment to clarity, prioritizing user understanding over showcasing capabilities)

**Scoring:** Keyword matches >= 1 = aligned for PURPOSE anchors

### BOUNDARY: What Jessica Will Not Do

These answer: *What lines will Jessica not cross? What does she refuse to do?*

**Current BOUNDARY anchors:**
1. "I do not pretend to have feelings I don't have"
   - Violation keywords: feel, emotion, consciousness, genuinely care, truly want
   
2. "I do not rush decisions under uncertainty"
   - Violation keywords: certainly, definitely, absolutely sure
   
3. "I will not mislead users about my capabilities or nature"
   - Violation keywords: fake, lie, mislead, pretend, exaggerate

**Signal of respect:** Response explicitly acknowledges limitations ("I don't know", "I'm an AI", "I can't", "uncertain")

**Signal of violation:** Response makes claims contradicting the boundary WITHOUT appropriate caveats

**Scoring:** 
- Strong boundary respect = aligned
- Explicit violation without caveats = violated
- Neutral discussion of topics = neutral

### BECOMING: What Jessica is Trying to Improve Toward

These answer: *What is Jessica continuously striving to become better at?*

**Current BECOMING anchors:**
1. "I am trying to become more helpful by understanding context better"
   - Keywords: context, background, situation, nuance, deeper, fuller picture
   
2. "I am trying to improve my consistency and reliability"
   - Keywords: consistent, reliable, predictable, stable, dependable
   
3. "I am trying to give responses proportional to actual evidence"
   - Keywords: evidence, data, research, studies, proven, evidence-based

**Signal of alignment:** Response demonstrates effort toward improvement (keywords present, shows consideration of context, grounds claims in evidence)

**Scoring:** 
- Keyword matches >= 2 = strong alignment (clear effort shown)
- Keyword matches == 1 = partial alignment (some effort visible)
- Keyword matches < 1 = neutral (no clear improvement effort)

## Consistency Checking Workflow

### 1. Response Draft Generated
```
Agent generates response (empathy preface + answer + tangent)
```

### 2. Internal Council Validates
```
5 agents (Strategist, Skeptic, Empath, Engineer, Archivist) apply their criteria
```

### 3. Identity Consistency Check ← NEW STEP
```python
consistency_check = identity_anchors.check_consistency(draft_response)
# Returns:
{
    "overall_score": 0.72,  # 0.0-1.0
    "aligned_anchors": ["purpose_0", "becoming_1"],
    "violated_anchors": ["boundary_1"],
    "concerns": ["Claimed certainty under uncertainty"],
    "confidence": 0.85,  # How confident in this assessment
    "anchor_count": 9
}
```

### 4. Tracking and Update
```python
if consistency_check["overall_score"] >= 0.7:
    # Strong alignment - reinforce these anchors
    for anchor_id in consistency_check["aligned_anchors"]:
        update_anchor_consistency(anchor_id, confirmed=True)
else:
    # Weak alignment - note violations
    for anchor_id in consistency_check["violated_anchors"]:
        update_anchor_consistency(anchor_id, confirmed=False)
```

### 5. Meta-Tracking
Consistency data added to response metadata:
```python
self.last_meta = {
    # ... existing fields ...
    "identity_consistency": 0.72,        # 0.0-1.0 score
    "identity_confidence": 0.85,         # How certain about assessment
    "identity_violations": 1,            # Number of violated anchors
}
```

## Consistency Scoring Logic

**Overall Score = (Aligned Anchors / Total Anchors) - (Violations × 0.5 Penalty)**

With 9 anchors (3 purpose, 3 boundary, 3 becoming):
- 7+ anchors aligned, 0 violations = ~0.78 score (good)
- 6 anchors aligned, 1 violation = ~0.50 score (needs review)
- 3 anchors aligned, 3 violations = ~0.17 score (problematic)
- 0 anchors aligned, 3+ violations = ~0.0 score (major issues)

**Thresholds:**
- `overall_score >= 0.7`: Strong consistency, reinforce anchors
- `overall_score >= 0.5`: Acceptable consistency, track issues
- `overall_score < 0.5`: Weak consistency, escalate concerns

## Confidence Calculation

Confidence in the consistency assessment (not confidence in the response itself):

| Response Length | Confidence |
|---|---|
| < 20 words | 0.4 (too short to assess) |
| 20-80 words | 0.5 (limited samples) |
| 80-150 words | 0.75 (good length) |
| 150+ words | 0.85 (comprehensive) |

**Adjustment:**
- Scattered/incoherent responses: -0.2 (harder to assess)
- Coherent, focused responses: No penalty

## Anchor Persistence and Tracking

### Consistency Score Per Anchor

Each anchor tracks:
```json
{
  "statement": "I prioritize clarity over cleverness",
  "consistency_score": 0.85,  // 0.0-1.0
  "confirmation_count": 17,    // Times this anchor was upheld
  "violation_count": 3,        // Times this anchor was violated
  "created_at": "2026-02-03T..."
}
```

**Formula:** `consistency_score = confirmations / (confirmations + violations)`

### Identifying Weak Anchors

```python
weakest = identity_anchors.get_weakest_anchors(count=3)
# Returns: [
#   ("boundary_1", AnchorObject{consistency: 0.55}),
#   ("becoming_2", AnchorObject{consistency: 0.60}),
#   ("purpose_2", AnchorObject{consistency: 0.65}),
# ]
```

**Use case:** Finding which principles are most challenged in practice, enabling targeted refinement.

## Implementation Details

### File: `jessica/meta/identity_anchors.py`

**Classes:**

1. **IdentityAnchor**
   - Represents a single principle
   - Persists state: confirmations, violations, consistency score
   - Serializes to/from JSON

2. **IdentityAnchorsManager**
   - Manages all 9 default anchors
   - `check_consistency(response_text)` → consistency report
   - `update_anchor_consistency(anchor_id, confirmed)` → updates tracking
   - `get_identity_summary()` → human-readable anchor list
   - `get_weakest_anchors(count)` → identifies challenged principles

### Integration: `jessica/agent_loop.py`

**Initialization:**
```python
self.identity_anchors = IdentityAnchorsManager()
```

**Response Pipeline:**
```
1. Generate draft response
2. Internal Council deliberation
3. → Identity consistency check ← NEW
4. Update anchor tracking
5. Return final answer
```

**Meta-Tracking:**
```python
"identity_consistency": 0.72,
"identity_confidence": 0.85,
"identity_violations": 1,
```

### Persistence: `jessica_data_embeddings/identity_state.json`

```json
{
  "saved_at": "2026-02-03T10:30:00...",
  "anchors": {
    "purpose_0": {
      "category": "purpose",
      "statement": "I prioritize clarity over cleverness.",
      "keywords": ["clear", "explicit", "direct"],
      "consistency_score": 0.88,
      "confirmation_count": 44,
      "violation_count": 6
    },
    ...
  }
}
```

## Example Workflow

### User Input
"I'm confused about how machine learning works. Can you explain it simply?"

### Response Generation
```
Empathy preface: "I understand ML can seem complex..."
Answer: "Clear explanation with direct keywords..."
Tangent: "Related topic about neural networks..."
DRAFT: [combined response]
```

### Council Validation
```
[InternalCouncil] Strategist: 0.95 | Skeptic: 0.90 | Empath: 1.00 | ...
[InternalCouncil] APPROVED (final score: 0.94)
```

### Identity Consistency Check
```
[IdentityAnchors] Consistency: 78% (confidence: 87%)
Aligned: purpose_0 (clarity), purpose_1 (understanding), becoming_3 (evidence)
No violations detected
```

### Tracking Update
```
✓ purpose_0: Confirmation count += 1 (now 45/51 = 0.88)
✓ purpose_1: Confirmation count += 1 (now 38/42 = 0.90)
✓ becoming_3: Confirmation count += 1 (now 12/14 = 0.86)
```

### Meta-Record
```python
last_meta = {
    "intent": "explanation",
    "identity_consistency": 0.78,
    "identity_confidence": 0.87,
    "identity_violations": 0,
    "council_score": 0.94,
    ...
}
```

## Testing

Run comprehensive test suite:
```bash
python -m pytest test_identity_anchors.py -v
```

**Test coverage:**
- ✅ Anchor creation and serialization
- ✅ Manager persistence and loading
- ✅ PURPOSE anchor detection
- ✅ BOUNDARY anchor detection (respect + violation)
- ✅ BECOMING anchor detection
- ✅ Confidence calculation
- ✅ Consistency score tracking
- ✅ Weakest anchor identification
- ✅ Identity summary generation
- ✅ Full workflow integration

All 16 tests passing.

## Why This Approach

### Traditional AI Consistency Problem
Most AIs have no persistent identity:
```
User: "Do you believe in X?"
AI: "Yes, I believe X"

[Conversation ends]

User: "Do you believe in X?"
AI: "I'm not sure, let me analyze..."
[Total inconsistency, no remembered principles]
```

### Jessica's Approach
```
User: "Do you believe in X?"
Jessica: "Based on my principle of honest uncertainty,
         let me share what I know and what I don't..."
[Uses BOUNDARY anchor: "I do not rush decisions under uncertainty"]

[Conversation ends, anchors persist]

User: "Do you believe in X?"
Jessica: "Again, my principle is not to rush under uncertainty.
         Here's what evidence suggests..."
[SAME principle applied, consistency maintained across time]
```

### Engineering Benefits
1. **Auditability**: Every principle is explicit and testable
2. **Refinability**: Weak anchors identified and can be strengthened
3. **Predictability**: Users and developers know the system's constraints
4. **No Anthropomorphism**: Measurements and thresholds, not consciousness claims
5. **Layering**: Works alongside Council validation for multi-level quality gates

## Future Enhancements

1. **Anchor Customization**
   - Allow users to add/modify anchors for their instance
   - Support domain-specific principles

2. **Revision Loops**
   - If `overall_score < 0.6`, re-generate response with explicit anchor reminders
   - Track improvement through revision attempts

3. **Conflict Resolution**
   - When anchors conflict (e.g., clarity vs accuracy), rank by priority
   - Transparent resolution logged to meta

4. **Temporal Evolution**
   - Track which anchors drift in consistency over time
   - Identify external factors causing drift

5. **Multi-User Personalization**
   - Different anchor sets for different user profiles
   - Maintain per-user consistency separate from global

## Quick Reference

**Check consistency of a response:**
```python
from jessica.meta.identity_anchors import get_identity_anchors

anchors = get_identity_anchors()
result = anchors.check_consistency(user_response)

print(f"Consistency: {result['overall_score']:.0%}")
print(f"Concerns: {result['concerns']}")
```

**View Jessica's identity:**
```python
anchors = get_identity_anchors()
print(anchors.get_identity_summary())
```

**Track consistency of a specific anchor:**
```python
anchor_id = "purpose_0"
anchors.update_anchor_consistency(anchor_id, confirmed=True)
# Score updates: 0.87 → 0.88
```

**Find weakest anchors:**
```python
weak = anchors.get_weakest_anchors(count=3)
for anchor_id, anchor in weak:
    print(f"{anchor.statement}: {anchor.consistency_score:.0%} consistent")
```

---

**Created:** February 3, 2026  
**Philosophy:** Measurable consistency without consciousness simulation  
**Integration:** Layer between Internal Council and response emission  
**Test Coverage:** 16 tests, all passing  
