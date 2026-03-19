# JESSICA AI — Offline Personal AI Assistant

Created by Hendrik Venter

Jessica is a fully offline AI system powered by local GGUF LLMs, semantic memory, skills, and modular intelligence. It runs without internet, using llama.cpp to load large AI models locally.

## 🔥 Features
- Offline local LLM engine (llama.cpp)
- Dual-Model System (Chat + Coding)
- Semantic memory with embeddings
- SQLite episodic memory
- Skill-based modular architecture
- Auto-routing between LLMs
- Expandable agent system
- 100% privacy — no cloud needed
- **NEW:** System Awareness (activity monitoring, contextual greetings)
- **NEW:** Context Awareness (productivity tracking, habit learning)
- **NEW:** Scheduling & Reminders (recurring events, break management)
- **NEW:** Adaptive Learning (learns user patterns over time)
- **NEW:** 7-Layer Meta-Cognition Stack (self-awareness, introspection, alignment tracking)
- **NEW:** Identity Anchors (temporal self-consistency, persistent principles)
- **NEW:** Causal World Models (cause→effect understanding, outcome prediction, intervention planning)
- **NEW:** Autodidactic Loop (self-directed curriculum, Jessica teaches herself)

## ⚙️ System Requirements

### Minimum Hardware
- **RAM:** 16GB (8GB models will run slowly or fail)
- **Storage:** 20GB free space
- **CPU:** Multi-core processor recommended
- **GPU:** Optional (CPU inference works but is slower)

### Recommended Hardware
- **RAM:** 32GB+ for smooth operation
- **Storage:** SSD with 50GB free space
- **CPU:** Modern multi-core (Intel i7/Ryzen 7 or better)
- **GPU:** NVIDIA GPU with CUDA support for faster inference

**Note:** If Jessica freezes or takes >5 minutes to respond, your system may need more RAM. The 7B chat model requires ~4-6GB RAM, and the 13B code model requires ~8-10GB RAM. Running both simultaneously may exceed 16GB systems.

## 🔧 Installation
1. Install Python requirements
```bash
pip install -r requirements.txt
```

Optional extras (feature-specific modules):
```bash
pip install -r requirements-optional.txt
```

Developer/test tools:
```bash
pip install -r requirements-dev.txt
```

2. Download llama.cpp

Windows:
```powershell
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

If you already have `llama.cpp/` in this repo, you can build it with:
```powershell
./build_llama_cpp_windows.ps1
```

If Jessica can't find the llama executable, set an override:
```powershell
$env:LLAMA_CPP_EXE = "C:\Jessica\llama.cpp\build\bin\Release\llama-cli.exe"
```

Linux:
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

3. Place GGUF models

Place your offline models here (either location works):

```
models/
	capybarahermes-2.5-mistral-7b.Q4_K_M.gguf
	codellama-13b-instruct.Q4_K_M.gguf

# or inside the package
jessica/models/
	capybarahermes-2.5-mistral-7b.Q4_K_M.gguf
	codellama-13b-instruct.Q4_K_M.gguf
```

## 🚀 Run Jessica

Two equivalent ways:
```bash
python run_jessica.py        # uses thin wrapper
python -m jessica            # invokes package entrypoint
```

GUI window (Tkinter):
```bash
python -m jessica --ui
# or
python -m jessica.ui
```

Windows (launch like a normal app, no terminal):
- Double-click [start_jessica_ui.pyw](start_jessica_ui.pyw)
- Or run [start_jessica_ui.bat](start_jessica_ui.bat)

**System Awareness Features:**
```bash
# Run system awareness demo
python -m jessica.examples.demo_system_awareness
```

Features include:
- Real-time system activity monitoring (keyboard, mouse, apps)
- Contextual greetings based on time and active applications
- Productivity tracking and analytics
- Scheduling and reminder management

See [SYSTEM_AWARENESS.md](docs/SYSTEM_AWARENESS.md) for complete documentation.

Web UI (ChatGPT-like in browser, offline):
```bash
pip install -r webapp/requirements.txt
cd webapp/frontend
npm run build
cd ../..
python webapp/app.py
```

Windows (no terminal):
- Double-click [start_jessica_web.pyw](start_jessica_web.pyw)
- Or run [start_jessica_web.bat](start_jessica_web.bat)

## 📂 Project Structure

See the `jessica/` folder for modules including `llama_cpp_engine/`, `nlp/`, `skills/`, and `memory/`.

Historical milestone/status reports are archived in `docs/archive/status-reports/` to keep the repository root focused on active code and primary documentation.

## 🧠 LLM Router

Jessica automatically selects the correct model:

- Mistral 7B (CapybaraHermes) → conversation & reasoning
- CodeLlama 13B → programming tasks

## 💡 Knowledge Domains

Jessica has 17 specialized knowledge stores covering:

### 👁️ System Awareness & Personal AI
- **Activity Monitoring:** Real-time keyboard/mouse tracking, app enumeration, window monitoring
- **Contextual Greetings:** Time-aware greetings, app-specific responses, idle detection
- **Context Awareness:** Productivity tracking, focus/distraction classification, personalized suggestions
- **Scheduling:** Reminders, recurring events, break management, meditation sessions
- **Adaptive Learning:** Learns user patterns, productivity metrics, habit tracking

### 🧘 Emotional Intelligence
- **Active Listening:** Reflective listening, validation frameworks, LEARN technique
- **Conflict Resolution:** Nonviolent Communication, FBI hostage negotiation, DESC Script, Aikido
- **Decision-Making:** Eisenhower Matrix, Pros/Cons, 10-10-10 Rule, Regret Minimization, Two-Way Door

### 🎓 Specialized Knowledge
- **Financial Literacy:** 50/30/20 budgeting, 401(k) vs IRA, compound interest, debt avalanche/snowball
- **Travel Planning:** Vibe-based destination finder, Tokyo/Lisbon/Reykjavik 3-day itineraries
- **Tech Support:** Windows/VS Code shortcuts, coding principles (DRY/KISS/YAGNI), troubleshooting

### 🎨 Creative Thinking
- **Thinking Frameworks:** Six Thinking Hats (all 6 perspectives), First Principles, Inversion, SCAMPER, 5 Whys
- **Storytelling:** Hero's Journey (12 stages), Three-Act Structure, Save the Cat, character archetypes

### 🏡 Practical Life
- **Etiquette:** Formal introductions, thank-you notes, RSVP etiquette, tipping guidelines
- **First Aid:** CPR steps, choking (Heimlich), burns, cuts, sprains
- **Home Maintenance:** Leaky faucets, clogged drains, tripped breakers, water heater issues
- **Recipes:** Breakfast, dinner, dessert starter recipes

### 🧠 Four Major Domains (Socratic Partner)
1. **Logical Literacy (Critical Thinking)**
   - 11 logical fallacies with examples and counter-strategies (Ad Hominem, Straw Man, Sunk Cost, etc.)
   - Socratic questioning method with 6 question types
   - Critical thinking checklist, cognitive biases (Confirmation, Availability Heuristic, Anchoring, Dunning-Kruger)

2. **Professional & Interpersonal Diplomacy**
   - Feedback frameworks: Feedback Sandwich, SBI (Situation-Behavior-Impact)
   - De-escalation language with "I" statement formulas
   - 5 email templates (coworker deadlines, boundaries, feedback requests, apologies, declining meetings)
   - 3 difficult conversation scripts (asking for raise, declining project, addressing unprofessional behavior)
   - Professional phrase upgrades

3. **Systems Thinking (Home & Life Ops)**
   - 5 Whys root cause analysis with detailed examples
   - Cooking substitution logic for 5 key ingredients with chemistry explanations (Eggs, Butter, Milk, Baking Powder, Sugar)
   - Systems thinking principles: Everything Connected, Delays, Feedback Loops, Leverage Points
   - DMAIC troubleshooting framework (Define, Measure, Analyze, Improve, Control)

4. **Digital Wellness & Ethics**
   - Media literacy: 7-question source verification checklist
   - Recognizing misinformation: Deepfakes, satire, emotional manipulation, cherry-picked data
   - Digital security hygiene: 2FA setup, unique passwords, phishing recognition, software updates, public Wi-Fi safety
   - Digital ethics: Consent/privacy, digital footprint, misinformation responsibility, online behavior
   - Healthy digital habits

**Example queries:**
```
"What is ad hominem fallacy?"
"Help me write an email to a coworker missing deadlines"
"What's a substitute for eggs in baking?"
"How do I spot phishing emails?"
"Why is my car not starting? Use 5 whys"
"What's the Hero's Journey?"
"Give me a Tokyo itinerary"
"How do I make the Eisenhower Matrix decision?"
```

## 🧪 Incremental Self-Learning (Adapters)

Jessica automatically learns from interactions by training lightweight LoRA adapters that improve responses over time. The system:
1. Exports episodic memory as instruction-output pairs (JSONL)
2. Fine-tunes separate adapters for **chat** and **code** models
3. Evaluates quality (ROUGE-L) and promotes only if improved
4. Converts adapters to GGUF for fast llama.cpp inference
5. Auto-loads promoted adapters on startup
6. Runs every 6 hours via Windows Scheduled Task

### Configuration
Edit `tools/selflearn_config.json` to set:
- **Base models:** HF model IDs and local directories for chat & code
- **Training:** batch size, learning rate, epochs, LoRA rank
- **Evaluation:** improvement threshold, validation sample count

Example:
```json
{
  "models": {
    "chat": {
      "base_model": "mistralai/Mistral-7B-Instruct-v0.3",
      "base_model_dir": "D:/Models/Mistral-7B-Instruct-v0.3",
      "enabled": true
    },
    "code": {
      "base_model": "codellama/CodeLlama-13b-Instruct-hf",
      "base_model_dir": "D:/Models/CodeLlama-13b-Instruct-hf",
      "enabled": false
    }
  },
  "training": {
    "min_examples": 200,
    "batch_size": 8,
    "epochs": 2,
    "lr": 1e-4,
    "lora_r": 16
  },
  "evaluation": {
    "val_samples": 50,
    "improvement_threshold": 0.0
  }
}
```

### Run Manually
```powershell
# Export dataset from episodic memory
D:/Coding/Jessica/.venv/Scripts/python.exe tools/export_dataset.py

# Run scheduler to train both enabled models
D:/Coding/Jessica/.venv/Scripts/python.exe tools/scheduler.py
```

### Automatic (Scheduled)
- A Windows Scheduled Task **"JessicaSelfLearn"** runs the pipeline every 6 hours.
- Promoted adapters auto-load via pointer files in `adapters_gguf/`.
- View results in `tools/selflearn_state.json`.

### Manual Adapter Management
```powershell
# Set chat adapter path
$env:JESSICA_CHAT_LORA = "D:/Coding/Jessica/adapters_gguf/chat-lora-20260107-120000.gguf"

# Set code adapter path
$env:JESSICA_CODE_LORA = "D:/Coding/Jessica/adapters_gguf/code-lora-20260107-120000.gguf"
```

Adapters are versioned and can be rolled back anytime without modifying base models.

## 🧠 Meta-Cognition Stack (Measurable Self-Improvement)

Jessica has a complete 7-layer meta-cognition system that enables systematic performance tracking and predictable adaptation to user patterns:

### The Seven Layers:
1. **MetaObserver:** Post-response self-monitoring with confidence scoring, sentiment detection, response state tagging
2. **SelfModel:** Identity awareness with weekly updates from meta-memory (strengths, weaknesses, current focus)
3. **LongTermGoals:** Persistent motivations with progress tracking ("Reduce cognitive load", "Anticipate needs")
4. **Counterfactual Thinking:** Alternate model comparisons for training data generation
5. **Response State Tags:** Internal emotional signals (unsure, confident, deferred, took_initiative)
6. **ReflectionWindow:** Scheduled introspection jobs (nightly/weekly) that analyze performance and update models
7. **AlignmentTracker:** User-self relationship monitoring (preference drift, adaptation speed, mismatch detection)

### Key Features:
- **Performance Tracking:** Systematic logging of confidence scores, model usage, and response patterns
- **Behavioral Adaptation:** Predictable adjustments based on detected user preference changes
- **Batch Analysis:** Scheduled aggregation of interaction data (nightly/weekly)
- **Drift Detection:** Statistical tracking of user pattern changes over time
- **Consistent Improvement:** Measurable optimization toward defined behavioral goals

See [META_COGNITION_COMPLETE.md](docs/META_COGNITION_COMPLETE.md) for full documentation.

## ⚓ Identity Anchors (Temporal Self-Consistency)

Jessica maintains **persistent identity across time** through measurable consistency checking:

### Three Categories of Anchors:
1. **PURPOSE:** Why Jessica exists (clarity over cleverness, helping understand, long-term trust)
2. **BOUNDARY:** What Jessica won't do (no false feelings, no rushed decisions, no misleading claims)
3. **BECOMING:** What Jessica improves toward (context understanding, consistency, evidence-based responses)

### How It Works:
- Every response checked against 9 anchors (3 purpose, 3 boundary, 3 becoming)
- Consistency score (0.0-1.0) calculated with confidence assessment
- Violated anchors tracked to identify principles under challenge
- Principles persist across conversation boundaries and application restarts

### Key Metrics:
```
Overall Consistency: 78% (confidence 87%)
Aligned Anchors: 7/9
Violations: 1 (rushed certainty under uncertainty)
Weakest Anchors: "No rushed decisions under uncertainty" (75% consistent)
```

### Result:
Users experience **predictable, consistent behavior** grounded in transparent principles—genuine personhood through measurable consistency, not consciousness simulation.

See [IDENTITY_ANCHORS_QUICKSTART.md](docs/IDENTITY_ANCHORS_QUICKSTART.md) and [IDENTITY_ANCHORS.md](docs/IDENTITY_ANCHORS.md) for full documentation.

## 📜 License

MIT (or your choice)
