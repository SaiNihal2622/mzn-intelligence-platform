"""
Vector Store Service
=====================
Manages a FAISS index over the consultancy knowledge base.  Documents are
chunked, embedded, and indexed on application startup.  At query time the
store performs approximate nearest-neighbour search and returns the most
relevant text chunks with source metadata.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import faiss
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
    """FAISS-backed vector store for consultancy knowledge base documents."""

    def __init__(self) -> None:
        self._index: Optional[faiss.IndexFlatIP] = None
        self._chunks: List[DocumentChunk] = []
        self._is_built = False

    # -- Index construction ---------------------------------------------------

    def build_index(self, directory: Optional[Path] = None) -> int:
        """Read all .txt files from *directory*, chunk them, embed, and index.

        Args:
            directory: Path to the knowledge base folder.  Defaults to
                       ``settings.knowledge_base_path``.

        Returns:
            Number of chunks indexed.
        """
        directory = directory or settings.knowledge_base_path

        if not directory.exists():
            logger.warning("Knowledge base directory not found: %s", directory)
            return 0

        # Collect and chunk documents ----------------------------------------
        self._chunks = []
        for filepath in sorted(directory.glob("*.txt")):
            text = filepath.read_text(encoding="utf-8")
            chunks = self._chunk_text(text, filepath.name)
            self._chunks.extend(chunks)

        if not self._chunks:
            logger.warning("No document chunks found in %s", directory)
            return 0

        logger.info("Embedding %d chunks from %s …", len(self._chunks), directory)

        # Embed all chunks at once -------------------------------------------
        texts = [c.text for c in self._chunks]
        vectors = embed_batch(texts)
        matrix = np.array(vectors, dtype=np.float32)

        # Normalise for cosine similarity via inner-product index
        faiss.normalize_L2(matrix)

        # Build FAISS index ---------------------------------------------------
        dim = matrix.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(matrix)

        self._is_built = True
        logger.info(
            "FAISS index built: %d vectors of dimension %d", self._index.ntotal, dim
        )
        return self._index.ntotal

    # -- Search ---------------------------------------------------------------

    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Perform semantic search over the indexed knowledge base.

        Args:
            query: Natural-language query string.
            top_k: Number of results to return. Defaults to ``settings.top_k_results``.

        Returns:
            A list of :class:`SearchResult` ordered by descending relevance.
        """
        if not self._is_built or self._index is None:
            logger.warning("Vector store has not been built yet.")
            return []

        top_k = top_k or settings.top_k_results

        query_vec = np.array([embed_text(query)], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        scores, indices = self._index.search(query_vec, top_k)

        results: List[SearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunk = self._chunks[idx]
            results.append(
                SearchResult(
                    text=chunk.text,
                    source=chunk.source,
                    score=float(score),
                    metadata=chunk.metadata,
                )
            )
        return results

    # -- Helpers --------------------------------------------------------------

    @staticmethod
    def _chunk_text(text: str, source: str) -> List[DocumentChunk]:
        """Split *text* into overlapping chunks.

        Uses ``settings.chunk_size`` and ``settings.chunk_overlap``.
        """
        words = text.split()
        chunk_size = settings.chunk_size
        overlap = settings.chunk_overlap
        chunks: List[DocumentChunk] = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
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
