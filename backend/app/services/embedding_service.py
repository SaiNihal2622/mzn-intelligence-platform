"""
Embedding Service
==================
Uses the Gemini Embeddings API (text-embedding-004) for dense vector embeddings.
No local ML models — zero torch dependency.
Falls back to TF-IDF style hashing when API is unavailable.
"""

from __future__ import annotations

import logging
import hashlib
import math
import requests
from typing import List

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

# Embedding dimension for gemini-embedding-001
EMBED_DIM = 3072


def _hash_embed(text: str, dim: int = EMBED_DIM) -> List[float]:
    """
    Deterministic hash-based fallback embedding.
    Produces consistent non-zero vectors for similarity comparisons.
    Uses multiple hash seeds to fill the full dimension.
    """
    vec = np.zeros(dim, dtype=np.float64)
    words = text.lower().split()
    for word in words:
        # Use word hash to index into embedding space
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = h % dim
        # Value between -1 and 1 based on character content
        val = math.sin(h * 0.0001) 
        vec[idx] += val
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def _gemini_embed_single(text: str) -> List[float]:
    """Call Gemini Embeddings API for a single text."""
    if not settings.gemini_api_key:
        logger.warning("No Gemini API key — using hash fallback embedding")
        return _hash_embed(text)

    # Use header instead of query param to avoid leakage in logs
    headers = {"x-goog-api-key": settings.gemini_api_key}
    payload = {
        "content": {
            "parts": [{"text": text[:6000]}]
        }
    }

    try:
        resp = requests.post(GEMINI_EMBED_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.error("Gemini embed API error %d: %s", resp.status_code, resp.text)
            return _hash_embed(text)
        data = resp.json()
        values = data.get("embedding", {}).get("values", [])
        if not values:
            logger.error("Empty embedding returned from Gemini API: %s", data)
            return _hash_embed(text)
        return values
    except Exception as e:
        logger.error("Gemini embed request failed: %s — using hash fallback", e)
        return _hash_embed(text)


def embed_text(text: str) -> List[float]:
    """Return the embedding vector for a single text string."""
    return _gemini_embed_single(text)


import concurrent.futures

def embed_batch(texts: List[str], batch_size: int = 50) -> List[List[float]]:
    """Return embedding vectors for a batch of texts concurrently."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all texts for embedding concurrently
        future_to_index = {executor.submit(embed_text, text): i for i, text in enumerate(texts)}
        
        # Pre-allocate results list to maintain order
        results = [[] for _ in range(len(texts))]
        
        for future in concurrent.futures.as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                vec = future.result()
                results[idx] = vec
            except Exception as e:
                logger.error("Embedding failed for batch item %d: %s", idx, e)
                results[idx] = _hash_embed(texts[idx])
                
    logger.info("Embedded %d texts concurrently", len(texts))
    return results
