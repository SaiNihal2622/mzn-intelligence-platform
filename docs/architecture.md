# 🏗 System Architecture & Workflow

## 1. Architectural Philosophy

The Development Intelligence Platform is intentionally designed as a structured, multi-agent orchestration system, rather than a conversational chatbot. 

Development consultancies require **predictable outputs**, **structured documentation**, and **workflow reproducibility**. For this reason, the system abandons conversational LLM chat in favor of a deterministic sequential pipeline.

### High-Level System Diagram

```text
+-----------------------------------------------------------+
|                  React Dashboard (Frontend)               |
|            Consultancy Workspace & Project Analytics       |
+----------------------------+------------------------------+
                             |
                      [POST /analyze-project]
                             |
                             v
+-----------------------------------------------------------+
|                  FastAPI Gateway (Backend)                |
|           Validation, Static Serving, Orchestration       |
+----------------------------+------------------------------+
                             |
                             v
+----------------------- Agent Orchestrator ----------------+
|                                                           |
| 1. PlannerAgent  -> Frames the consultancy brief           |
|                               |                           |
| 2. KnowledgeAgent -> Queries FAISS Vector Store           |
|                               |                           |
| 3. FundingAgent   -> Cross-matches Donor Dataset          |
|                               |                           |
| 4. ProposalAgent  -> Generations Strategy & Briefing       |
|                               |                           |
| 5. WorkflowAgent  -> Produces Sprint Task Checklist        |
|                               |                           |
| 6. ComplianceAgent -> EU-aligned GDPR & Ethics Review     |
|                                                           |
+----------------------------+------------------------------+
                             |
                     [Aggregated JSON Payload]
                             |
                             v
+-----------------------------------------------------------+
|                  Dashboard Visualization                  |
|          Matched Funding | Proposal | Tasks | Compliance  |
+-----------------------------------------------------------+
```

## 2. Intelligence Layer Architecture

The system prioritizes data privacy and offline capability by utilizing a local vector store and optional local inference.

```text
+----------------------+      +-------------------------+
| Documents (PDF/TXT)  | ---> | Embedding Engine (Local)|
+----------------------+      | (all-MiniLM-L6-v2)      |
                              +------------+------------+
                                           |
                                           v
+----------------------+      +-------------------------+
| User Project Input   | ---> | FAISS Vector Index (RAM)|
+-----------+----------+      | (Cosine Similarity)     |
            |                 +------------+------------+
            |                              |
            |      [Similar Context Chunks]|
            |                              |
            v                              v
+-------------------------------------------------------+
|                 Large Language Model (LLM)            |
|       (Gemini 1.5 Pro | Claude 3.5 | Local T5)        |
+-------------------------------------------------------+
```

## 3. Deployment Architecture

The entire platform is encapsulated within a standardized Docker environment for consistent deployment.

```text
+----------------------- Docker Container -----------------+
|                                                           |
|  +------------------+         +-----------------------+   |
|  |  React Frontend  | <-----> |   FastAPI Backend     |   |
|  |  (Static Build)  |         |   (Python/Uvicorn)    |   |
|  +------------------+         +-----------+-----------+   |
|                                           |               |
|  +----------------------------------------v-----------+   |
|  |               System Resources                     |   |
|  | [FAISS Matrix] [Model Weights] [CSV Datasets]      |   |
|  +----------------------------------------------------+   |
|                                                           |
+-----------------------------------------------------------+
```

## 4. Agent Roles & Consultancy Analogies

| Agent | Purpose | Consultancy Analogy |
| :--- | :--- | :--- |
| **Planner** | Defines workflow context & priorities | Engagement Lead |
| **Knowledge** | Retrieves institutional best practices | Research Analyst |
| **Funding** | Scans donor landscape for matches | Grants Officer |
| **Proposal** | Generates strategy & executive briefing | Technical Writer |
| **Workflow** | Creates actionable task sequences | Project Manager |
| **Compliance** | Validates GDPR & Ethical standards | Legal/QA Lead |

## 5. Scaling with Frontier Models

The architecture is built on a **Modular LLM Dispatcher**. While the prototype uses a lightweight offline model (`flan-t5`) for cost-free deployment, the orchestrator is "Gemini-Ready". Swapping the inference endpoint in `app/config.py` unlocks frontier reasoning (Gemini 1.5 Pro / Claude 3.5 Sonnet) with **zero changes to the agent logic**.

## 6. Responsible AI

The platform integrates **Human-in-the-Loop** validation by default. AI outputs are framed as *Draft Zero* — they represent high-quality starting points that require a senior consultant's sign-off, ensuring institutional integrity and legal compliance with GDPR data protection principles.
