import re

def detect_module(exam: str, question: str) -> str:
    question_lower = question.lower()
    word_count = len(question.split())
    
    # Check for writing_feedback
    writing_keywords = ['evaluate', 'check my', 'score my', 'give feedback on']
    writing_phrases = ['my answer', 'my essay']
    starts_with_writing = any(question_lower.startswith(kw) for kw in writing_keywords)
    contains_writing = any(phrase in question_lower for phrase in writing_phrases)
    
    if (word_count > 100 and exam in ['ielts', 'upsc_gs']) or starts_with_writing or contains_writing:
        return 'writing_feedback'
        
    # Check for solver
    solver_keywords = ['find', 'calculate', 'compute', 'prove', 'solve', 'how many', 'what is the value']
    has_math_symbols = bool(re.search(r'[=+<>\^\*\{\}\[\]\\]|\d+[a-zA-Z]?', question))
    contains_solver = any(kw in question_lower for kw in solver_keywords)
    
    if exam in ['gate_cs', 'gate_ece', 'cat'] and (has_math_symbols or contains_solver):
        return 'solver'
        
    # Default to explainer
    return 'explainer'
