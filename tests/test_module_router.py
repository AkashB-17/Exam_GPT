"""Tests for the module_router service."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.module_router import detect_module


def test_solver_detection_gate():
    """GATE CS math problems should route to solver."""
    assert detect_module("gate_cs", "Calculate the time complexity of T(n) = 2T(n/2) + n") == "solver"
    assert detect_module("gate_cs", "Find the number of page faults using FIFO with 3 frames") == "solver"
    assert detect_module("gate_cs", "Compute the value of 2^10 mod 7") == "solver"


def test_solver_detection_cat():
    """CAT math problems should route to solver."""
    assert detect_module("cat", "Find the speed of the train if it covers 150km in 3 hours") == "solver"
    assert detect_module("cat", "How many ways can 5 people be seated in a row?") == "solver"


def test_explainer_detection():
    """Conceptual questions should route to explainer."""
    assert detect_module("gate_cs", "What is the difference between process and thread?") == "explainer"
    assert detect_module("upsc_gs", "Explain the significance of the 42nd Amendment") == "explainer"


def test_writing_feedback_detection_ielts():
    """IELTS essay submissions should route to writing_feedback."""
    long_essay = "Check my essay: " + "This is a test sentence. " * 20
    assert detect_module("ielts", long_essay) == "writing_feedback"
    assert detect_module("ielts", "Evaluate my answer on climate change") == "writing_feedback"


def test_writing_feedback_keywords():
    """Writing feedback keywords should trigger writing module."""
    assert detect_module("ielts", "Score my essay on global warming") == "writing_feedback"
    assert detect_module("upsc_gs", "Check my answer about Indian constitution") == "writing_feedback"


def test_default_to_explainer():
    """Unknown patterns should default to explainer."""
    assert detect_module("gre", "What does 'ubiquitous' mean?") == "explainer"
    assert detect_module("upsc_gs", "Tell me about the Green Revolution in India") == "explainer"


if __name__ == "__main__":
    test_solver_detection_gate()
    test_solver_detection_cat()
    test_explainer_detection()
    test_writing_feedback_detection_ielts()
    test_writing_feedback_keywords()
    test_default_to_explainer()
    print("SUCCESS: All module_router tests passed!")
