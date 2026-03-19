# Jessica AI — Offline Autonomous AI System

Jessica is a fully offline, multi-agent AI system designed for reasoning, decision support, and real-world workflow automation.

Built to operate without cloud dependencies, Jessica combines local LLMs, semantic memory, and modular intelligence into a single autonomous system.

---

## 🚀 Key Features

- Multi-agent “Council of Experts” architecture  
- Fully offline (100% private, no cloud)  
- Dual-model routing (chat + coding)  
- Semantic + episodic memory system  
- Self-learning via LoRA adapters  
- Advanced meta-cognition and self-reflection  
- Modular skill-based architecture  

---

## 🧠 Architecture Overview

Jessica is structured as a modular system:

- `core/` → reasoning engine  
- `jessica/` → orchestration layer  
- `memory/` → learning + persistence  
- `tools/` → integrations + utilities  
- `config/` → system configuration  

---

## ⚙️ Requirements

- Python 3.10+  
- 16GB RAM minimum (32GB recommended)  
- Local GGUF models (not included)  

---

## ▶️ Quick Start

```bash
pip install -r requirements.txt
python run_jessica.py