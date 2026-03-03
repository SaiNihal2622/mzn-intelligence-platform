"""
Proposal Agent
===============
Generates structured proposal outline (problem, solution, impact,
implementation, budget concept) and a consultant briefing.
"""

import logging
from typing import Any, Dict, List, Tuple

from app.config import settings
from app.services.llm_service import generate_text

logger = logging.getLogger(__name__)


class ProposalAgent:
    """Generates structured proposal outline and briefing notes using LLMs."""
    
    async def execute(
        self,
        context: Dict[str, Any],
        similar_projects: List[Dict[str, Any]],
        matched_funding: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], str]:
        """Generate proposal and briefing using advanced LLMs."""
        logger.info("▶ ProposalAgent: Generating proposal and briefing via LLM")
        
        sector = context["sector"]
        region = context["region"]
        desc = context["project_description"]
        
        if settings.use_llm:
            try:
                # Prepare a rich prompt
                knowledge_context = "\n".join([f"- {p['source']}: {p['text'][:200]}..." for p in similar_projects[:3]]) if similar_projects else "No relevant institutional knowledge found."
                funding_context = "\n".join([f"- {f['donor_name']} ({f['sector']}): {f['description'][:200]}..." for f in matched_funding[:3]]) if matched_funding else "No specific donor findings available."

                system_instruction = (
                    "You are a Senior Technical Strategy Advisor at MzN International. "
                    "Your writing is sophisticated, analytical, and highly professional. "
                    "Provide deep strategic insights for consultancy proposals."
                )

                prompt = f"""
PROJECT CONTEXT:
Sector: {sector}
Region: {region}
Description: {desc}

RETRIEVED INSTITUTIONAL KNOWLEDGE (RAG):
{knowledge_context}

DONOR FINDINGS:
{funding_context}

TASK:
Generate a Concise Strategy Outline and an Executive Briefing.

OUTPUT FORMAT:
Return ONLY a JSON object with:
- 'proposal_outline': Markdown string (concise strategy).
- 'consultant_briefing': Markdown string (bulleted briefing).
"""
                output = await generate_text(prompt, system_instruction=system_instruction)
                
                import json
                clean_json = output.strip().strip("```json").strip("```").strip()
                data = json.loads(clean_json)
                return data['proposal_outline'], data['consultant_briefing']
                
            except Exception as e:
                logger.error(f"ProposalAgent LLM call failed: {e}")

        # Fallback to templates
        proposal_outline = self._generate_proposal(sector, region, desc, similar_projects, matched_funding)
        consultant_briefing = self._generate_briefing(sector, region, desc, similar_projects, matched_funding)
        
        return proposal_outline, consultant_briefing

    def _generate_proposal(
        self, sector: str, region: str, desc: str,
        similar_projects: List[Dict[str, Any]], matched_funding: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        references = [p.get("source", "internal report") for p in similar_projects[:3]]
        donors = [f.get("donor_name", "TBD") for f in matched_funding[:3]]
        
        return {
            "title": f"{sector.title()} Initiative: {region}",
            "problem": f"Critical challenges in {sector} across {region} require immediate, evidence-based interventions. {desc}",
            "solution": f"A targeted, multi-phase approach leveraging best practices from {', '.join(references) if references else 'past experiences'}.",
            "impact": [
                f"Strengthen {sector} capacity in target communities",
                f"Establish sustainable frameworks for service delivery",
                f"Build local ownership and knowledge transfer mechanisms"
            ],
            "implementation": {
                "approach": "Mixed-methods participatory design with phased implementation.",
                "phases": [
                    {"name": "Inception", "activities": ["Baseline data collection", "Stakeholder mapping"]},
                    {"name": "Delivery", "activities": [f"Core {sector} interventions", "Capacity building"]},
                    {"name": "Consolidation", "activities": ["Knowledge products", "Sustainability transition"]}
                ]
            },
            "budget_concept": {
                "total_estimated": "USD 1,500,000 – 3,000,000",
                "potential_donors": donors,
                "notes": "Aligns with typical funding envelopes for identified donors."
            }
        }

    def _generate_briefing(
        self, sector: str, region: str, desc: str,
        similar_projects: List[Dict[str, Any]], matched_funding: List[Dict[str, Any]]
    ) -> str:
        
        references = ", ".join(p.get("source", "N/A") for p in similar_projects[:3]) or "None available"
        donors = ", ".join(f.get("donor_name", "TBD") for f in matched_funding[:3]) or "None"
        
        return f"""
CONFIDENTIAL CONSULTANT BRIEFING

Sector: {sector.title()}
Region: {region}
Generated By: Development Intelligence Platform

1. PROJECT OVERVIEW
{desc}

2. SECTOR CONTEXT & TRENDS
The {sector} sector in {region} involves evolving policy frameworks and a shift towards locally-led development. Integration of digital tools and resilience-building approaches are critical.

3. STAKEHOLDER LANDSCAPE
- Donors: {donors}
- Implementers: Local NGOs, government ministries, community leaders.

4. PRIOR ENGAGEMENTS
MzN Experience: {references}

5. RECOMMENDED APPROACH
- Conduct rapid landscape assessment.
- Design intervention using participatory theory of change.
- Maintain adaptive management throughout delivery.
""".strip()
