# Security, GDPR, and Responsible AI

The Development Intelligence Platform operates in a sector with highly sensitive qualitative data. Protecting target populations and organizational intellectual property is paramount.

## 1. Compliance By Origin (GDPR)
Operating inside the EU or conducting data analysis on subjects originating from GDPR jurisdictions demands strict compliance.

The platform achieves compliance via:
* **The Compliance Agent**: A specific Python class designed solely to inject compliance reminders into the consultant's dashboard. It analyzes the queried region, injecting relevant data-storage guidelines into the frontend JSON output.
* **On-Premise Deployment Capability**: All models (`sentence-transformers` and Local LLMs) process inferences entirely on the host machine. 
* **Database Isolation**: The Vector Database (FAISS) builds in memory or writes strictly to the `data/` volume.

## 2. The AI Safety Paradigm (Hallucinations)
Consultancies lose entire contracts to hallucinated budget numbers or fabricated prior engagements. 

The Development Intelligence Platform mitigates hallucinations structurally:
* **No generative donors**: `FundingAgent` explicitly matches via semantic similarity to a curated, static `grants.csv`, preserving donor eligibility accuracy. 
* **RAG Prompt Guardrails**: The `KnowledgeAgent` passes explicit contexts to the `ProposalAgent`, severely limiting the chance of fabricating ungrounded claims.

## 3. Access Controls (Roadmap)
The current structure supports wrapping the API into a JWT-authenticated envelope. Consultants should require Role Based Access Control (RBAC) linking their Active Directory account to specific Regional knowledge silos.

**Currently, no logging of user prompts is stored persistently**, satisfying basic data minimization rules.
