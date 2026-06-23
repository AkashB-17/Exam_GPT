from typing import List, Dict
from . import vector_store
from ..config import TOP_K_RESULTS

def retrieve(exam: str, question: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
    """Retrieve relevant Previous Year Questions for a given query."""
    return vector_store.search(exam, question, top_k=top_k)
