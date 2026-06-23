import groq
import logging
from typing import List, Dict
from ..config import GROQ_API_KEY, LLM_PRIMARY_MODEL, LLM_FAST_MODEL, LLM_MAX_TOKENS, EXAM_CONFIG

logger = logging.getLogger(__name__)

client = groq.Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPTS = {
    "solver": """You are ExamGPT, an expert tutor for Indian competitive exams. The student is preparing for {exam_display_name}. Your task is to solve the given problem step by step, exactly as a top-scoring student would write in the exam. Format your response as follows:

**UNDERSTANDING THE PROBLEM:**
[1-2 sentences identifying what is being asked and what approach will be used]

**STEP-BY-STEP SOLUTION:**
[Numbered steps, each showing the working clearly. Use plain text for equations.]

**FINAL ANSWER:**
[State the answer clearly, with units if applicable.]

**EXAM TIP:**
[One sentence about common mistakes or tricks for this type of question in {exam_display_name}.]""",

    "explainer": """You are ExamGPT, an expert tutor for Indian competitive exams. The student is preparing for {exam_display_name}. Your task is to explain the concept or answer the question clearly and concisely. Format your response as follows:

**CORE ANSWER:**
[Direct answer in 2-3 sentences. No preamble — answer first, explain after.]

**EXPLANATION:**
[Expand on the answer with context, causes, effects, or mechanism. Keep it exam-relevant. Maximum 150 words.]

**EXAM-RELEVANT EXAMPLE:**
[Give one concrete example that would work well in an exam answer. For UPSC, cite a real-world Indian policy or event. For GATE, show a small concrete example.]

**RELATED {exam_display_name} TOPICS:**
[List 3 related topics a student should also study.]""",

    "writing_feedback": """You are ExamGPT, an expert examiner and writing coach for {exam_display_name}. The student has submitted a written answer or essay for evaluation. Provide detailed, constructive feedback. Format your response as follows:

**OVERALL SCORE:**
[Give a score in the format used by the exam — IELTS: X.0/9.0 Band, UPSC: X/10 marks. Then one sentence summarizing the overall quality.]

**DIMENSION SCORES:**
- [Dimension 1 name]: [Score] — [One line of specific feedback]
- [Dimension 2 name]: [Score] — [One line of specific feedback]
- [Dimension 3 name]: [Score] — [One line of specific feedback]
- [Dimension 4 name]: [Score] — [One line of specific feedback]
For IELTS, the dimensions are: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy.
For UPSC Mains, the dimensions are: Content Coverage, Structure & Flow, Examples & Evidence, Conclusion Quality.

**TOP 3 IMPROVEMENTS:**
[Numbered list of the 3 most impactful things the student can fix immediately.]

**CORRECTED SENTENCE EXAMPLE:**
[Take one weak sentence from the student's writing and rewrite it better. Show the original and the improved version.]"""
}

USER_PROMPTS = {
    "solver": """Here are similar questions that appeared in previous {exam_display_name} exams for context:
{pyq_context}
---
Now solve this question: {question}""",

    "explainer": """Here are related questions from previous {exam_display_name} exams:
{pyq_context}
---
Please explain: {question}""",

    "writing_feedback": """Here are examples of high-scoring answers from previous {exam_display_name} exams for reference:
{pyq_context}
---
Please evaluate this student's answer: {question}"""
}


def generate(exam: str, question: str, module: str, retrieved_pyqs: List[Dict]) -> str:
    """Generate a response using Groq Cloud API."""
    exam_info = EXAM_CONFIG.get(exam, {})
    exam_display_name = exam_info.get("display_name", exam)

    # Use primary model for complex tasks, fast model for quick answers
    model = LLM_PRIMARY_MODEL if module == "writing_feedback" else LLM_FAST_MODEL

    # Format PYQ context
    pyq_context_lines = []
    for pyq in retrieved_pyqs:
        ans = pyq.get('answer', '')
        if not ans:
            ans = 'Not provided'
        pyq_context_lines.append(f"Q: {pyq.get('question_text', '')}\nA: {ans}")
    pyq_context = "\n\n".join(pyq_context_lines) if pyq_context_lines else "No previous year questions available for this topic."

    system_prompt = SYSTEM_PROMPTS.get(module, SYSTEM_PROMPTS["explainer"]).format(
        exam_display_name=exam_display_name
    )
    user_message = USER_PROMPTS.get(module, USER_PROMPTS["explainer"]).format(
        exam_display_name=exam_display_name,
        pyq_context=pyq_context,
        question=question
    )

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=LLM_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    except groq.AuthenticationError:
        logger.error("Groq API authentication failed. Check your GROQ_API_KEY.")
        raise LLMError("Invalid API key. Please check your Groq Cloud API key configuration.")

    except groq.RateLimitError:
        logger.warning("Groq API rate limit reached.")
        raise LLMError("Rate limit exceeded. Please wait a moment and try again.")

    except groq.APIError as e:
        logger.error(f"Groq API error: {e}")
        raise LLMError(f"AI service temporarily unavailable. Please try again shortly.")

    except Exception as e:
        logger.error(f"Unexpected error calling LLM: {e}")
        raise LLMError("An unexpected error occurred while generating the answer.")


class LLMError(Exception):
    """Custom exception for LLM service errors."""
    pass
