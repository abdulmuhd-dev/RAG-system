import logging
import os
import tempfile
import time

from flask import Blueprint, request, jsonify
from prometheus_client import Counter, Histogram, Gauge

from app.core.chunker import DocumentChunker
from app.core.generator import RAGGenerator
from app.db.vector_store import VectorStore

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}

DOCUMENTS_INGESTED = Counter(
    "rag_documents_ingested_total",
    "Total number of documents successfully ingested",
    ["filename_extension"]
)

CHUNKS_CREATED = Counter(
    "rag_chunks_created_total",
    "Total number of chunks created during ingestion"
)

INGESTION_ERRORS = Counter(
    "rag_ingestion_errors_total",
    "Total number of failed document ingestions"
)

ANSWER_LATENCY = Histogram(
    "rag_answer_latency_seconds",
    "Time taken to generate an answer",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

QUESTIONS_ASKED = Counter(
    "rag_questions_asked_total",
    "Total number of questions asked"
)

QUESTION_ERRORS = Counter(
    "rag_question_errors_total",
    "Total number of failed question answers"
)

ACTIVE_REQUESTS = Gauge(
    "rag_active_requests",
    "Number of requests currently being processed"
)


def allowed_file(filename: str) -> bool:
    """Check file extension is supported."""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.get("/health")
def health_check():
    """
    Liveness probe endpoint.
    Kubernetes calls this every 30s to confirm pod is alive.
    Keep it lightweight — no DB calls, no heavy logic.
    """
    return jsonify({"status": "healthy"}), 200


@api_bp.post("/ingest")
def ingest_document():
    """
    Upload and index a document into the vector store.
    Expects: multipart/form-data with a 'file' field
    Returns: chunk count and filename on success
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file type. "
                     f"Allowed: {list(ALLOWED_EXTENSIONS)}"
        }), 400

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        ACTIVE_REQUESTS.inc()

        chunker = DocumentChunker()
        vector_store = VectorStore()

        chunks = chunker.load_and_chunk(tmp_path)
        vector_store.add_documents(chunks)

        DOCUMENTS_INGESTED.labels(filename_extension=suffix).inc()
        CHUNKS_CREATED.inc(len(chunks))

        logger.info(f"Ingested '{file.filename}' → {len(chunks)} chunks")

        return jsonify({
            "message": "Document ingested successfully",
            "filename": file.filename,
            "chunks_created": len(chunks),
        }), 201

    except Exception as e:
        INGESTION_ERRORS.inc()
        logger.error(f"Ingestion failed: {e}")
        return jsonify({
            "error": "Ingestion failed",
            "detail": str(e)
        }), 500

    finally:
        ACTIVE_REQUESTS.dec()
        os.unlink(tmp_path)


@api_bp.post("/ask")
def ask_question():
    """
    Ask a question against ingested documents.
    Expects: JSON body { "question": "..." }
    Returns: question + answer pair
    """
    data = request.get_json()

    if not data or not data.get("question", "").strip():
        return jsonify({"error": "Question cannot be empty"}), 400

    question = data["question"].strip()

    ACTIVE_REQUESTS.inc()
    QUESTIONS_ASKED.inc()

    start_time = time.time()

    try:
        generator = RAGGenerator()
        answer = generator.answer(question)

        ANSWER_LATENCY.observe(time.time() - start_time)

        return jsonify({
            "question": question,
            "answer": answer,
        }), 200

    except Exception as e:
        QUESTION_ERRORS.inc()
        logger.error(f"Generation failed: {e}")
        return jsonify({
            "error": "Generation failed",
            "detail": str(e)
        }), 500

    finally:
        ACTIVE_REQUESTS.dec()
