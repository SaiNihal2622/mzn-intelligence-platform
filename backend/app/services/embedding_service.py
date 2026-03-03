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

OPENROUTER_EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

# Embedding dimension for text-embedding-3-small (and Gemini)
EMBED_DIM = 1536


def _hash_embed(text: str, dim: int = EMBED_DIM) -> List[float]:
    """
    Deterministic hash-based fallback embedding.
    Produces consistent non-zero vectors for similarity comparisons.
    """
    vec = np.zeros(dim, dtype=np.float64)
    words = text.lower().split()
    for word in words:
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = h % dim
        val = math.sin(h * 0.0001) 
        vec[idx] += val
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def _call_openrouter_embed(text: str) -> List[float]:
    """Call OpenRouter Embeddings API."""
    if not settings.openrouter_api_key:
        logger.error("OpenRouter API key missing for embeddings")
        return _hash_embed(text)

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.embedding_model,
        "input": text[:8000]
    }

    try:
        resp = requests.post(OPENROUTER_EMBED_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.error("OpenRouter embed error %d: %s", resp.status_code, resp.text)
            return _hash_embed(text)
        data = resp.json()
        return data["data"][0]["embedding"]
    except Exception as e:
        logger.error("OpenRouter embed request failed: %s", e)
        return _hash_embed(text)


def _call_gemini_embed(text: str) -> List[float]:
    """Call Gemini Embeddings API securely via headers."""
    if not settings.gemini_api_key:
        return _hash_embed(text)

    headers = {"x-goog-api-key": settings.gemini_api_key}
    payload = {
        "content": {"parts": [{"text": text[:6000]}]}
    }

    try:
        resp = requests.post(GEMINI_EMBED_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.error("Gemini embed error %d: %s", resp.status_code, resp.text)
            return _hash_embed(text)
        data = resp.json()
        return data.get("embedding", {}).get("values", [])
    except Exception as e:
        logger.error("Gemini embed failed: %s", e)
        return _hash_embed(text)


def embed_text(text: str) -> List[float]:
    """Return the embedding vector for a single text string using the configured provider."""
    if settings.embedding_provider == "openrouter":
        return _call_openrouter_embed(text)
    return _call_gemini_embed(text)


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
