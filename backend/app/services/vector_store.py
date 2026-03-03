"""
Vector Store Service
=====================
Manages an in-memory numpy vector store over the consultancy knowledge base.
Documents are chunked, embedded via Gemini API, and indexed on startup.
Uses pure numpy cosine similarity — no FAISS, no torch dependency.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from app.config import settings
from app.services.embedding_service import embed_batch, embed_text

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DocumentChunk:
    """A chunk of text with source metadata."""
    text: str
    source: str
    chunk_index: int
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single search result with relevance score."""
    text: str
    source: str
    score: float
    metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Vector Store
# ---------------------------------------------------------------------------

class VectorStore:
    """Numpy-backed vector store for consultancy knowledge base documents."""

    def __init__(self) -> None:
        self._matrix: Optional[np.ndarray] = None  # Shape: (N, D)
        self._chunks: List[DocumentChunk] = []
        self._is_built = False

    def build_index(self, directory: Optional[Path] = None) -> int:
        """Read all .txt files from directory, chunk, embed, and index."""
        directory = directory or settings.knowledge_base_path

        if not directory.exists():
            logger.warning("Knowledge base directory not found: %s", directory)
            return 0

        self._chunks = []
        for filepath in sorted(directory.glob("*.txt")):
            text = filepath.read_text(encoding="utf-8")
            chunks = self._chunk_text(text, filepath.name)
            self._chunks.extend(chunks)

        if not self._chunks:
            logger.warning("No document chunks found in %s", directory)
            return 0

        logger.info("Embedding %d chunks from %s …", len(self._chunks), directory)

        texts = [c.text for c in self._chunks]
        vectors = embed_batch(texts)
        matrix = np.array(vectors, dtype=np.float32)

        # L2 normalize for cosine similarity via dot product
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._matrix = matrix / norms

        self._is_built = True
        logger.info("Vector index built: %d vectors of dimension %d", len(self._chunks), self._matrix.shape[1])
        return len(self._chunks)

    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Perform semantic search over the indexed knowledge base."""
        if not self._is_built or self._matrix is None:
            logger.warning("Vector store has not been built yet.")
            return []

        top_k = top_k or settings.top_k_results

        query_vec = np.array(embed_text(query), dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        scores = self._matrix @ query_vec  # Cosine similarities
        top_indices = np.argsort(scores)[::-1][:top_k]

        results: List[SearchResult] = []
        for idx in top_indices:
            chunk = self._chunks[idx]
            results.append(
                SearchResult(
                    text=chunk.text,
                    source=chunk.source,
                    score=float(scores[idx]),
                    metadata=chunk.metadata,
                )
            )
        return results

    @staticmethod
    def _chunk_text(text: str, source: str) -> List[DocumentChunk]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunk_size = settings.chunk_size
        overlap = settings.chunk_overlap
        chunks: List[DocumentChunk] = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i: i + chunk_size]
            if not chunk_words:
                break
            chunks.append(
                DocumentChunk(
                    text=" ".join(chunk_words),
                    source=source,
                    chunk_index=len(chunks),
                )
            )
        return chunks

    @property
    def is_ready(self) -> bool:
        return self._is_built


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
vector_store = VectorStore()
