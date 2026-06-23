from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..models import QueryRequest, QueryResponse, PYQCitation
from ..database import get_db, QueryLog
from ..services import module_router, rag_service, llm_service
from ..services.vector_store import compute_confidence
from ..services.llm_service import LLMError
from ..config import EXAM_CONFIG, TOP_K_RESULTS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    x_session_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    exam = request.exam
    question = request.question

    # 1. Validate exam
    if exam not in EXAM_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported exam: {exam}. Available: {', '.join(EXAM_CONFIG.keys())}")

    # 2. Determine module
    if request.module_override:
        supported = EXAM_CONFIG[exam].get("supported_modules", [])
        if request.module_override not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Module '{request.module_override}' not supported for {exam}. Available: {supported}"
            )
        module = request.module_override
    else:
        module = module_router.detect_module(exam, question)

    # 3. Retrieve PYQs
    retrieved_pyqs = rag_service.retrieve(exam, question, top_k=TOP_K_RESULTS)

    # 4. Compute confidence from retrieval quality
    confidence = compute_confidence(retrieved_pyqs, num_total_expected=TOP_K_RESULTS)

    # 5. Generate AI response
    try:
        answer = llm_service.generate(exam, question, module, retrieved_pyqs)
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # 6. Log to DB
    log_entry = QueryLog(
        session_id=x_session_id,
        exam=exam,
        question=question,
        module_used=module,
        response=answer,
        citations_count=len(retrieved_pyqs)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    # 7. Format citations (strip internal _distance field)
    citations = []
    for pyq in retrieved_pyqs:
        citations.append(PYQCitation(
            id=pyq.get("id", ""),
            exam=pyq.get("exam", exam),
            year=pyq.get("year", 0),
            subject=pyq.get("subject", "Uncategorized"),
            question_text=pyq.get("question_text", ""),
            answer=pyq.get("answer", "")
        ))

    return QueryResponse(
        query_id=log_entry.id,
        answer=answer,
        module_used=module,
        citations=citations,
        confidence=confidence
    )
