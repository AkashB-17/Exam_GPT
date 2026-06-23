from fastapi import APIRouter
from typing import List
from ..models import ExamInfo
from ..config import EXAM_CONFIG

router = APIRouter(prefix="/api/exams", tags=["Exams"])

@router.get("", response_model=List[ExamInfo])
async def list_exams():
    exams = []
    for exam_id, config in EXAM_CONFIG.items():
        exams.append(ExamInfo(
            id=exam_id,
            name=config.get("display_name", exam_id),
            description="",
            subjects=config.get("subjects", []),
            modules=config.get("supported_modules", [])
        ))
    return exams
