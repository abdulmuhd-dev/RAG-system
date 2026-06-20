import logging

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings

logger = logging.getLogger(__name__)


class Embedder:
    """
    Wraps the embedding model.

    Responsible for ONE thing:
    Load the embedding model and expose it.

    LangChain's vector store classes (Chroma, Pinecone, etc.)
    expect an "embedding function" object — this class provides
    exactly that, so it plugs in directly.
    """

    def __init__(self):
        settings = get_settings()

        logger.info(f"Loading embedding model: {settings.embedding_model}")

        self.model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info("Embedding model loaded successfully")

    def get_model(self) -> HuggingFaceEmbeddings:
        """
        Returns the underlying embedding model.
        Vector stores (ChromaDB etc.) need this object directly.
        """
        return self.model

    def embed_text(self, text: str) -> list[float]:
        """
        Manually embed a single piece of text.
        Useful for testing/debugging — not used in the main
        pipeline (the vector store handles embedding internally).
        """
        return self.model.embed_query(text)
