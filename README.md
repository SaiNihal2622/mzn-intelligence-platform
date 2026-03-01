# 🏗️ Development Intelligence Platform
### Professional AI-Augmented Consultancy Framework

The **Development Intelligence Platform** is a structured, multi-agent orchestration system designed for international development consultancies. It transforms fragmented institutional memory and complex donor landscapes into actionable, high-quality project intelligence.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=Development+Intelligence+Dashboard+Preview)

## 🌟 Key Features
*   **Structured Orchestration:** Abandons unpredictable chatbots for a deterministic 6-agent sequential pipeline (Planner, Knowledge, Funding, Proposal, Workflow, Compliance).
*   **Frontier LLM Support:** Integrated with **Gemini 1.5 Pro** and **Claude 3.5 (OpenRouter)** with a failproof local model fallback.
*   **Consultancy-Grade RAG:** Local FAISS vector store for semantic retrieval of historical reports and proprietary datasets.
*   **Operational Tasking:** Automatically generates 2-sprint project plans and consultant executive briefings.
*   **Full Architectural Transparency:** Dedicated dashboard sections for system logic and workflow analysis.
*   **GDPR-Ready:** Built-in compliance agent and regional data-protection filtering.

## Architecture & Technology Stack
The platform uses a modern, open-source stack designed for zero-API-cost deployment.

*   **Frontend**: React (Vite) + Vanilla CSS (Glassmorphism)
*   **Backend**: Python FastAPI
*   **AI Orchestration**: Custom 6-Agent Sequential Pipeline
*   **Knowledge Retrieval (RAG)**: FAISS Index + `sentence-transformers`
*   **Infrastructure**: Production-ready Docker container

---

## 🚀 Deployment & Reviewer Access
For detailed instructions on how to host this platform for external review, see the **[DEPLOYMENT.md](./DEPLOYMENT.md)** guide.

---

## 🚀 Quick Start (Docker - Recommended)

The platform is designed to be run as a single container serving both the React frontend and the FastAPI backend.

1.  **Clone the repository.**
2.  **Copy the environment file:**
    ```bash
    cp .env.example .env
    ```
3.  **Build and run the Docker instance:**
    ```bash
    docker build -t dev-intelligence .
    docker run -p 3000:3000 dev-intelligence
    ```
4.  **Access the Dashboard:**
    Open `http://localhost:3000` in your browser.
    *(Note: Model downloading occurs on the first request and might take a minute).*

## 💻 Local Development Setup

To run the frontend and backend separately for development:

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

---

## The Agents

The platform uses a sequential orchestration pipeline to guarantee output structure:
1.  `PlannerAgent`: Validates inputs and sets up the execution context.
2.  `KnowledgeAgent`: Vectorizes queries and extracts chunks from `data/knowledge_docs/`.
3.  `FundingAgent`: Filters `data/grants.csv` and ranks using Semantic Cosine Similarity.
4.  `ProposalAgent`: Formats a proposal structure based on RAG context.
5.  `WorkflowAgent`: Determines agile sprint checklists based on sector.
6.  `ComplianceAgent`: Applies programmatic safety rails and GDPR warnings.

---

## Deployment (Render.com / Fly.io)

This application is ready for free-tier PaaS deployment.

**Render.com configuration:**
1. Select "New Web Service" connecting your repo.
2. Use Docker environment.
3. Set `PORT=3000` in the environment variables.

---

## Future Roadmap
- [ ] Connect Live Sector API (ReliefWeb).
- [ ] Add Multi-Tenant User Authentication (Auth0/Firebase).
- [ ] Implement collaborative editing in the rich text output panels.
- [ ] Add `PDF/DOCX` report generation download links.
