# INTERNAL COUNCIL — Multi-Perspective Response Validation

## What This Is (And Isn't)

### NOT:
- ❌ Simulated personalities arguing
- ❌ Artificial consciousness with "internal thoughts"
- ❌ Multiple AIs having conversations
- ❌ Anthropomorphic "council of minds"

### IS:
- ✅ Systematic validation pipeline with specialized checks
- ✅ Multi-perspective quality gates before output
- ✅ Measurable criteria applied from different analytical angles
- ✅ Structured conflict resolution via weighted scoring

**This is quality assurance, not consciousness simulation.**

---

## Architecture

### The Five Validation Agents

Each agent applies specific, measurable criteria to draft responses:

| Agent | Role | Checks |
|-------|------|--------|
| **Strategist** | Long-term goal alignment | Response length, goal consistency, question answering |
| **Skeptic** | Logic & hallucination detection | Certainty language, weasel words, unsupported claims |
| **Empath** | Emotional tone appropriateness | User sentiment match, condescension, warmth |
| **Engineer** | Technical feasibility | Code syntax, path consistency, error handling |
| **Archivist** | Memory relevance | Past context usage, preference adherence, entity recognition |

+ **Observer** (existing MetaObserver) acts as arbitrator

---

## How It Works

### Flow:

```
1. Primary LLM drafts response
   ↓
2. InternalCouncil.deliberate(draft, context)
   ↓
3. Dynamic agent routing (based on intent)
   ↓
4. Each agent evaluates draft → (score, critique)
   ↓
5. Aggregate scores → final_score
   ↓
6. Observer arbitrates if scores conflict
   ↓
7. Approved response OR modification suggestions
   ↓
8. Response emitted (with council metadata)
```

### Dynamic Routing:

Not all agents run every time. Selection based on intent:

- **chat/advice** → Strategist + Empath
- **code** → Strategist + Skeptic + Engineer
- **If memory_used** → Add Archivist
- **Default minimum** → Strategist + Skeptic

---

## Agent Specifications

### 1. Strategist (Long-term Goal Alignment)

**Purpose:** Validates response serves user intent and active goals

**Criteria:**
- Response length appropriate for intent type
- Active goals respected (e.g., "Reduce cognitive load" → shorter responses)
- User questions clearly answered
- No tangents or off-topic content

**Scoring:**
```python
score = 1.0
if chat_intent and len(draft) > 400: score -= 0.2
if "Reduce cognitive load" in goals and len(draft) > 300: score -= 0.1
if question_unanswered: score -= 0.2
```

**Example critiques:**
- ✅ "Strategic alignment verified"
- ❌ "Somewhat verbose for chat"
- ❌ "User question not clearly answered"

---

### 2. Skeptic (Logic & Hallucination Detection)

**Purpose:** Catches weak logic, unsupported claims, overconfidence

**Criteria:**
- Certainty language matches confidence score
- No weasel words ("some say", "reportedly")
- Code provided with appropriate caveats
- No internal contradictions

**Scoring:**
```python
score = 1.0
if "definitely" in draft and confidence < 0.7: score -= 0.2
if "some say" in draft: score -= 0.15
if code_without_caveats and confidence < 0.8: score -= 0.1
```

**Example critiques:**
- ✅ "Logical consistency verified"
- ❌ "High certainty language ('definitely') with low confidence"
- ❌ "Vague attribution ('some say') suggests weak support"

---

### 3. Empath (Emotional Alignment)

**Purpose:** Ensures tone matches user sentiment and avoids condescension

**Criteria:**
- Cheerfulness matches user sentiment (not cheerful if user frustrated)
- Acknowledgment of difficulty when user is negative
- No condescending language ("just", "obviously", "simply")
- Appropriate warmth for positive interactions

**Scoring:**
```python
score = 1.0
if user_frustrated and "awesome!" in draft: score -= 0.2
if user_negative and no_acknowledgment: score -= 0.1
if condescending_word in draft: score -= 0.15
```

**Example critiques:**
- ✅ "Emotional alignment verified"
- ❌ "Cheerful tone ('awesome!') mismatched with user frustration"
- ❌ "Potentially condescending language ('just')"

---

### 4. Engineer (Technical Feasibility)

**Purpose:** Validates code correctness and technical accuracy

**Criteria:**
- Python syntax errors (missing colons, improper indentation)
- Path separator consistency (\\ vs /)
- Commands properly formatted as code blocks
- Error handling mentioned if user mentioned errors

**Scoring:**
```python
score = 1.0
if python_function_missing_colon: score -= 0.3
if mixed_path_separators: score -= 0.1
if command_not_formatted: score -= 0.1
if no_error_handling_when_needed: score -= 0.15
```

**Example critiques:**
- ✅ "Technical feasibility verified"
- ❌ "Python function definition missing colon"
- ❌ "Mixed path separators (use one style)"

---

### 5. Archivist (Memory Relevance)

**Purpose:** Ensures past context and preferences are respected

**Criteria:**
- Relevant memory referenced when available
- User preferences adhered to (verbosity, formality)
- Known entities used instead of generic references
- No contradiction of past statements

**Scoring:**
```python
score = 1.0
if memory_available_but_not_used: score -= 0.1
if verbose_despite_concise_preference: score -= 0.15
if generic_reference_when_entity_known: score -= 0.05
```

**Example critiques:**
- ✅ "Memory usage verified"
- ❌ "Relevant memory available but not referenced"
- ❌ "Response verbose despite user concise preference"

---

## Consensus Mechanism

### Approval Logic:
```python
approved = all(agent_score >= agent.threshold for agent in active_agents)
final_score = mean(all_agent_scores)
```

**Thresholds:**
- Strategist: 0.6
- Skeptic: 0.7
- Empath: 0.65
- Engineer: 0.7
- Archivist: 0.6

### Conflict Resolution:

If agents disagree (some approve, some don't):
1. Calculate weighted final_score
2. Observer (MetaObserver) provides tie-breaker based on:
   - Confidence score
   - User sentiment
   - Historical pattern
3. If final_score ≥ 0.7 → Approve with notation
4. If final_score < 0.7 → Suggest modifications

---

## Integration

### In agent_loop.py:

```python
# After LLM generates draft response
council_context = {
    "intent": intent,
    "user_text": text,
    "confidence": 0.7,
    "user_sentiment": self._sentiment_label(text),
    "memory_used": bool(semantic_hits),
    "active_goals": [g.get("goal") for g in self.goals.load().get("goals", [])],
}

deliberation = self.council.deliberate(draft_response, council_context)

print(f"[InternalCouncil] {deliberation['consensus']}")

# Log in meta-observation
self.last_meta["council_score"] = deliberation["final_score"]
self.last_meta["council_agents"] = deliberation["active_agents"]
```

---

## Testing Results

```bash
python test_internal_council.py
```

**All tests passing:**
- ✅ Strategist detects verbosity, unanswered questions
- ✅ Skeptic catches overconfident language, weasel words
- ✅ Empath identifies tone mismatches, condescension
- ✅ Engineer finds syntax errors, path inconsistencies
- ✅ Archivist validates memory usage, preference adherence
- ✅ Full council deliberation with dynamic routing

---

## Example Deliberations

### Example 1: Good Response (Approved)
```
Draft: "Here's a concise answer to your question."
Context: {intent: "chat", user_sentiment: "neutral"}

Active Agents: Strategist, Empath
Strategist: 1.00 — Strategic alignment verified
Empath: 1.00 — Emotional alignment verified
Final Score: 1.00
Consensus: Approved
```

### Example 2: Problematic Response (Flagged)
```
Draft: "This is definitely correct and will always work."
Context: {intent: "code", confidence: 0.45, user_sentiment: "frustrated"}

Active Agents: Strategist, Skeptic, Engineer
Strategist: 1.00 — Strategic alignment verified
Skeptic: 0.80 — High certainty language with low confidence
Engineer: 0.85 — No error handling discussed
Final Score: 0.88
Consensus: Approved with reservations
Modifications: Add caveats or reduce certainty language
```

---

## Performance Impact

- **Per-deliberation overhead:** ~3-8ms
- **Agents run:** 2-5 (dynamic)
- **Memory:** Minimal (no extra models loaded)
- **Blocking:** Yes (deliberation before response emission)

**Total response time increase:** ~5-10ms (negligible)

---

## Future Enhancements

### Phase 1 (Implemented):
- ✅ Multi-perspective validation
- ✅ Dynamic agent routing
- ✅ Consensus scoring
- ✅ Critique logging

### Phase 2 (Future):
- ⏳ **Revision loop:** Auto-regenerate if approval fails
- ⏳ **Learning:** Track which critiques correlate with user satisfaction
- ⏳ **Custom agents:** User-defined validation criteria
- ⏳ **Agent weights:** Adjust importance based on user priorities

### Phase 3 (Research):
- ⏳ **Confidence calibration:** Use council disagreement to calibrate confidence scores
- ⏳ **Training data:** Generate preference examples from council critiques
- ⏳ **A/B testing:** Compare responses with/without council validation

---

## Key Metrics

Tracked in meta_observations:
```python
{
  "council_score": 0.88,  # Aggregate approval score
  "council_agents": ["strategist", "skeptic", "engineer"],  # Active validators
}
```

Available for analysis:
- Which agents flag responses most often?
- Which agent scores correlate with user satisfaction?
- Are certain intents consistently flagged?
- Do council scores predict MetaObserver confidence?

---

## Philosophical Grounding

This system adheres to the META_COGNITION_PHILOSOPHY principles:

1. **Measurable criteria:** Every agent uses quantifiable thresholds
2. **No anthropomorphism:** Agents are validation functions, not personalities
3. **Predictable behavior:** Same input → same scores
4. **Systematic improvement:** Critiques enable targeted refinement

**We're building quality assurance, not simulated consciousness.**

---

## Summary

The Internal Council system adds **multi-perspective validation** without falling into anthropomorphism:

- **NOT** simulated internal dialogue
- **IS** systematic quality gates from different analytical perspectives

Each "agent" is simply a specialized validation function applying measurable criteria. The "council" is a batch validation pipeline with dynamic routing.

**This is engineering, not theater.**

See [META_COGNITION_PHILOSOPHY.md](META_COGNITION_PHILOSOPHY.md) for philosophical grounding.

---

**Status:** ✅ IMPLEMENTED AND TESTED
**Integration:** ✅ Live in AgencyLoop
**Performance:** ✅ Minimal overhead (<10ms)
**Philosophy:** ✅ Grounded in measurable validation
