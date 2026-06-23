import os
import json
import sys
import argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import FAISS_INDEX_DIR, EMBEDDING_MODEL

PYQS_DIR = "backend/data/pyqs"
PROCESSED_DIR = "backend/data/processed"


def extract_questions_from_pdf(pdf_path, exam, year):
    """Extract questions from a PDF file (basic regex-based extraction)."""
    import fitz  # PyMuPDF
    import re

    questions = []
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"

        # Split by common question numbering patterns
        splits = re.split(r'(?:Q\.?\s*\d+|Question\s+\d+|\d+\.)', full_text)

        for i, split_text in enumerate(splits[1:], start=1):
            q_text = split_text.strip()
            if not q_text or len(q_text) < 10:
                continue

            q_id = f"{exam}_{year}_q{i}"
            questions.append({
                "id": q_id,
                "exam": exam,
                "year": year,
                "subject": "General",
                "question_text": q_text[:1000],
                "answer": "",
                "difficulty": "medium"
            })

    except Exception as e:
        print(f"  ✗ Error processing {pdf_path}: {e}")

    return questions


def process_pdfs():
    """Process PDF files from the pyqs directory."""
    if not os.path.exists(PYQS_DIR):
        print(f"  ℹ No PDF directory found at {PYQS_DIR}. Skipping PDF processing.")
        return

    for exam in os.listdir(PYQS_DIR):
        exam_dir = os.path.join(PYQS_DIR, exam)
        if not os.path.isdir(exam_dir):
            continue

        pdf_files = [f for f in os.listdir(exam_dir) if f.endswith(".pdf")]
        if not pdf_files:
            continue

        import re

        all_exam_questions = []
        for filename in pdf_files:
            print(f"  📄 Processing PDF: {filename} for exam {exam}...")
            year = 2023
            m = re.search(r'20\d{2}', filename)
            if m:
                year = int(m.group())

            pdf_path = os.path.join(exam_dir, filename)
            qs = extract_questions_from_pdf(pdf_path, exam, year)
            all_exam_questions.extend(qs)
            print(f"     Extracted {len(qs)} questions")

        if all_exam_questions:
            out_file = os.path.join(PROCESSED_DIR, f"{exam}_pyqs.json")

            existing_questions = []
            if os.path.exists(out_file):
                with open(out_file, 'r', encoding='utf-8') as f:
                    existing_questions = json.load(f)

            existing_ids = {q['id'] for q in existing_questions}
            new_count = 0
            for q in all_exam_questions:
                if q['id'] not in existing_ids:
                    existing_questions.append(q)
                    new_count += 1

            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(existing_questions, f, indent=4, ensure_ascii=False)
            print(f"  ✓ Saved {len(existing_questions)} total questions for {exam} ({new_count} new)")


def build_indexes():
    """Build FAISS indexes from processed JSON files."""
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    print(f"{'='*50}\n")
    model = SentenceTransformer(EMBEDDING_MODEL)

    json_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith("_pyqs.json")]

    if not json_files:
        print("  ⚠ No processed JSON files found. Nothing to index.")
        return

    for filename in json_files:
        exam = filename.replace("_pyqs.json", "")
        json_path = os.path.join(PROCESSED_DIR, filename)

        with open(json_path, 'r', encoding='utf-8') as f:
            pyqs = json.load(f)

        if not pyqs:
            print(f"  ⚠ {exam}: Empty JSON file, skipping.")
            continue

        print(f"  📊 Building index for {exam} with {len(pyqs)} questions...")

        texts = [q['question_text'] for q in pyqs]
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        index_path = os.path.join(FAISS_INDEX_DIR, f"{exam}.index")
        faiss.write_index(index, index_path)

        meta_path = os.path.join(FAISS_INDEX_DIR, f"{exam}_meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(pyqs, f, indent=4, ensure_ascii=False)

        print(f"  ✓ {exam}: Indexed {len(pyqs)} questions (dim={dimension})")

    print(f"\n{'='*50}")
    print(f"SUCCESS: All indexes built successfully!")
    print(f"   Index directory: {os.path.abspath(FAISS_INDEX_DIR)}")
    print(f"{'='*50}")


def run_ingestion(json_only=False):
    """Run the full ingestion pipeline."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  ExamGPT India — Data Ingestion Pipeline")
    print(f"{'='*50}\n")

    # Step 1: Process PDFs (unless --json-only)
    if not json_only:
        print("📁 Step 1: Processing PDFs...")
        process_pdfs()
    else:
        print("📁 Step 1: Skipping PDF processing (--json-only mode)")

    # Step 2: Build FAISS indexes from all processed JSONs
    print("\n🔨 Step 2: Building FAISS indexes...")
    build_indexes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ExamGPT India — PYQ Data Ingestion")
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Skip PDF processing, only rebuild FAISS indexes from existing JSON files"
    )
    args = parser.parse_args()
    run_ingestion(json_only=args.json_only)
