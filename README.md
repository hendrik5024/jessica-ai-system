# Jessica AI — Offline Autonomous Multi-Agent System

Jessica is a fully offline, multi-agent AI system designed for reasoning, decision support, and real-world workflow automation.

Built to operate without cloud dependencies, Jessica combines local LLMs, semantic memory, and modular intelligence into a single autonomous system.

> ⚡ Built as a foundation for autonomous AI systems that operate in real-world environments.

---

## 🚀 Key Features

* Multi-agent “Council of Experts” architecture
* Fully offline (100% private, no cloud)
* Dual-model routing (chat + coding)
* Semantic + episodic memory system
* Self-learning via LoRA adapters
* Advanced meta-cognition and self-reflection
* Modular skill-based architecture

---

## 🧠 Architecture Overview

Jessica is structured as a modular system:

* `core/` → reasoning engine
* `jessica/` → orchestration layer
* `memory/` → learning + persistence
* `tools/` → integrations + utilities
* `config/` → system configuration
* `tests/` → validation and testing

---

## 🧭 System Flow

![Jessica Architecture](docs/architecture.png)

---

## 💬 Example Interaction

**User:**
"Help me optimize my daily workflow"

**Jessica:**

* Analyzes past activity patterns
* Identifies productivity bottlenecks
* Suggests schedule improvements
* Sets reminders and break intervals

**Result:**
Personalized, adaptive workflow optimization

---

## 🎯 Purpose

Jessica is designed to move beyond traditional chatbots into autonomous systems that can reason, learn, and assist in real-world decision-making.

---

## ⚙️ Requirements

* Python 3.10+
* 16GB RAM minimum (32GB recommended)
* Local GGUF models (not included)

---

## ▶️ Quick Start

```bash
pip install -r requirements.txt
python run_jessica.py
```

Alternative:

```bash
python -m jessica
```

---

## ⚠️ Note on Models

Large AI models are not included due to size constraints.

Jessica is designed to run with locally hosted GGUF models using llama.cpp.

---

## 📸 Demo

See full system demos and screenshots:
👉 https://www.henser.co.za

---

## 📚 Documentation

Detailed documentation is available in the `/docs` folder, including:

* Meta-cognition system
* Self-learning pipeline
* Identity anchors
* System awareness

---

## 👨‍💻 Author

Hendrik Venter
AI Systems Builder

---
