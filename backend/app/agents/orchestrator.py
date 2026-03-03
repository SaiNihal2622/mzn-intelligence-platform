"""
Agent Orchestrator
===================
Coordinates parallel + sequential execution of all agents for maximum speed.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict

from app.agents.planner_agent import PlannerAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.funding_agent import FundingAgent
from app.agents.proposal_agent import ProposalAgent
from app.agents.workflow_agent import WorkflowAgent
from app.agents.compliance_agent import ComplianceAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow with maximum parallelism."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.knowledge = KnowledgeAgent()
        self.funding = FundingAgent()
        self.proposal = ProposalAgent()
        self.workflow = WorkflowAgent()
        self.compliance = ComplianceAgent()

    async def run_pipeline(
        self,
        sector: str,
        region: str,
        project_description: str,
    ) -> Dict[str, Any]:
        """Execute the full agent pipeline with parallel stages."""
        start = time.time()
        logger.info(
            "═══ Orchestrator: starting pipeline for sector=%s, region=%s ═══",
            sector,
            region,
        )

        # Stage 1: Planner (fast, no API calls)
        context = await self.planner.execute(sector, region, project_description)

        # Stage 1: Async Start for ALL independent agents
        # These 4 can all run at once.
        knowledge_task = asyncio.create_task(self.knowledge.execute(context))
        funding_task = asyncio.create_task(self.funding.execute(context))
        workflow_task = asyncio.create_task(self.workflow.execute(context))
        compliance_task = asyncio.create_task(self.compliance.execute(context))

        # Stage 2: Wait ONLY for Knowledge + Funding (needed for Proposal)
        similar_projects, matched_funding = await asyncio.gather(knowledge_task, funding_task)
        logger.info("▶ Stage 2 Complete: Knowledge + Funding ready. Starting Proposal.")

        # Stage 3: Proposal depends on Knowledge+Funding results
        proposal_task = asyncio.create_task(self.proposal.execute(context, similar_projects, matched_funding))

        # Stage 4: Final Gather of EVERYTHING
        # This allows Proposal, Workflow, and Compliance to finish in parallel.
        (proposal_outline, consultant_briefing), workflow_tasks, compliance_notes = await asyncio.gather(
            proposal_task, workflow_task, compliance_task
        )

        elapsed = round(time.time() - start, 2)
        logger.info("═══ Orchestrator: pipeline completed in %.2fs ═══", elapsed)

        return {
            "funding_matches": matched_funding,
            "similar_projects": similar_projects,
            "proposal_outline": proposal_outline,
            "consultant_briefing": consultant_briefing,
            "workflow_tasks": workflow_tasks,
            "compliance_notes": compliance_notes,
            "metadata": {
                "pipeline_duration_seconds": elapsed,
                "sector": sector,
                "region": region,
                "agents_executed": [
                    "PlannerAgent",
                    "KnowledgeAgent",
                    "FundingAgent",
                    "ProposalAgent",
                    "WorkflowAgent",
                    "ComplianceAgent",
                ],
            },
        }
