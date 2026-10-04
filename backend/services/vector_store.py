import os
import json
import faiss
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from ..config import FAISS_INDEX_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Global state — PYQ indexes
indexes = {}
metadata = {}
embedding_model = None

# Global state — User-uploaded document indexes
user_indexes = {}
user_metadata = {}

def load_all_indexes():
    global embedding_model, indexes, metadata

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    if not os.path.exists(FAISS_INDEX_DIR):
        logger.warning(f"Index directory {FAISS_INDEX_DIR} does not exist. Run scripts/ingest_pyqs.py first.")
        return

    logger.info("Loading FAISS indexes...")
    loaded_count = 0
    for filename in os.listdir(FAISS_INDEX_DIR):
        if filename.endswith(".index"):
            exam_name = filename.replace(".index", "")
            index_path = os.path.join(FAISS_INDEX_DIR, filename)
            meta_path = os.path.join(FAISS_INDEX_DIR, f"{exam_name}_meta.json")

            try:
                indexes[exam_name] = faiss.read_index(index_path)

                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        metadata[exam_name] = json.load(f)
                else:
                    metadata[exam_name] = []

                loaded_count += 1
                logger.info(f"  ✓ {exam_name}: {indexes[exam_name].ntotal} items indexed")
            except Exception as e:
                logger.error(f"  ✗ Failed to load index {exam_name}: {e}")

    if loaded_count == 0:
        logger.warning("No FAISS indexes found. Run 'python scripts/ingest_pyqs.py' to build them.")
    else:
        logger.info(f"Successfully loaded {loaded_count} PYQ indexes.")

    # --- Also load user-uploaded document indexes ---
    _load_user_indexes()


def _load_user_indexes():
    """Load FAISS indexes for user-uploaded documents."""
    global user_indexes, user_metadata

    user_index_dir = os.path.join(FAISS_INDEX_DIR, "user_docs")
    if not os.path.exists(user_index_dir):
        logger.info("No user document indexes found (directory does not exist).")
        return

    loaded = 0
    for filename in os.listdir(user_index_dir):
        if filename.endswith(".index"):
            key = filename.replace(".index", "")
            idx_path = os.path.join(user_index_dir, filename)
            meta_path = os.path.join(user_index_dir, f"{key}_meta.json")

            try:
                user_indexes[key] = faiss.read_index(idx_path)
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        user_metadata[key] = json.load(f)
                else:
                    user_metadata[key] = []
                loaded += 1
                logger.info(f"  ✓ user/{key}: {user_indexes[key].ntotal} chunks indexed")
            except Exception as e:
                logger.error(f"  ✗ Failed to load user index {key}: {e}")

    logger.info(f"Loaded {loaded} user document indexes.")


def search(exam: str, query_text: str, top_k: int = 5):
    """
    Search FAISS indexes for similar content — both PYQ and user-uploaded documents.
    Returns a list of dicts, each with a '_distance' field for confidence scoring.
    """
    # Compute query vector once
    query_vector = embedding_model.encode([query_text], convert_to_numpy=True)

    results = []

    # --- Search PYQ index ---
    if exam in indexes and exam in metadata:
        index = indexes[exam]
        meta_list = metadata[exam]
        if index.ntotal > 0 and len(meta_list) > 0:
            k = min(top_k, index.ntotal)
            distances, indices_arr = index.search(query_vector, k)
            for i, idx in enumerate(indices_arr[0]):
                if idx != -1 and idx < len(meta_list):
                    result = dict(meta_list[idx])
                    result['_distance'] = float(distances[0][i])
                    result['_source'] = 'pyq'
                    results.append(result)

    # --- Search user document index ---
    user_key = f"{exam}_user"
    if user_key in user_indexes and user_key in user_metadata:
        u_index = user_indexes[user_key]
        u_meta = user_metadata[user_key]
        if u_index.ntotal > 0 and len(u_meta) > 0:
            k = min(top_k, u_index.ntotal)
            distances, indices_arr = u_index.search(query_vector, k)
            for i, idx in enumerate(indices_arr[0]):
                if idx != -1 and idx < len(u_meta):
                    result = dict(u_meta[idx])
                    result['_distance'] = float(distances[0][i])
                    result['_source'] = 'user_doc'
                    results.append(result)

    # Merge and sort by distance (best matches first), then take top_k
    results.sort(key=lambda r: r['_distance'])
    return results[:top_k]


def compute_confidence(retrieved_pyqs: list, num_total_expected: int = 5) -> float:
    """
    Compute a confidence score (0.0 to 1.0) based on retrieval quality.

    Factors:
    - How many results were retrieved vs expected
    - Average FAISS L2 distance (lower = better match)
    """
    if not retrieved_pyqs:
        return 0.1  # Very low confidence if no PYQs found

    # Factor 1: Coverage (how many of the expected results were found)
    coverage = min(len(retrieved_pyqs) / max(num_total_expected, 1), 1.0)

    # Factor 2: Relevance (based on average L2 distance)
    distances = [pyq.get('_distance', 2.0) for pyq in retrieved_pyqs]
    avg_distance = sum(distances) / len(distances) if distances else 2.0

    # L2 distance → relevance score (lower distance = higher relevance)
    # Typical L2 distances for sentence-transformers range from 0 (identical) to ~2.0 (unrelated)
    relevance = max(0.0, 1.0 - (avg_distance / 2.0))

    # Weighted combination
    confidence = (0.4 * coverage) + (0.6 * relevance)

    # Clamp to [0.1, 1.0]
    return round(max(0.1, min(1.0, confidence)), 2)
