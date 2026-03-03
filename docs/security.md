# 🛡️ Zero-Leak Security & GDPR Sovereignty

## 1. The Security Architecture: Zero-Exposure
Most AI applications leak API keys in logs, browser history, or repository commits. Our platform implements a **Strict Zero-Leak** infrastructure to protect billing and intellectual property.

### A. Environment Variable Contract
The application strictly refuses to start if sensitive keys are hardcoded.
- **Local:** Managed via a `.env` file (strictly gitignored).
- **Production:** Managed via **Railway Encrypted Secrets**. 
- **Verification:** Developers can run `python backend/app/tools/security_audit.py` to recursively scan the workspace for leaked key patterns (`sk-or-v1-` or `AIzaSy`).

### B. Header-Based Authentication (In-Flight Security)
Unlike standard implementations that pass keys as URL parameters (which get logged by proxies and servers), we use **Request Headers**.
- **OpenRouter:** Passed via standard `Authorization: Bearer` headers.
- **Security Impact:** Keys exist only in RAM during the fetch cycle and are never written to disk logs.

## 2. GDPR & Data Sovereignty
In the international development sector, data mishandling can put populations at risk. The platform is built on the principle of **Data Minimization**.

### A. Local Vector Sovereignty
- **FAISS Index:** The vector database is built and queried entirely in memory (RAM). Even when written to disk, it stays within the private Docker volume.
- **Context Pinning:** The `KnowledgeAgent` retrieves only relevant snippets, ensuring that the LLM only sees the minimum data required to answer the specific brief.

### B. Programmatic Compliance Agent
The `ComplianceAgent` isn't just a text generator; it's a **Regulatory Rails** system. 
- It detects the **Target Region** from user input.
- It dynamically fetches GDPR, CCPA, or regional data-storage advice.
- It injects mandatory safety warnings into the final consultant briefing.

## 3. Responsible AI & Hallucination Mitigation
- **Grounded RAG:** The `ProposalAgent` is instructed to prioritize "Retrieved Context" over "General Knowledge."
- **Deterministic Funding:** We do not let the AI "hallucinate" donors. The `FundingAgent` performs a hard semantic search against a **curated, static CSV dataset**, ensuring 100% eligibility accuracy.

## 4. Operational Security Checklist
- [x] **Static Assets:** Build files are served via FastAPI static mounting, avoiding open directory listing.
- [x] **No Persistent Prompts:** User prompts are processed in-flight and not stored in any persistent database, satisfying basic data minimization mandates.
- [x] **Connection Pooling:** Uses `httpx` to manage secure, encrypted tunnels to AI providers without repeated TLS negotiation leaks.
