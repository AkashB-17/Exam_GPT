import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq Cloud) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_PRIMARY_MODEL = os.getenv("LLM_PRIMARY_MODEL", "llama-3.3-70b-versatile")
LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL", "llama-3.1-8b-instant")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))

# --- Backend ---
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Vector Store ---
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "backend/data/indexes")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./examgpt.db")

# --- Feature Flags ---
ENABLE_FEEDBACK = os.getenv("ENABLE_FEEDBACK", "true").lower() == "true"
ENABLE_HISTORY = os.getenv("ENABLE_HISTORY", "true").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# --- Environment ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Exam Configurations ---
EXAM_CONFIG = {
    "gate_cs": {
        "display_name": "GATE — Computer Science",
        "subjects": ["Data Structures", "Algorithms", "Operating Systems", "DBMS", "Computer Networks", "Theory of Computation", "Compiler Design", "Digital Logic", "Computer Organization", "Discrete Mathematics", "Linear Algebra", "Probability"],
        "default_module": "solver",
        "supported_modules": ["solver", "explainer"],
        "pyq_years_available": [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    },
    "gate_ece": {
        "display_name": "GATE — Electronics & Communication (ECE)",
        "subjects": ["Networks, Signals and Systems", "Electronic Devices", "Analog Circuits", "Digital Circuits", "Control Systems", "Communications", "Electromagnetics", "Engineering Mathematics"],
        "default_module": "solver",
        "supported_modules": ["solver", "explainer"],
        "pyq_years_available": [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    },
    "cat": {
        "display_name": "CAT — MBA Entrance",
        "subjects": ["Quantitative Aptitude", "Data Interpretation", "Logical Reasoning", "Verbal Ability", "Reading Comprehension"],
        "default_module": "explainer",
        "supported_modules": ["solver", "explainer"],
        "pyq_years_available": [2021, 2022, 2023]
    },
    "upsc_gs": {
        "display_name": "UPSC — Civil Services GS",
        "subjects": ["Indian Polity", "Economy", "History", "Geography", "Science & Technology", "Environment & Ecology", "Current Affairs", "Ethics"],
        "default_module": "explainer",
        "supported_modules": ["explainer", "writing_feedback"],
        "writing_dimensions": ["Content Coverage", "Structure & Flow", "Examples & Evidence", "Conclusion Quality"],
        "pyq_years_available": [2020, 2021, 2022, 2023]
    },
    "ielts": {
        "display_name": "IELTS — English Proficiency",
        "subjects": ["Writing Task 1", "Writing Task 2", "Reading", "Listening", "Speaking", "Grammar", "Vocabulary"],
        "default_module": "writing_feedback",
        "supported_modules": ["explainer", "writing_feedback"],
        "writing_dimensions": ["Task Achievement", "Coherence & Cohesion", "Lexical Resource", "Grammatical Range & Accuracy"],
        "score_format": "X.0/9.0 Band",
        "pyq_years_available": [2022, 2023]
    },
    "gre": {
        "display_name": "GRE — Graduate Admissions",
        "subjects": ["Verbal Reasoning", "Quantitative Reasoning", "Analytical Writing"],
        "default_module": "solver",
        "supported_modules": ["solver", "explainer", "writing_feedback"],
        "pyq_years_available": [2021, 2022]
    }
}
