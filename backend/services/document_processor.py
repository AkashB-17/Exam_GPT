"""
Document Processor Service
Handles: text extraction, chunking, embedding, and FAISS indexing for user-uploaded documents.
"""
import os
import json
import uuid
import logging
import fitz  # PyMuPDF
import faiss
import numpy as np
from typing import List, Dict, Tuple
from ..config import FAISS_INDEX_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# --- Directory for user-uploaded document indexes ---
USER_INDEX_DIR = os.path.join(FAISS_INDEX_DIR, "user_docs")

# --- Chunking parameters ---
CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 100    # overlap between consecutive chunks


def _ensure_dirs():
    """Ensure the user index directory exists."""
    os.makedirs(USER_INDEX_DIR, exist_ok=True)


def extract_text(filepath: str, filename: str) -> str:
    """Extract text from a PDF or plain-text file."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext in (".txt", ".md", ".text"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .txt, .md")


def _extract_pdf(filepath: str) -> str:
    """Extract text from a PDF using PyMuPDF."""
    doc = fitz.open(filepath)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks


def process_and_index(
    filepath: str,
    filename: str,
    exam: str,
    doc_id: str,
) -> Tuple[int, List[Dict]]:
    """
    Full pipeline: extract text → chunk → embed → add to per-exam FAISS user index.

    Returns:
        (num_chunks, list of chunk metadata dicts)
    """
    from . import vector_store  # import here to avoid circular dependency

    _ensure_dirs()

    # 1. Extract text
    raw_text = extract_text(filepath, filename)
    if not raw_text.strip():
        raise ValueError("No text could be extracted from this document.")

    # 2. Chunk
    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("Document produced no usable text chunks.")

    logger.info(f"Document '{filename}' → {len(chunks)} chunks")

    # 3. Embed using the shared embedding model
    if vector_store.embedding_model is None:
        from sentence_transformers import SentenceTransformer
        vector_store.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    embeddings = vector_store.embedding_model.encode(chunks, convert_to_numpy=True)

    # 4. Build / update user FAISS index for this exam
    index_key = f"{exam}_user"
    index_path = os.path.join(USER_INDEX_DIR, f"{index_key}.index")
    meta_path = os.path.join(USER_INDEX_DIR, f"{index_key}_meta.json")

    # Load existing index or create new
    dim = embeddings.shape[1]
    if os.path.exists(index_path):
        user_index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            user_meta = json.load(f)
    else:
        user_index = faiss.IndexFlatL2(dim)
        user_meta = []

    # 5. Add embeddings
    user_index.add(embeddings.astype(np.float32))

    # 6. Build metadata for each chunk
    chunk_metas = []
    for i, chunk in enumerate(chunks):
        meta = {
            "id": f"{doc_id}_chunk_{i}",
            "doc_id": doc_id,
            "exam": exam,
            "source_file": filename,
            "chunk_index": i,
            "question_text": chunk,   # reuse field for compatibility with PYQ search
            "answer": "",
            "year": 0,
            "subject": "User Document",
            "is_user_doc": True,
        }
        chunk_metas.append(meta)
        user_meta.append(meta)

    # 7. Save index and metadata
    faiss.write_index(user_index, index_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(user_meta, f, ensure_ascii=False, indent=2)

    # 8. Update in-memory vector store
    vector_store.user_indexes[index_key] = user_index
    vector_store.user_metadata[index_key] = user_meta

    logger.info(f"Indexed {len(chunks)} chunks for exam '{exam}' from '{filename}'")
    return len(chunks), chunk_metas


def remove_document_from_index(doc_id: str, exam: str) -> bool:
    """
    Remove all chunks belonging to a document from the FAISS user index.
    Since FAISS doesn't support deletion, we rebuild the index without the doc's chunks.
    """
    from . import vector_store

    _ensure_dirs()
    index_key = f"{exam}_user"
    meta_path = os.path.join(USER_INDEX_DIR, f"{index_key}_meta.json")
    index_path = os.path.join(USER_INDEX_DIR, f"{index_key}.index")

    if not os.path.exists(meta_path):
        return False

    with open(meta_path, "r", encoding="utf-8") as f:
        user_meta = json.load(f)

    # Filter out chunks belonging to this doc
    remaining_meta = [m for m in user_meta if m.get("doc_id") != doc_id]

    if len(remaining_meta) == len(user_meta):
        return False  # doc_id not found

    if not remaining_meta:
        # No chunks left — delete index files
        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        vector_store.user_indexes.pop(index_key, None)
        vector_store.user_metadata.pop(index_key, None)
        return True

    # Rebuild index from remaining chunks
    texts = [m["question_text"] for m in remaining_meta]

    if vector_store.embedding_model is None:
        from sentence_transformers import SentenceTransformer
        vector_store.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    embeddings = vector_store.embedding_model.encode(texts, convert_to_numpy=True)
    dim = embeddings.shape[1]
    new_index = faiss.IndexFlatL2(dim)
    new_index.add(embeddings.astype(np.float32))

    faiss.write_index(new_index, index_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(remaining_meta, f, ensure_ascii=False, indent=2)

    vector_store.user_indexes[index_key] = new_index
    vector_store.user_metadata[index_key] = remaining_meta

    logger.info(f"Removed doc {doc_id} from {index_key}, rebuilt with {len(remaining_meta)} chunks")
    return True
