from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    exam: str
    question: str
    module_override: Optional[str] = None

class PYQCitation(BaseModel):
    id: str
    exam: str
    year: int
    subject: str
    question_text: str
    answer: Optional[str]

class QueryResponse(BaseModel):
    query_id: str
    answer: str
    module_used: str
    citations: List[PYQCitation]
    confidence: float

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int
    comment: Optional[str] = None

class ExamInfo(BaseModel):
    id: str
    name: str
    description: str
    subjects: List[str]
    modules: List[str]
