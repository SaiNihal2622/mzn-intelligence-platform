"""
Embedding Service
==================
Uses the Gemini Embeddings API (text-embedding-004) for dense vector embeddings.
No local ML models — zero torch dependency.
"""

from __future__ import annotations

import logging
import requests
from typing import List

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"

# Embedding dimension for text-embedding-004
EMBED_DIM = 768


def _gemini_embed_single(text: str) -> List[float]:
    """Call Gemini Embeddings API for a single text."""
    if not settings.gemini_api_key:
        # Fallback: random-ish deterministic vector (for offline dev only)
        rng = np.random.default_rng(abs(hash(text[:64])))
        v = rng.standard_normal(EMBED_DIM)
        return (v / np.linalg.norm(v)).tolist()

    url = f"{GEMINI_EMBED_URL}?key={settings.gemini_api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text[:8000]}]},  # API limit
    }
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]


def embed_text(text: str) -> List[float]:
    """Return the embedding vector for a single text string."""
    try:
        return _gemini_embed_single(text)
    except Exception as e:
        logger.error("Embedding failed for text snippet: %s", e)
        # Return zero vector on failure so pipeline doesn't crash
        return [0.0] * EMBED_DIM


def embed_batch(texts: List[str], batch_size: int = 50) -> List[List[float]]:
    """Return embedding vectors for a batch of texts (sequential API calls)."""
    results = []
    for i, text in enumerate(texts):
        vec = embed_text(text)
        results.append(vec)
        if (i + 1) % 20 == 0:
            logger.info("Embedded %d/%d texts", i + 1, len(texts))
    return results
