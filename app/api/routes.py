import logging
import os
import tempfile

from flask import Blueprint, request, jsonify

from app.core.chunker import DocumentChunker
from app.core.generator import RAGGenerator
from app.db.vector_store import VectorStore

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def allowed_file(filename: str) -> bool:
    """Check file extension is supported."""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.get("/health")
def health_check():
    """
    Liveness probe endpoint.

    Kubernetes calls this every 30s to confirm the pod is alive.
    Must return 200 or K8s will restart the pod.
    Keep it lightweight — no DB calls, no heavy logic.
    """
    return jsonify({"status": "healthy"}), 200


@api_bp.post("/ingest")
def ingest_document():
    """
    Upload a document and index it into the vector store.

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
        chunker = DocumentChunker()
        vector_store = VectorStore()

        chunks = chunker.load_and_chunk(tmp_path)
        vector_store.add_documents(chunks)

        logger.info(f"Ingested '{file.filename}' → {len(chunks)} chunks")

        return jsonify({
            "message": "Document ingested successfully",
            "filename": file.filename,
            "chunks_created": len(chunks),
        }), 201

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return jsonify({
            "error": "Ingestion failed",
            "detail": str(e)
        }), 500

    finally:
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

    try:
        generator = RAGGenerator()
        answer = generator.answer(question)

        return jsonify({
            "question": question,
            "answer": answer,
        }), 200

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({
            "error": "Generation failed",
            "detail": str(e)
        }), 500
