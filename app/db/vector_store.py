import logging

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.config import get_settings
from app.core.embedder import Embedder

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Wraps ChromaDB.

    Responsible for ONE thing:
    Store chunks and retrieve the most relevant ones.

    db/ layer never knows about chunking or LLM generation —
    it only knows how to store and search vectors.
    """

    def __init__(self):
        settings = get_settings()
        embedder = Embedder()

        logger.info(
            f"Connecting to ChromaDB | "
            f"collection={settings.collection_name} | "
            f"persist_dir={settings.chroma_persist_dir}"
        )

        self.store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=embedder.get_model(),
            persist_directory=settings.chroma_persist_dir,
        )

        logger.info("ChromaDB connection ready")

    def add_documents(self, chunks: list[Document]) -> list[str]:
        """
        Embed and store a list of chunks.
        Returns the IDs Chroma assigned to each chunk.
        """
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
        """
        Find the k most relevant chunks for a given query.
        Used mainly for debugging/testing retrieval quality.
        """
        settings = get_settings()
        k = k or settings.top_k_results

        logger.info(f"Searching | query='{query}' | top_k={k}")
        results = self.store.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} matching chunk(s)")

        return results

    def similarity_search_with_score(
        self, query: str, k: int | None = None
    ) -> list[tuple[Document, float]]:
        """
        Same as above, but also returns a similarity score per chunk.
        Useful when you want to filter out weak/irrelevant matches.

        IMPORTANT: Chroma returns DISTANCE, not similarity.
        Lower distance = more similar (opposite of cosine similarity).
        """
        settings = get_settings()
        k = k or settings.top_k_results

        return self.store.similarity_search_with_score(query, k=k)

    def as_retriever(self) -> VectorStoreRetriever:
        """
        Returns a LangChain "retriever" object.

        This is what generator.py will use — it plugs directly
        into an LCEL chain.
        """
        settings = get_settings()
        return self.store.as_retriever(
            search_kwargs={"k": settings.top_k_results}
        )

    def delete_collection(self) -> None:
        """
        Wipes the entire collection.
        Useful for resetting during testing/development.
        """
        logger.warning("Deleting entire collection")
        self.store.delete_collection()
