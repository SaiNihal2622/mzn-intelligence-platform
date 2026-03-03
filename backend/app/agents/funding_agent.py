"""
Funding Agent
==============
Matches NGO projects with funding dataset. 
Pre-caches grant embeddings at startup for instant retrieval.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import settings
from app.services.embedding_service import embed_batch, embed_text

logger = logging.getLogger(__name__)

# Module-level embedding cache
_grants_cache: Optional[Dict[str, Any]] = None


def _precompute_grant_embeddings():
    """Pre-compute and cache all grant embeddings once."""
    global _grants_cache
    if _grants_cache is not None:
        return _grants_cache

    grants_path = settings.grants_path
    if not grants_path.exists():
        logger.warning("Grants file not found: %s", grants_path)
        _grants_cache = {"df": pd.DataFrame(), "vectors": None, "norms": None}
        return _grants_cache

    logger.info("Pre-computing grant embeddings (one-time)...")
    df = pd.read_csv(grants_path)
    descriptions = df["description"].tolist()
    vectors = np.array(embed_batch(descriptions), dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    _grants_cache = {"df": df, "vectors": vectors, "norms": norms}
    logger.info("Grant embeddings cached: %d grants × %d dims", *vectors.shape)
    return _grants_cache


class FundingAgent:
    """Matches NGO projects with funding dataset using cached embeddings."""

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank funding opportunities using pre-cached embeddings."""
        logger.info("▶ FundingAgent: Matching for sector=%s, region=%s", context["sector"], context["region"])

        cache = _precompute_grant_embeddings()
        df = cache["df"].copy()
        
        if df.empty:
            return []

        # Keyword filtering
        sector_lower = context["sector"].lower()
        region_lower = context["region"].lower()
        mask = (
            df["sector"].str.lower().isin([sector_lower, "multiple"])
        ) & (
            df["region"].str.lower().str.contains(region_lower)
            | df["region"].str.lower().str.contains("global")
        )
        filtered_indices = df[mask].index.tolist()

        if not filtered_indices:
            logger.info("No keyword matches; using all grants.")
            filtered_indices = df.index.tolist()

        # Use pre-cached embeddings — only embed the query (1 API call)
        all_vectors = cache["vectors"]
        all_norms = cache["norms"]
        grant_vectors = all_vectors[filtered_indices]
        grant_norms = all_norms[filtered_indices]

        query_vector = np.array(embed_text(context["project_description"]), dtype=np.float32)
        norm_q = np.linalg.norm(query_vector)
        if norm_q == 0:
            norm_q = 1.0

        similarities = (grant_vectors @ query_vector) / (grant_norms.flatten() * norm_q)

        filtered_df = df.iloc[filtered_indices].copy()
        filtered_df["relevance_score"] = similarities
        top = filtered_df.nlargest(self.top_k, "relevance_score")

        results = []
        for _, row in top.iterrows():
            results.append({
                "donor_name": row["donor_name"],
                "sector": row["sector"],
                "region": row["region"],
                "funding_size": row["funding_size"],
                "eligibility": row["eligibility"],
                "description": row["description"],
                "relevance_score": round(float(row["relevance_score"]), 4),
            })

        return results
