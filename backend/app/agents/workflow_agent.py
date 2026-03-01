"""
Workflow Agent
===============
Produces consultant task checklists simulating sprint delivery.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List
from app.config import settings
from app.services.llm_service import generate_text

logger = logging.getLogger(__name__)


class WorkflowAgent:
    """Produces consultant task checklist using LLMs."""
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a sprint-style workflow task summary."""
        sector = context["sector"]
        region = context["region"]
        desc = context["project_description"]
        logger.info("▶ WorkflowAgent: Generating workflow task summary via LLM")

        if settings.use_llm:
            try:
                system_instruction = (
                    "You are a Senior Project Management Consultant. "
                    "You excel at breaking down complex development projects into logical, actionable work streams. "
                    "Your task lists are detailed, technical, and account for realistic consultancy overhead."
                )

                prompt = f"""
Generate a detailed 2-sprint (4-week) implementation workflow for the following project:
Sector: {sector}
Region: {region}
Description: {desc}

RETRIEVED CONTEXT:
{context.get('knowledge_context', 'No specific context available.')}

REQUIREMENTS:
- Generate 6-8 distinct, highly granular tasks.
- Each task should have a realistic 'Estimated Hours' (e.g., 8, 16, 24).
- Include specific 'Dependencies' referencing other task titles.
- Use realistic dates starting from {datetime.now().strftime('%Y-%m-%d')}.

OUTPUT FORMAT:
Return ONLY a JSON list of objects. Each object MUST have:
- 'title': Professional task title.
- 'description': Multi-sentence markdown description explaining the technical requirement.
- 'hours': Integer.
- 'start_date': YYYY-MM-DD.
- 'end_date': YYYY-MM-DD.
- 'dependencies': List of task titles or empty list.

Example:
[
  {{
    "title": "Stakeholder Mapping & UX Research",
    "description": "Perform deep-dive interviews with local community leaders in {region} to identify primary friction points in {sector} interventions.",
    "hours": 24,
    "start_date": "2026-03-01",
    "end_date": "2026-03-04",
    "dependencies": []
  }}
]
"""
                
                output = await generate_text(prompt, system_instruction=system_instruction)
                import json
                clean_json = output.strip().strip("```json").strip("```").strip()
                tasks = json.loads(clean_json)
                if isinstance(tasks, list):
                    return tasks
            except Exception as e:
                logger.error(f"WorkflowAgent LLM failed: {e}")

        # Fallback to templates
        today = datetime.utcnow().date()

        return [
            {
                "task_id": "TASK-001",
                "title": "Stakeholder Mapping & Landscape Analysis",
                "description": f"Identify key stakeholders in the {sector} sector across {region}.",
                "owner": "Senior Consultant",
                "priority": "high",
                "sprint": "Sprint 1 – Week 1",
                "estimated_hours": 12,
                "start_date": str(today),
                "due_date": str(today + timedelta(days=3)),
                "status": "pending",
                "dependencies": [],
            },
            {
                "task_id": "TASK-002",
                "title": "Desk Review & Evidence Synthesis",
                "description": f"Review prior MzN reports and donor documentation relevant to {sector} in {region}.",
                "owner": "Research Analyst",
                "priority": "high",
                "sprint": "Sprint 1 – Week 1",
                "estimated_hours": 16,
                "start_date": str(today),
                "due_date": str(today + timedelta(days=4)),
                "status": "pending",
                "dependencies": [],
            },
            {
                "task_id": "TASK-003",
                "title": "Funding Opportunity Analysis",
                "description": "Analyse matched funding opportunities and prepare donor alignment matrix.",
                "owner": "Business Development Lead",
                "priority": "high",
                "sprint": "Sprint 1 – Week 1",
                "estimated_hours": 8,
                "start_date": str(today + timedelta(days=2)),
                "due_date": str(today + timedelta(days=4)),
                "status": "pending",
                "dependencies": ["TASK-001"],
            },
            {
                "task_id": "TASK-004",
                "title": "Proposal Outline & First Draft",
                "description": "Prepare detailed proposal outline including executive summary, objectives, and budget.",
                "owner": "Proposal Writer",
                "priority": "critical",
                "sprint": "Sprint 1 – Week 2",
                "estimated_hours": 20,
                "start_date": str(today + timedelta(days=5)),
                "due_date": str(today + timedelta(days=10)),
                "status": "pending",
                "dependencies": ["TASK-002", "TASK-003"],
            },
            {
                "task_id": "TASK-005",
                "title": "Internal Peer Review",
                "description": "Conduct internal review of draft proposal with sector experts.",
                "owner": "Quality Assurance Lead",
                "priority": "medium",
                "sprint": "Sprint 2 – Week 1",
                "estimated_hours": 8,
                "start_date": str(today + timedelta(days=10)),
                "due_date": str(today + timedelta(days=12)),
                "status": "pending",
                "dependencies": ["TASK-004"],
            },
            {
                "task_id": "TASK-006",
                "title": "Final Proposal Submission Package",
                "description": "Compile final submission package including narrative, budget, annexes, CVs.",
                "owner": "Senior Consultant",
                "priority": "critical",
                "sprint": "Sprint 2 – Week 2",
                "estimated_hours": 16,
                "start_date": str(today + timedelta(days=13)),
                "due_date": str(today + timedelta(days=14)),
                "status": "pending",
                "dependencies": ["TASK-005"],
            },
        ]
