import pytest
from unittest.mock import patch, MagicMock


class TestONNXEmbeddingWrapper:

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_embed_documents_returns_list(self, mock_onnx):
        """embed_documents must return list of vectors."""
        from app.db.vector_store import ONNXEmbeddingWrapper

        mock_onnx.return_value.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

        wrapper = ONNXEmbeddingWrapper()
        result = wrapper.embed_documents(["text one", "text two"])

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], list)

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_embed_query_returns_single_vector(self, mock_onnx):
        """embed_query must return a single vector."""
        from app.db.vector_store import ONNXEmbeddingWrapper

        mock_onnx.return_value.return_value = [[0.1, 0.2, 0.3]]

        wrapper = ONNXEmbeddingWrapper()
        result = wrapper.embed_query("what is RAG?")

        assert isinstance(result, list)
        assert isinstance(result[0], float)

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_embed_documents_empty_list(self, mock_onnx):
        """embed_documents with empty list returns empty list."""
        from app.db.vector_store import ONNXEmbeddingWrapper

        mock_onnx.return_value.return_value = []

        wrapper = ONNXEmbeddingWrapper()
        result = wrapper.embed_documents([])

        assert result == []


class TestEmbedder:

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_embedder_initializes(self, mock_onnx):
        """Embedder must initialize without errors."""
        from app.core.embedder import Embedder

        embedder = Embedder()
        assert embedder is not None
        assert embedder.model is not None

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_get_model_returns_wrapper(self, mock_onnx):
        """get_model must return ONNXEmbeddingWrapper instance."""
        from app.core.embedder import Embedder
        from app.db.vector_store import ONNXEmbeddingWrapper

        embedder = Embedder()
        model = embedder.get_model()

        assert isinstance(model, ONNXEmbeddingWrapper)

    @patch("app.db.vector_store.ONNXMiniLM_L6_V2")
    def test_embed_text_returns_vector(self, mock_onnx):
        """embed_text must return a list of floats."""
        from app.core.embedder import Embedder

        mock_onnx.return_value.return_value = [[0.1, 0.2, 0.3]]

        embedder = Embedder()
        result = embedder.embed_text("test query")

        assert isinstance(result, list)
