# WorkflowSmith: Autonomous Multi-Agent Pipeline Repair System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-red.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

WorkflowSmith is a research-grade system designed to monitor, diagnose, and repair failures in data pipelines autonomously. Leveraging a multi-agent architecture coordinated via LangGraph, it achieves self-healing capabilities and autonomous recovery from common pipeline issues such as schema drift, data corruption, and logic bugs.

## 🏗️ Multi-Agent Architecture

WorkflowSmith employs specialized AI agents orchestrated by an explicit state machine (LangGraph):

- **Planner**: Orchestrates the multi-agent workflow and manages state transitions.
- **Detector**: Classifies pipeline failures based on logs and statistical metadata.
- **Debugger**: Performs Chain-of-Thought (CoT) root-cause analysis and suggests repair strategies.
- **Fixer**: Generates minimal code, imputation, or schema mapping patches.
- **Verifier**: Validates patches in a secure sandbox before deployment, ensuring constraints are met.

## 🛠️ Key Features

- **Automated ETL Pipeline Monitoring**: Integrated `DataWatcher` automatically tracks landing zones for new files.
- **Reasoning-Driven AI**: Agents provide transparent reasoning (Chain-of-Thought) for every decision.
- **LangGraph Orchestration**: Robust explicit state machine for agent coordination.
- **Secure Sandbox**: Static analysis and restricted execution environment for generated patches.
- **Premium Web Dashboard**: A rich Flask UI displaying per-audit repair metrics in real-time.
- **Comprehensive Metrics**: Tracks Mean Time To Repair (MTTR), Patch Success Rates, iteration counts, and verification checks.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- LLM API Key (configured in `.env`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/WorkflowSmith.git
   cd WorkflowSmith
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure the environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set your GOOGLE_API_KEY or OPENAI_API_KEY
   ```

### Running the System

**1. Premium Web Dashboard (Interactive Demo)**
To launch the Flask-based web dashboard to visualize metrics and test file repairs interactively:
```bash
python interactive_demo.py
```
This will automatically open your browser to `http://127.0.0.1:5000`.

**2. Headless / Scripted Repair**
Run the main script to trigger an autonomous repair demo on an enterprise-scale research dataset:
```bash
python src/main.py
```

## 📊 Evaluation & Metrics

The system tracks several research-grade metrics crucial for evaluating autonomous healing systems, including:
- **MTTR (Mean Time To Repair)**: Total time from failure detection to patch deployment.
- **Patch Success Rate**: Percentage of patches passing strict sandbox verification.
- **Reasoning Transparency**: Full trace of agent thought processes securely stored in `logs/`.

---
*Developed as part of a comprehensive research project on autonomous data systems.*
