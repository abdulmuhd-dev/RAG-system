import logging
from app.db.vector_store import ONNXEmbeddingWrapper


class Embedder:
    """
    Uses ChromaDB's built-in ONNX embedding function.

    WHY ONNX over PyTorch:
      PyTorch → 2.5GB, full ML framework, GPU support
      ONNX    → ~50MB runtime, optimized for inference only
      Same model (all-MiniLM-L6-v2), same quality,
      fraction of the size.
    """

    def __init__(self):
        logger.info("Loading ONNX embedding model")
        self.model = ONNXEmbeddingWrapper()
        logger.info("Embedding model loaded successfully")

    def get_model(self) -> ONNXEmbeddingWrapper:
        return self.model

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text — useful for testing."""
        return self.model.embed_query(text)
