"""
Document Service
================
Handles PDF/TXT upload, text extraction, FAISS indexing per session,
and question-answering using the existing LLM service.
"""

import io
import uuid
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

# Global in-memory session store: { doc_id: { "chunks": [...], "index": faiss_index, "filename": str } }
_document_sessions: Dict[str, dict] = {}

# Shared embedding model (loaded once)
_embedding_model: Optional[SentenceTransformer] = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model for document service...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(f"[Page {i+1}]\n{text.strip()}")
        return "\n\n".join(pages)
    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        raise ValueError(f"Could not read PDF: {e}")


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def process_document(file_bytes: bytes, filename: str) -> str:
    """
    Parse the document, chunk it, embed it, and store in a FAISS index.
    Returns a doc_id used for future queries.
    """
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif extension in (".txt", ".md"):
        text = file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {extension}. Use PDF or TXT.")

    if not text.strip():
        raise ValueError("Could not extract any text from the document.")

    chunks = _chunk_text(text)
    logger.info("Document '%s' → %d chunks", filename, len(chunks))

    model = _get_embedding_model()
    embeddings = model.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
    embeddings_np = np.array(embeddings, dtype="float32")

    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    index.add(embeddings_np)

    doc_id = str(uuid.uuid4())
    _document_sessions[doc_id] = {
        "chunks": chunks,
        "index": index,
        "filename": filename,
        "text_preview": text[:300],
    }

    logger.info("Document indexed with id=%s", doc_id)
    return doc_id


def retrieve_relevant_chunks(doc_id: str, question: str, top_k: int = 4) -> Tuple[List[str], str]:
    """
    Retrieve the most relevant document chunks for a given question.
    Returns (chunks, filename).
    """
    session = _document_sessions.get(doc_id)
    if not session:
        raise ValueError(f"Document session '{doc_id}' not found. Please re-upload the document.")

    model = _get_embedding_model()
    query_embedding = model.encode([question], normalize_embeddings=True)
    query_np = np.array(query_embedding, dtype="float32")

    distances, indices = session["index"].search(query_np, min(top_k, len(session["chunks"])))

    relevant_chunks = [session["chunks"][i] for i in indices[0] if i != -1]
    return relevant_chunks, session["filename"]


def get_session_info(doc_id: str) -> Optional[dict]:
    """Return metadata about an uploaded document session."""
    session = _document_sessions.get(doc_id)
    if not session:
        return None
    return {
        "doc_id": doc_id,
        "filename": session["filename"],
        "chunk_count": len(session["chunks"]),
        "preview": session["text_preview"],
    }


def cleanup_session(doc_id: str) -> bool:
    """Remove a document session from memory."""
    if doc_id in _document_sessions:
        del _document_sessions[doc_id]
        logger.info("Document session %s removed.", doc_id)
        return True
    return False
