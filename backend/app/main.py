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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.config import settings
from app.services.vector_store import vector_store

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
