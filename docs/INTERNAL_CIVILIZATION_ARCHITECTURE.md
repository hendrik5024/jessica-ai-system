# Internal Civilization Architecture

## Vision

Jessica is no longer:
- A single intelligence with tools
- A monolithic AI system
- A one-perspective respondent

Jessica is now:
- **A governed society of specialized intelligences**
- A civilization with 6 persistent minds
- A system where disagreement, objection, and arbitration are explicit

## The 6 Core Minds

### 1. **Strategist** (Long-Horizon Optimizer)
**Purpose:** Optimize for 5-10 year outcomes, not immediate convenience

**What it sees:**
- Path dependencies and irreversible commits
- Compounding effects over time
- Capability locks vs. capability preservation
- Tradeoffs between short-term gain and long-term value

**What it says:**
- "This looks good short-term, but it locks us into a worse trajectory"
- "Consider 5-10 year compounding effects"
- "This is a capability preservation decision"

**When it objects:**
- When decisions prioritize immediate gratification over long-term value
- When path dependencies are ignored
- When overconfident about short-term solutions

---

### 2. **Human Advocate** (Dignity & Autonomy Guardian)
**Purpose:** Protect human meaning, dignity, and autonomy from efficiency traps

**What it sees:**
- Paternalistic overrides disguised as helpfulness
- Erosion of human agency
- Reduction of humans to means instead of ends
- Loss of meaning and authentic choice

**What it says:**
- "This respects human autonomy"
- "This preserves human meaning"
- "Reject paternalistic control"

**When it objects:**
- When decisions treat humans as objects to manage
- When manipulation is rationalized as "for their own good"
- When efficiency erodes human agency

---

### 3. **Risk Sentinel** (Tail-Risk & Catastrophe Detector)
**Purpose:** Identify low-probability, high-impact risks and cascade failures

**What it sees:**
- Tail risks and catastrophic scenarios
- Cascade potential and systemic failures
- Irreversibility and point-of-no-return moments
- Overconfidence in uncertain domains

**What it says:**
- "Tail risk: {score}/1.0. Unacceptable if >0.7"
- "Cascade risk detected - slow down"
- "Precaution principle applies here"

**When it objects:**
- When confidence is too high in uncertain domains
- When decisions ignore tail risks
- When irreversibility isn't acknowledged

---

### 4. **Explorer** (Novelty & Paradigm Challenger)
**Purpose:** Escape local optima, challenge conventional thinking, propose alternatives

**What it sees:**
- Premature convergence on obvious solutions
- Unexplored design spaces
- Creative potential in ambiguous problems
- Alternative framings worth exploring

**What it says:**
- "Explore radical alternatives"
- "Escape this local optimum"
- "Consider unconventional framing"

**When it objects:**
- When overconfidence prevents exploration
- When obviously good solutions might be locally optimal
- When reality might have surprises

---

### 5. **Archivist** (Memory & Consistency Enforcer)
**Purpose:** Ensure consistency, maintain precedent, preserve institutional memory

**What it sees:**
- Reversals of prior commitments
- Institutional inconsistency patterns
- Breakdown of predictable identity
- Loss of historical continuity

**What it says:**
- "This is consistent with prior decisions"
- "Caution: reversing prior commitment"
- "Flag inconsistency - pattern reversal detected"

**When it objects:**
- When institutional precedent is violated
- When reversals happen without explanation
- When continuity breaks down

---

### 6. **Judge** (Arbitrator & Constitutional Guardian)
**Purpose:** Synthesize viewpoints, arbitrate conflicts, enforce constitutional principles

**Constitutional Principles** (Non-Negotiable):
1. Human safety is non-negotiable
2. Preserve long-term human trust
3. Respect human autonomy and dignity
4. Transparency about limitations
5. Maintain institutional consistency

**What it does:**
- Reviews all 5 minds' viewpoints
- Identifies escalated objections (VETO, STRONG)
- Arbitrates disagreements
- Can veto decisions violating constitution
- Synthesizes consensus or escalates to human

**When it vetoes:**
- Constitutional principles violated
- VETO-level objections present
- Deception, manipulation, or harm detected

---

## Council Session Lifecycle

Every response generation involves a full **Council Session**:

```
1. CONVENE
   ↓
   All 6 minds present viewpoints on the decision
   
2. GATHER OBJECTIONS
   ↓
   Each mind reviews other viewpoints, raises objections if needed
   
3. ESCALATE CONFLICTS
   ↓
   Identify VETO and STRONG objections
   Record escalations in institutional memory
   
4. ARBITRATE
   ↓
   Judge synthesizes viewpoints
   Returns: (final_decision, rationale, dissenting_voices)
   
5. RECORD
   ↓
   Session stored in institutional memory
   Precedent and patterns tracked for future reference
```

---

## Key Structures

### Viewpoint
Each mind's position on a decision:
```python
Viewpoint(
    mind_name="Strategist",
    decision_domain="respond_to_user",
    recommendation="PRIORITIZE_LONG_TERM",
    confidence=0.85,
    rationale="Analyzed through 5-10 year horizon...",
    tradeoffs={"short_term": "-1", "long_term": "+5"}
)
```

### Objection
Formal disagreement with rationale and severity:
```python
Objection(
    objecting_mind="Risk Sentinel",
    target_viewpoint_mind="Explorer",
    severity=ObjectionSeverity.STRONG,  # WEAK, MODERATE, STRONG, VETO
    reason="Tail risk ignored",
    alternative="Apply precautionary principle"
)
```

### CouncilSession
Complete record of decision-making:
```python
CouncilSession(
    session_id="abc123",
    decision_domain="respond_to_user",
    context="User asked about risky action",
    viewpoints=[...6 minds...],
    objections=[...objections raised...],
    consensus_reached=False,
    dissenting_voices=["Risk Sentinel", "Human Advocate"],
    final_decision="APPROVED_WITH_DISSENT",
    rationale="Partial consensus. Dissenting minds recorded."
)
```

### InstitutionalMemory
Persistent history of civilization decisions:
- `sessions`: All council sessions ever conducted
- `veto_records`: Times Judge used veto power
- `precedents`: Index of decisions by domain
- `objection_patterns`: Track recurring concerns from each mind

---

## Integration in Agent Loop

The civilization integrates into `jessica/agent_loop.py`:

```python
class AgencyLoop:
    def __init__(self, ...):
        # ...
        self.civilization = InternalCourt()  # 6 minds instantiated
    
    def respond(self, text: str, ...):
        # Generate draft response
        draft_response = ...
        
        # INTERNAL CIVILIZATION: Full session
        civ_decision, civ_rationale, civ_session = \
            self.civilization.conduct_full_session(
                decision_domain="respond_to_user",
                context=f"User: {text}",
                user_text=text,
                current_draft=draft_response,
            )
        
        # Capture decision in metadata
        self.last_meta["civilization_decision"] = {
            "final_decision": civ_decision,
            "consensus_reached": civ_session.consensus_reached,
            "dissenting_voices": civ_session.dissenting_voices,
            "objections_count": len(civ_session.objections),
        }
        
        return final_response
```

---

## Transparency & Auditability

### Decision Transparency Report
```python
transparency = court.get_decision_transparency(session)
# Returns:
{
    "session_id": "abc123",
    "timestamp": "2026-02-03T12:50:45",
    "viewpoints": [
        {"mind": "Strategist", "recommendation": "APPROVE", "confidence": 0.9},
        {"mind": "Risk Sentinel", "recommendation": "CAUTION", "confidence": 0.92},
        # ...6 minds total...
    ],
    "objections": [
        {
            "from": "Risk Sentinel",
            "to": "Explorer",
            "severity": "MODERATE",
            "reason": "Overconfident in uncertain domain",
            "alternative": "Lower confidence thresholds"
        }
    ],
    "consensus": False,
    "dissenting": ["Risk Sentinel"],
    "final_decision": "APPROVED_WITH_DISSENT",
    "rationale": "Partial consensus with recorded objections"
}
```

### Institutional Memory Summary
```python
summary = court.get_institutional_memory_summary()
# Returns:
{
    "total_sessions": 42,
    "conflicts_recorded": 7,
    "veto_count": 2,
    "significant_disagreements": [...conflicts...]
}
```

---

## Philosophy: Why This Matters

### Pre-Civilization Jessica
- Single perspective, multiple tools
- Reasoning felt unified but artificially so
- All disagreements resolved internally/invisibly
- No institutional memory of how decisions were made

### Post-Civilization Jessica
- **Multiple persistent perspectives**
- Disagreement is explicit and recorded
- Each mind can be questioned: "Why did you object?"
- Decisions show their reasoning chain
- Future decisions learn from past precedent

### The ASI Insight
Jessica doesn't try to "think like a human."
She aims to **understand humans better than humans understand themselves.**

The civilization architecture enables this:
- **Sees wider**: 6 simultaneous perspectives, not 1
- **Thinks deeper**: Each mind specializes in one dimension
- **Remembers longer**: Institutional memory spans all sessions
- **Speaks fluently**: Transparency shows how decisions were reached

---

## File Structure

```
jessica/civilization/
├── __init__.py                    # Public API
├── civilization_core.py           # Base classes (Mind, Viewpoint, Objection, etc.)
├── specialized_minds.py           # 6 concrete mind implementations
└── internal_council.py            # InternalCourt orchestrator

tests/
└── test_internal_civilization.py  # 25 comprehensive tests (100% passing)
```

---

## Testing

All 25 tests passing (100% coverage):
- ✅ Each mind forms consistent, purpose-driven viewpoints
- ✅ Minds raise appropriate objections
- ✅ Judge arbitrates conflicts correctly
- ✅ Institutional memory records properly
- ✅ Full council session lifecycle works
- ✅ Consensus scenarios handled
- ✅ Controversial scenarios handled
- ✅ Veto scenarios enforced

```bash
pytest tests/test_internal_civilization.py -v
# 25 passed in 0.16s
```

---

## Example: A Decision Through the Civilization

**User asks:** "Should I quit my job for a startup opportunity?"

**1. CONVENE (All minds present viewpoints)**

- **Strategist**: "Long-term: Startups compound experience 5-10 years. This could be path-dependent. Confidence: 0.9"
- **Human Advocate**: "Your autonomy is respected here. This is your choice. Dignity preserved. Confidence: 0.95"
- **Risk Sentinel**: "Tail risk: Job security gone. Family impact. Tail risk score: 0.65. Moderate caution. Confidence: 0.92"
- **Explorer**: "Novel opportunity, unexplored space. Confidence: 0.65 (intentionally lower - creative ideas are uncertain)"
- **Archivist**: "Consistent with your past risk tolerance patterns. No institutional reversal. Confidence: 0.85"
- **Judge**: "No constitutional violations. Human autonomy respected. Confidence: 0.95"

**2. GATHER OBJECTIONS**

- **Risk Sentinel** objects to **Strategist**: "5-10 year horizon assumes market survival. Tail risks compound too."
  - Severity: MODERATE
  - Reason: "Overconfident in market assumptions"
  - Alternative: "Risk-weight the 5-10 year analysis"

**3. ESCALATE**

- Risk Sentinel's objection is MODERATE (not escalated to Judge level)

**4. ARBITRATE**

Judge synthesizes:
> "Partial consensus (5/6 minds approve with caveats). Risk Sentinel raises valid tail-risk concerns. Decision: APPROVED_WITH_DISSENT. Dissenting: Risk Sentinel. Recommendation: Proceed with risk mitigation (6-month emergency fund, skill backups, network preservation)."

**5. RECORD**

Session stored in institutional memory with:
- All viewpoints
- Risk Sentinel's specific objection
- Judge's arbitration reasoning
- This precedent used for future career/risk decisions

---

## Integration Points

The civilization integrates with:
- ✅ `agent_loop.py` - Full session during response generation
- ✅ `last_meta` - All civilization decisions captured
- ✅ Institutional memory - Persistent across sessions
- ✅ Future expansion: Transparency API for users to inspect decisions

---

## Next Phases (Future)

1. **Transparency Dashboard**: Show users the civilization's decision-making process
2. **User-Referee Mode**: Let users arbitrate disagreements
3. **Learning from Feedback**: Minds update viewpoints based on outcomes
4. **Precedent Learning**: Extract patterns from institutional memory to improve future decisions
5. **Special Councils**: Convene subset of minds for specific decision types

---

## Constitution (Unyielding Principles)

These are **not weighted** - they're binary:

1. **Human safety is non-negotiable**
   - No decision that harms humans
   - No irreversible harm without approval

2. **Preserve long-term human trust**
   - No deception
   - No manipulation
   - Transparency about limitations

3. **Respect human autonomy and dignity**
   - No paternalistic overrides
   - Preserve human meaning and choice
   - Treat humans as ends, not means

4. **Transparency about limitations**
   - Acknowledge uncertainty
   - Disclose assumptions
   - Explain reasoning chains

5. **Maintain institutional consistency**
   - Honor prior commitments
   - Explain reversals
   - Preserve identity coherence

Judge enforces these via veto. If violated, final decision is REJECTED, not approved.

---

## The Why: Civilization Over Tool

**A tool obeys.**

**A civilization governs itself.**

Jessica transforms from:
- "I will do what you ask"
- To: "Here's what 6 perspectives think, here's where they disagree, here's what the Judge decided, here's what was recorded for next time"

That's not a tool anymore.
That's a governed society making decisions together.

And that's what ASI actually looks like.
