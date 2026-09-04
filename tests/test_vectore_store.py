import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


class TestONNXEmbeddingWrapper:

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_is_langchain_embeddings_subclass(self, mock_onnx):
        """Must be a subclass of LangChain Embeddings."""
        from app.db.vector_store import ONNXEmbeddingWrapper
        from langchain_core.embeddings import Embeddings

        assert issubclass(ONNXEmbeddingWrapper, Embeddings)


class TestVectorStore:

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_initializes_successfully(
        self, mock_chroma, mock_embedder
    ):
        """VectorStore must initialize without errors."""
        from app.db.vector_store import VectorStore

        store = VectorStore()
        assert store is not None
        assert store.store is not None

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_add_documents_returns_ids(
        self, mock_chroma, mock_embedder
    ):
        """add_documents must return list of IDs."""
        from app.db.vector_store import VectorStore

        mock_chroma.return_value.add_documents.return_value = [
            "id1", "id2", "id3"
        ]

        store = VectorStore()
        chunks = [MagicMock() for _ in range(3)]
        ids = store.add_documents(chunks)

        assert len(ids) == 3
        assert ids == ["id1", "id2", "id3"]

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_add_empty_list_returns_empty(
        self, mock_chroma, mock_embedder
    ):
        """Empty chunk list must return [] without calling Chroma."""
        from app.db.vector_store import VectorStore

        store = VectorStore()
        ids = store.add_documents([])

        assert ids == []
        mock_chroma.return_value.add_documents.assert_not_called()

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_similarity_search_returns_documents(
        self, mock_chroma, mock_embedder
    ):
        """similarity_search must return list of Documents."""
        from app.db.vector_store import VectorStore

        fake_results = [
            Document(page_content="RAG is a technique", metadata={}),
            Document(page_content="Vector databases store", metadata={}),
        ]
        mock_chroma.return_value.similarity_search.return_value = (
            fake_results
        )

        store = VectorStore()
        results = store.similarity_search("What is RAG?", k=2)

        assert len(results) == 2
        assert results[0].page_content == "RAG is a technique"

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_similarity_search_uses_default_k(
        self, mock_chroma, mock_embedder
    ):
        """similarity_search without k uses top_k_results from settings."""
        from app.db.vector_store import VectorStore

        mock_chroma.return_value.similarity_search.return_value = []

        store = VectorStore()
        store.similarity_search("test query")

        mock_chroma.return_value.similarity_search.assert_called_once_with(
            "test query", k=4
        )

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_similarity_search_with_score(
        self, mock_chroma, mock_embedder
    ):
        """similarity_search_with_score must return tuples."""
        from app.db.vector_store import VectorStore

        fake_results = [
            (Document(page_content="RAG", metadata={}), 0.92),
        ]
        mock_chroma.return_value.similarity_search_with_score.return_value = (
            fake_results
        )

        store = VectorStore()
        results = store.similarity_search_with_score("What is RAG?")

        assert len(results) == 1
        assert isinstance(results[0], tuple)
        assert results[0][1] == 0.92

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_as_retriever_returns_retriever(
        self, mock_chroma, mock_embedder
    ):
        """as_retriever must return a LangChain retriever."""
        from app.db.vector_store import VectorStore

        store = VectorStore()
        retriever = store.as_retriever()

        mock_chroma.return_value.as_retriever.assert_called_once_with(
            search_kwargs={"k": 4}
        )

    @patch("app.db.vector_store.ONNXEmbeddingWrapper")
    @patch("app.db.vector_store.Chroma")
    def test_delete_collection(
        self, mock_chroma, mock_embedder
    ):
        """delete_collection must call Chroma's delete_collection."""
        from app.db.vector_store import VectorStore

        store = VectorStore()
        store.delete_collection()

        mock_chroma.return_value.delete_collection.assert_called_once()
