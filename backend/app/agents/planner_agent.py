"""
Planner Agent
==============
Validates and structures the input for downstream agents.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Understands input and prepares workflow context."""
    
    async def execute(self, sector: str, region: str, project_description: str) -> Dict[str, Any]:
        """Prepare execution context."""
        logger.info("▶ PlannerAgent: Structuring initial context")
        return {
            "sector": sector,
            "region": region,
            "project_description": project_description,
            "query": f"Sector: {sector}. Region: {region}. {project_description}"
        }
