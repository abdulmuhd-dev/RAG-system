import logging

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Wraps ChromaDB with ONNX-based embeddings.
    No PyTorch dependency — lightweight and fast.
    """

    def __init__(self):
        settings = get_settings()

        logger.info(
            f"Connecting to ChromaDB | "
            f"collection={settings.collection_name} | "
            f"persist_dir={settings.chroma_persist_dir}"
        )

  
        embedding_function = ONNXMiniLM_L6_V2()

        self.store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=embedding_function,
            persist_directory=settings.chroma_persist_dir,
        )

        logger.info("ChromaDB connection ready")

    def add_documents(self, chunks: list[Document]) -> list[str]:
        if not chunks:
            logger.warning("add_documents called with empty chunk list")
            return []

        logger.info(f"Embedding and storing {len(chunks)} chunk(s)")
        ids = self.store.add_documents(chunks)
        logger.info(f"Stored {len(ids)} chunk(s) successfully")
        return ids

    def similarity_search(
        self, query: str, k: int | None = None
    ) -> list[Document]:
        settings = get_settings()
        k = k or settings.top_k_results

        logger.info(f"Searching | query='{query}' | top_k={k}")
        results = self.store.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} matching chunk(s)")
        return results

    def similarity_search_with_score(
        self, query: str, k: int | None = None
    ) -> list[tuple[Document, float]]:
        settings = get_settings()
        k = k or settings.top_k_results
        return self.store.similarity_search_with_score(query, k=k)

    def as_retriever(self) -> VectorStoreRetriever:
        settings = get_settings()
        return self.store.as_retriever(
            search_kwargs={"k": settings.top_k_results}
        )

    def delete_collection(self) -> None:
        logger.warning("Deleting entire collection")
        self.store.delete_collection()
