"""
Documents Router — Upload, list, and delete user documents for RAG.
"""
import os
import shutil
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db, UploadedDocument
from ..services import document_processor
from ..config import EXAM_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Maximum file size: 200 MB
MAX_FILE_SIZE = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    exam: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a document and index it into the vector store for RAG."""

    # Validate exam
    if exam not in EXAM_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported exam: {exam}. Available: {', '.join(EXAM_CONFIG.keys())}"
        )

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size / 1024 / 1024:.1f} MB). Maximum is 200 MB."
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")

    # Create DB record
    doc_record = UploadedDocument(
        filename=file.filename,
        exam=exam,
        file_size=file_size,
        status="processing"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Write to a temp file for processing
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        with open(tmp_path, "wb") as f:
            f.write(content)

        # Process and index
        num_chunks, _ = document_processor.process_and_index(
            filepath=tmp_path,
            filename=file.filename,
            exam=exam,
            doc_id=doc_record.id,
        )

        # Update DB record
        doc_record.status = "indexed"
        doc_record.num_chunks = num_chunks
        db.commit()

        return {
            "id": doc_record.id,
            "filename": file.filename,
            "exam": exam,
            "num_chunks": num_chunks,
            "status": "indexed",
            "message": f"Successfully indexed '{file.filename}' into {num_chunks} chunks for {EXAM_CONFIG[exam]['display_name']}."
        }

    except ValueError as e:
        doc_record.status = "error"
        doc_record.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        doc_record.status = "error"
        doc_record.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    finally:
        # Clean up temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("", response_model=None)
async def list_documents(
    exam: str = None,
    db: Session = Depends(get_db)
):
    """List all uploaded documents, optionally filtered by exam."""
    query = db.query(UploadedDocument)
    if exam:
        query = query.filter(UploadedDocument.exam == exam)
    
    docs = query.order_by(UploadedDocument.created_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "exam": doc.exam,
            "exam_display": EXAM_CONFIG.get(doc.exam, {}).get("display_name", doc.exam),
            "file_size": doc.file_size,
            "num_chunks": doc.num_chunks,
            "status": doc.status,
            "error_message": doc.error_message,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }
        for doc in docs
    ]


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document and remove its chunks from the vector index."""
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove from FAISS index
    try:
        document_processor.remove_document_from_index(doc_id, doc.exam)
    except Exception as e:
        logger.warning(f"Error removing document from index: {e}")

    # Remove from DB
    db.delete(doc)
    db.commit()

    return {"message": f"Document '{doc.filename}' deleted successfully.", "id": doc_id}
