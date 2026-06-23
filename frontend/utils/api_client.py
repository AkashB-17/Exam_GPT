import requests
import logging
from backend.config import BACKEND_URL

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60  # seconds — LLM calls can take a while


def submit_query(exam: str, question: str) -> dict:
    """Submit a query to the backend API."""
    url = f"{BACKEND_URL}/api/query"
    try:
        response = requests.post(
            url,
            json={"exam": exam, "question": question},
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure the backend server is running on port 8000."}
    except requests.Timeout:
        return {"error": "Request timed out. The AI is taking too long to respond. Please try again."}
    except requests.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return {"error": detail}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def submit_feedback(query_id: str, rating: int, comment: str = None) -> bool:
    """Submit feedback for a query response."""
    url = f"{BACKEND_URL}/api/feedback"
    try:
        payload = {"query_id": query_id, "rating": rating}
        if comment:
            payload["comment"] = comment
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to submit feedback: {e}")
        return False


def get_exams() -> list:
    """Fetch available exams from the backend."""
    url = f"{BACKEND_URL}/api/exams"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Failed to fetch exams: {e}")
        return []


def check_backend_health() -> bool:
    """Check if the backend is running."""
    url = f"{BACKEND_URL}/"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
