import os
import json
import faiss
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from ..config import FAISS_INDEX_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Global state
indexes = {}
metadata = {}
embedding_model = None

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
        logger.info(f"Successfully loaded {loaded_count} indexes.")


def search(exam: str, query_text: str, top_k: int = 5):
    """
    Search FAISS index for similar PYQs.
    Returns a list of dicts, each with a '_distance' field for confidence scoring.
    """
    if exam not in indexes or exam not in metadata:
        return []

    index = indexes[exam]
    meta_list = metadata[exam]

    if index.ntotal == 0 or len(meta_list) == 0:
        return []

    # Ensure top_k is not larger than the index size
    k = min(top_k, index.ntotal)

    # Compute query vector
    query_vector = embedding_model.encode([query_text], convert_to_numpy=True)

    # Search
    distances, indices_arr = index.search(query_vector, k)

    results = []
    for i, idx in enumerate(indices_arr[0]):
        if idx != -1 and idx < len(meta_list):
            result = dict(meta_list[idx])  # Copy to avoid mutating cached data
            result['_distance'] = float(distances[0][i])
            results.append(result)

    return results


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
