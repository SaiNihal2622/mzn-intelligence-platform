"""
Embedding Service
==================
Singleton wrapper around sentence-transformers for generating dense vector
embeddings.  The model is loaded once on first use and reused across requests
to minimise memory footprint and latency.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model on first call."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s …", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully.")
    return _model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_text(text: str) -> List[float]:
    """Return the embedding vector for a single text string.

    Args:
        text: The input text to embed.

    Returns:
        A list of floats representing the dense vector.
    """
    model = _get_model()
    vector: np.ndarray = model.encode(text, show_progress_bar=False)
    return vector.tolist()


def embed_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Return embedding vectors for a batch of texts.

    Args:
        texts: A list of input texts.
        batch_size: Number of texts to encode in one forward pass.

    Returns:
        A list of embedding vectors (each a list of floats).
    """
    model = _get_model()
    vectors: np.ndarray = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
    )
    return vectors.tolist()
