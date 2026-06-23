from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import FeedbackRequest
from ..database import get_db, Feedback
import uuid

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    if request.rating not in [1, -1]:
        raise HTTPException(status_code=400, detail="Rating must be 1 or -1")
        
    feedback_entry = Feedback(
        id=str(uuid.uuid4()),
        query_id=request.query_id,
        rating=request.rating,
        comment=request.comment
    )
    db.add(feedback_entry)
    db.commit()
    
    return {"status": "success"}
