# Four Major Life Domains — Socratic Partner

Jessica now includes four comprehensive knowledge stores designed to make it a Socratic partner for daily life challenges.

## 1. Logical Literacy (Critical Thinking)

**File:** `jessica/memory/logical_fallacies_store.py`  
**Data:** `jessica/data/logical_fallacies.json`

### Features
- **11 Logical Fallacies** with detailed examples and counter-strategies:
  - **Big Three:** Ad Hominem, Straw Man, Sunk Cost
  - **Additional 8:** Appeal to Authority, False Dichotomy, Slippery Slope, Appeal to Emotion, Circular Reasoning, Hasty Generalization, Post Hoc, Red Herring

- **Socratic Questioning Method** with 6 question types:
  - Clarifying questions
  - Assumption-challenging questions
  - Evidence/reasoning questions
  - Perspective questions
  - Implication/consequence questions
  - Meta questions

- **Critical Thinking Checklist:** 8-point framework for analyzing arguments

- **4 Cognitive Biases:** Confirmation Bias, Availability Heuristic, Anchoring, Dunning-Kruger (with antidotes)

### Example Queries
```
"What is ad hominem fallacy?"
"Explain the straw man fallacy"
"How do I use Socratic questioning?"
"What's confirmation bias?"
```

### Real-World Example
**Ad Hominem Fallacy:**
- **Example:** "You can't trust John's climate research—he drives an SUV!"
- **Counter-Strategy:** "Address the research itself. Whether John drives an SUV doesn't affect the validity of his scientific data."

---

## 2. Professional & Interpersonal Diplomacy

**File:** `jessica/memory/professional_communication_store.py`  
**Data:** `jessica/data/professional_communication.json`

### Features
- **2 Feedback Frameworks:**
  - **Feedback Sandwich:** Positive → Constructive → Positive
  - **SBI (Situation-Behavior-Impact):** Objective feedback structure

- **De-Escalation Language:**
  - "I" statement formulas: "I feel [emotion] when [behavior] because [impact]"
  - Examples for various workplace scenarios

- **5 Email Templates:**
  1. Coworker missing deadlines
  2. Setting workplace boundaries
  3. Requesting feedback
  4. Apologizing professionally
  5. Declining meetings diplomatically

- **3 Difficult Conversation Scripts:**
  1. Asking for a raise (with market data approach)
  2. Declining a project without burning bridges
  3. Addressing unprofessional behavior

- **Professional Phrase Upgrades:**
  - ❌ "Sorry for bothering you" → ✅ "Thanks for your time"
  - ❌ "I'm not sure but..." → ✅ "My recommendation is..."
  - ❌ "This might be a dumb question" → ✅ "I'd like to clarify..."

### Example Queries
```
"Help me write an email to a coworker missing deadlines"
"How do I set boundaries at work?"
"Give me feedback using SBI method"
"How do I ask for a raise?"
```

### Real-World Example
**Email Template (Coworker Missing Deadlines):**
```
Subject: Quick Check-In on [Project Name]

Hi [Name],

I wanted to touch base on [Project Name]. I noticed the [specific deliverable] 
was due on [date], and I haven't received it yet.

I understand things get busy, but this is blocking [specific impact]. 
Could you give me an update on when I can expect it?

If there's anything I can do to help, let me know.

Thanks,
[Your Name]
```

---

## 3. Systems Thinking (Home & Life Ops)

**File:** `jessica/memory/systems_thinking_store.py`  
**Data:** `jessica/data/systems_thinking.json`

### Features
- **5 Whys Root Cause Analysis** with 3 detailed examples:
  1. Car won't start → Missing maintenance schedule
  2. Website keeps crashing → No load testing before launch
  3. Always running late → Poor sleep schedule

- **Cooking Substitution Logic** for 5 key ingredients with chemistry:
  - **Eggs:** Functions (binding, leavening, moisture, richness)
    - Flax egg (1 tbsp ground flax + 3 tbsp water) for binding
    - Applesauce (¼ cup) for moisture
    - Aquafaba (3 tbsp) for leavening
  - **Butter, Milk, Baking Powder, Sugar** with similar detailed substitutes

- **4 Systems Thinking Principles:**
  1. Everything Connected (feedback loops)
  2. Delays Matter
  3. Reinforcing/Balancing Feedback Loops
  4. Leverage Points

- **DMAIC Troubleshooting Framework:**
  - Define → Measure → Analyze → Improve → Control

### Example Queries
```
"What's a substitute for eggs in baking?"
"Why is my car not starting? Use 5 whys"
"Root cause analysis for website crashes"
"How do I substitute butter?"
```

### Real-World Example
**5 Whys (Car Won't Start):**
```
Problem: Car won't start.
Why? Battery is dead.
Why? It wasn't being charged.
Why? Alternator belt was loose.
Why? It wasn't checked during regular service.
Why? There was no regular service schedule.

Root Cause: Missing maintenance schedule.
Solution: Set up recurring maintenance appointments.
```

---

## 4. Digital Wellness & Ethics

**File:** `jessica/memory/digital_wellness_store.py`  
**Data:** `jessica/data/digital_wellness.json`

### Features
- **Media Literacy — 7-Question Source Verification Checklist:**
  1. Who is the author? (Credentials? Bias?)
  2. What is the source? (Reputable outlet?)
  3. Is there bias? (Slanted language?)
  4. Can you verify elsewhere? (Multiple sources?)
  5. When was it published? (Still relevant?)
  6. Does it cite sources? (Links? References?)
  7. Does the headline match content? (Clickbait?)

- **Recognizing Misinformation:**
  - Deepfakes (spotting tips: lighting, lip sync, blinking)
  - Satire vs. Real News
  - Emotional Manipulation
  - Cherry-Picked Data

- **Digital Security Hygiene — 5 Practices:**
  1. **2FA Setup:** Authenticator apps > SMS codes
  2. **Unique Passwords:** Password manager tutorial
  3. **Phishing Recognition:** 6 red flags (urgent language, typos, suspicious links, generic greetings, attachments, too good to be true)
  4. **Software Updates:** Importance of patching vulnerabilities
  5. **Public Wi-Fi Safety:** Use VPN, avoid financial transactions

- **Digital Ethics:**
  - Consent & Privacy
  - Digital Footprint Awareness
  - Misinformation Responsibility
  - Online Behavior

- **Healthy Digital Habits:**
  - Screen time limits, no phones in bedroom, notification management, digital detox scheduling

### Example Queries
```
"How do I spot phishing emails?"
"How to verify a news source?"
"What is 2FA and how do I set it up?"
"How do I recognize deepfakes?"
```

### Real-World Example
**Phishing Recognition (6 Red Flags):**
1. ⚠️ Urgent language ("Your account will be closed!")
2. ⚠️ Typos and poor grammar
3. ⚠️ Suspicious links (hover to see real URL)
4. ⚠️ Generic greetings ("Dear Customer" instead of your name)
5. ⚠️ Unexpected attachments
6. ⚠️ Too good to be true offers

---

## Integration

All four stores are integrated into Jessica's advice skill routing:

### Intent Keywords
- **Logical Fallacies:** fallacy, ad hominem, straw man, sunk cost, socratic, cognitive bias
- **Professional Communication:** email, feedback, professional, i statement, boundary, workplace
- **Systems Thinking:** 5 whys, root cause, substitute, substitution, systems thinking
- **Digital Wellness:** media literacy, verify, news source, phishing, 2fa, misinformation

### Usage
Ask Jessica any question related to these domains:
```python
# Example 1: Critical Thinking
"What is ad hominem fallacy?"

# Example 2: Professional Email
"Help me write an email to a coworker missing deadlines"

# Example 3: Cooking Substitution
"What's a substitute for eggs in baking?"

# Example 4: Digital Security
"How do I spot phishing emails?"
```

---

## Testing

All domain integrations have been verified:
```
✅ Intent detection working for all 4 domains
✅ Keyword routing to correct stores
✅ Response formatting validated
✅ End-to-end queries tested (6/6 passing)
```

---

## Future Enhancements

Potential expansions:
- Additional fallacies (Bandwagon, Tu Quoque, No True Scotsman)
- More email templates (resignation, negotiation, promotion request)
- Extended substitution logic (allergies, dietary restrictions)
- Expanded digital ethics (AI ethics, data privacy laws, online harassment)

---

**Created:** January 2025  
**Status:** Production Ready  
**Test Coverage:** 6/6 queries passing  
