# 2-Week Sprint Plan: Development Intelligence Platform

This document simulates the agile delivery cycle used to rapidly prototype this platform for MzN International.

## Sprint Goal
Deliver a functional, full-stack, AI-powered intelligence platform that automates funding matches and proposal generation.

## Week 1: Core API & Data Layer

*   **Day 1 (Planning & Setup)**: Finalize API abstractions, set up Python `backend/` directory, and define Pydantic models.
*   **Day 2 (Knowledge Base)**: Seed `data/knowledge_docs/` with 5 realistic reports. Implement `vector_store.py` using FAISS.
*   **Day 3 (Funding Mechanics)**: Create `grants.csv`. Build `FundingAgent` semantic search.
*   **Day 4 (Agent Pipeline)**: Write `PlannerAgent`, `ProposalAgent`, and `WorkflowAgent`. 
*   **Day 5 (Integration)**: Build `AgentOrchestrator` and expose via `main.py`.

## Week 2: Frontend & Deployment

*   **Day 6 (React Scaffold)**: `npm create vite@latest`, setup Tailwind CSS colors, setup Lucide icons.
*   **Day 7 (Component UI)**: Build the `InputPanel` card and establish Axios networking to the backend.
*   **Day 8 (Dashboard Visuals)**: Build `ResultsDashboard`, ensuring complex JSON arrays map cleanly to UX-friendly UI cards.
*   **Day 9 (Docker Architecture)**: Create the multi-stage Dockerfile enabling FastAPI to serve the built React `dist/` folder.
*   **Day 10 (Review)**: Internal QA, compliance review against GDPR guidelines, and documentation finalization.
