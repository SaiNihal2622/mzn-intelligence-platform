"""
Development Intelligence Platform – FastAPI Application
======================================================
Production-grade REST API exposing the AI agent pipeline.
Serves the React frontend application from the static directory constraint.
"""

from __future__ import annotations

import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.config import settings
from app.services.vector_store import vector_store
from app.services.document_service import process_document, retrieve_relevant_chunks, get_session_info
from app.services.llm_service import generate_text

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("dev_platform")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ClientInput(BaseModel):
    sector: str = Field(..., examples=["climate"])
    region: str = Field(..., examples=["East Africa"])
    project_description: str = Field(..., examples=["Community-based climate adaptation."])


class FundingMatch(BaseModel):
    donor_name: str
    sector: str
    region: str
    funding_size: str
    eligibility: str
    description: str
    relevance_score: float


class SimilarProject(BaseModel):
    text: str
    source: str
    relevance_score: float


class WorkflowTask(BaseModel):
    task_id: str
    title: str
    description: str
    owner: str
    priority: str
    sprint: str
    estimated_hours: int
    start_date: str
    due_date: str
    status: str
    dependencies: List[str]


class PipelineMetadata(BaseModel):
    pipeline_duration_seconds: float
    sector: str
    region: str
    agents_executed: List[str]


class AnalysisResponse(BaseModel):
    """Full response schema from the agent pipeline."""
    funding_matches: List[FundingMatch]
    similar_projects: List[SimilarProject]
    proposal_outline: Dict[str, Any]
    consultant_briefing: str
    workflow_tasks: List[WorkflowTask]
    compliance_notes: str
    metadata: PipelineMetadata


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    preview: str
    suggested_questions: List[str]


class ChatRequest(BaseModel):
    doc_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    doc_id: str


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Build the FAISS vector index on startup."""
    logger.info("Starting Development Intelligence Platform API...")
    n_indexed = vector_store.build_index()
    logger.info("Vector store ready: %d chunks indexed.", n_indexed)
    yield
    logger.info("Shutting down API.")


# ---------------------------------------------------------------------------
# FastAPI application & Middlewares
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Development Intelligence Platform",
    description="Multi-agent platform for consultancy workflows.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AgentOrchestrator()


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/analyze-project",
    response_model=AnalysisResponse,
    tags=["analysis"],
)
async def analyze_project(client_input: ClientInput) -> AnalysisResponse:
    """Execute the full agent pipeline for a client project."""
    logger.info("POST /analyze-project – sector=%s", client_input.sector)
    try:
        result = await orchestrator.run_pipeline(
            sector=client_input.sector,
            region=client_input.region,
            project_description=client_input.project_description,
        )
        return AnalysisResponse(**result)
    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Agent pipeline failed: {str(e)}",
        ) from e


# ---------------------------------------------------------------------------
# Document Chatbot Endpoints
# ---------------------------------------------------------------------------

SUPPORTED_FILE_TYPES = {".pdf", ".txt", ".md"}

@app.post("/upload-document", response_model=DocumentUploadResponse, tags=["document-chat"])
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """Upload a PDF or TXT document for RAG-based Q&A chatting."""
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Use PDF or TXT.")

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=400, detail="File too large. Max size is 20 MB.")

    try:
        doc_id = process_document(file_bytes, file.filename or "document.pdf")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    info = get_session_info(doc_id)

    # Auto-generate suggested starter questions
    preview = info["preview"]
    suggested_questions = [
        "What are the main conclusions of this document?",
        "Summarize the key recommendations.",
        "What problem does this document address?",
    ]

    logger.info("Document uploaded: %s → doc_id=%s", file.filename, doc_id)
    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=info["filename"],
        chunk_count=info["chunk_count"],
        preview=preview,
        suggested_questions=suggested_questions,
    )


@app.post("/chat-document", response_model=ChatResponse, tags=["document-chat"])
async def chat_document(request: ChatRequest) -> ChatResponse:
    """Ask a question about an uploaded document using RAG + Gemini."""
    doc_id = request.doc_id
    question = request.message.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        chunks, filename = retrieve_relevant_chunks(doc_id, question, top_k=4)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    context = "\n\n---\n\n".join(chunks)
    prompt = f"""You are an expert analyst. A user has uploaded a document called "{filename}" and is asking questions about it.

Using ONLY the information from the document excerpts below, answer the user's question. If the answer is not found in the document, say "This information is not covered in the uploaded document."

DOCUMENT EXCERPTS:
{context}

USER QUESTION: {question}

ANSWER (cite the relevant parts of the document in your response):"""

    system_instruction = (
        "You are a precise, professional document analyst. Answer only from the provided document context. "
        "Be concise but thorough. If quoting, use quotation marks."
    )

    try:
        answer = await generate_text(prompt, system_instruction=system_instruction)
    except Exception as e:
        logger.error("LLM generation failed for doc chat: %s", e)
        answer = "I encountered an error generating an answer. Please check your API keys or try again."

    return ChatResponse(
        answer=answer,
        sources=[c[:200] + "..." for c in chunks[:3]],  # Return first 200 chars of each source
        doc_id=doc_id,
    )


# ---------------------------------------------------------------------------
# Static File Serving (React Frontend)
# ---------------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

# Mount React static files if the directory exists (it will post-build)
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React's index.html for all non-API paths to support client-side routing."""
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path == "analyze-project":
            raise HTTPException(status_code=404, detail="Not Found")
        
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend build not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
