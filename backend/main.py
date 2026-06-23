from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import DEBUG_MODE, ENVIRONMENT, LOG_LEVEL
from .database import init_db
from .routers import query, exams, feedback
from .services import vector_store

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI app."""
    # --- Startup ---
    logger.info("=" * 60)
    logger.info("  ExamGPT India API — Starting up")
    logger.info("=" * 60)

    logger.info("Initializing database...")
    init_db()

    logger.info("Loading vector indexes...")
    vector_store.load_all_indexes()

    logger.info("=" * 60)
    logger.info("  ExamGPT India API — Ready!")
    logger.info("=" * 60)

    yield

    # --- Shutdown ---
    logger.info("ExamGPT India API — Shutting down.")


app = FastAPI(
    title="ExamGPT India API",
    version="1.0.0",
    description="Unified AI-Powered Q&A Platform for Indian Competitive Exams",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = ["*"] if ENVIRONMENT == "development" else [
    "http://localhost:8501",
    "https://examgpt.streamlit.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(exams.router)
app.include_router(feedback.router)


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "indexes_loaded": len(vector_store.indexes),
    }
