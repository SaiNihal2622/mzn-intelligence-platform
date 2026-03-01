"""
Knowledge Agent
================
Retrieves relevant institutional knowledge via RAG.
"""

import logging
from typing import Any, Dict, List

from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """Performs RAG retrieval over consultancy documents."""
    
    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge chunks matching the context query."""
        query = context["query"]
        logger.info("▶ KnowledgeAgent: Retrieving context for query: %.120s…", query)

        results = vector_store.search(query, top_k=self.top_k)

        similar_projects = [
            {
                "text": r.text,
                "source": r.source,
                "relevance_score": round(r.score, 4),
            }
            for r in results
        ]

        logger.info("KnowledgeAgent returned %d chunks.", len(similar_projects))
        return similar_projects
