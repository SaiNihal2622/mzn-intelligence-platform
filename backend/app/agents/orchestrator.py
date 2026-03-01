"""
Agent Orchestrator
===================
Coordinates the sequential execution of all agents in the Development
Intelligence Platform.
"""

from __future__ import annotations

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
    """Orchestrates the multi-agent workflow sequentially."""
    
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
        """Execute the full agent pipeline for a client project."""
        start = time.time()
        logger.info(
            "═══ Orchestrator: starting pipeline for sector=%s, region=%s ═══",
            sector,
            region,
        )

        # 1. Planner Agent understands input and sets up context
        context = await self.planner.execute(sector, region, project_description)

        # 2. Knowledge Agent performs RAG
        similar_projects = await self.knowledge.execute(context)

        # 3. Funding Agent matches opportunities
        matched_funding = await self.funding.execute(context)

        # 4. Proposal Agent generates structured outline and briefing
        proposal_outline, consultant_briefing = await self.proposal.execute(
            context, similar_projects, matched_funding
        )

        # 5. Workflow Agent creates task checklist
        workflow_tasks = await self.workflow.execute(context)

        # 6. Compliance Agent adds GDPR and responsible AI notes
        compliance_notes = await self.compliance.execute(context, proposal_outline)

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
                    "ComplianceAgent"
                ]
            }
        }
