"""
Funding Agent
==============
Matches NGO projects with funding dataset based on keywords and semantic similarity.
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.config import settings
from app.services.embedding_service import embed_batch, embed_text

logger = logging.getLogger(__name__)


class FundingAgent:
    """Matches NGO projects with funding dataset."""
    
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self._grants_df = None

    def _load_grants(self) -> pd.DataFrame:
        if self._grants_df is None:
            logger.info("Loading grants database from %s", settings.grants_path)
            self._grants_df = pd.read_csv(settings.grants_path)
        return self._grants_df

    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank funding opportunities."""
        logger.info("▶ FundingAgent: Matching opportunities for sector=%s, region=%s", context["sector"], context["region"])
        
        df = self._load_grants()
        sector_lower = context["sector"].lower()
        region_lower = context["region"].lower()

        # Keyword filtering
        mask = (
            df["sector"].str.lower().isin([sector_lower, "multiple"])
        ) & (
            df["region"].str.lower().str.contains(region_lower)
            | df["region"].str.lower().str.contains("global")
        )

        filtered = df[mask].copy()

        if filtered.empty:
            logger.info("No explicit matches; falling back to all grants.")
            filtered = df.copy()

        # Semantic ranking
        grant_descriptions = filtered["description"].tolist()
        grant_vectors = np.array(embed_batch(grant_descriptions), dtype=np.float32)
        query_vector = np.array(embed_text(context["project_description"]), dtype=np.float32)

        norms_g = np.linalg.norm(grant_vectors, axis=1, keepdims=True)
        norms_g[norms_g == 0] = 1.0
        norm_q = np.linalg.norm(query_vector)
        if norm_q == 0:
            norm_q = 1.0

        similarities = (grant_vectors @ query_vector) / (norms_g.flatten() * norm_q)
        filtered["relevance_score"] = similarities

        top = filtered.nlargest(self.top_k, "relevance_score")

        results = []
        for _, row in top.iterrows():
            results.append(
                {
                    "donor_name": row["donor_name"],
                    "sector": row["sector"],
                    "region": row["region"],
                    "funding_size": row["funding_size"],
                    "eligibility": row["eligibility"],
                    "description": row["description"],
                    "relevance_score": round(float(row["relevance_score"]), 4),
                }
            )

        return results
