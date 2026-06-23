"""Tests for Pydantic models."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import QueryRequest, QueryResponse, PYQCitation, FeedbackRequest, ExamInfo


def test_query_request():
    """Test QueryRequest model creation and defaults."""
    req = QueryRequest(exam="gate_cs", question="What is a binary tree?")
    assert req.exam == "gate_cs"
    assert req.question == "What is a binary tree?"
    assert req.module_override is None

    req_with_override = QueryRequest(exam="ielts", question="Check my essay", module_override="writing_feedback")
    assert req_with_override.module_override == "writing_feedback"


def test_query_response():
    """Test QueryResponse model with query_id."""
    resp = QueryResponse(
        query_id="abc-123",
        answer="The answer is 42.",
        module_used="solver",
        citations=[],
        confidence=0.85
    )
    assert resp.query_id == "abc-123"
    assert resp.confidence == 0.85
    assert resp.citations == []


def test_pyq_citation():
    """Test PYQCitation model."""
    citation = PYQCitation(
        id="gate_cs_2022_q1",
        exam="gate_cs",
        year=2022,
        subject="Operating Systems",
        question_text="What is virtual memory?",
        answer="A memory management technique"
    )
    assert citation.year == 2022
    assert citation.subject == "Operating Systems"


def test_feedback_request():
    """Test FeedbackRequest validation."""
    fb = FeedbackRequest(query_id="abc-123", rating=1)
    assert fb.rating == 1
    assert fb.comment is None

    fb_with_comment = FeedbackRequest(query_id="abc-123", rating=-1, comment="Needs improvement")
    assert fb_with_comment.comment == "Needs improvement"


def test_exam_info():
    """Test ExamInfo model."""
    info = ExamInfo(
        id="gate_cs",
        name="GATE — Computer Science",
        description="Graduate Aptitude Test in Engineering",
        subjects=["Data Structures", "Algorithms"],
        modules=["solver", "explainer"]
    )
    assert len(info.subjects) == 2
    assert "solver" in info.modules


if __name__ == "__main__":
    test_query_request()
    test_query_response()
    test_pyq_citation()
    test_feedback_request()
    test_exam_info()
    print("SUCCESS: All model tests passed!")
