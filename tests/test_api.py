"""Integration tests for API endpoints."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_list_exams():
    """Test the /api/exams endpoint returns all configured exams."""
    response = client.get("/api/exams")
    assert response.status_code == 200
    exams = response.json()
    assert len(exams) >= 6

    exam_ids = [e["id"] for e in exams]
    assert "gate_cs" in exam_ids
    assert "upsc_gs" in exam_ids
    assert "ielts" in exam_ids


def test_query_invalid_exam():
    """Test that an invalid exam returns 400."""
    response = client.post("/api/query", json={
        "exam": "invalid_exam",
        "question": "What is this?"
    })
    assert response.status_code == 400


def test_feedback_invalid_rating():
    """Test that an invalid rating returns 400."""
    response = client.post("/api/feedback", json={
        "query_id": "test-id",
        "rating": 5  # Must be 1 or -1
    })
    assert response.status_code == 400


if __name__ == "__main__":
    test_health_check()
    test_list_exams()
    test_query_invalid_exam()
    test_feedback_invalid_rating()
    print("SUCCESS: All API tests passed!")
