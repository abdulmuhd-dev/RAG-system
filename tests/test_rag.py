import pytest
from unittest.mock import patch, MagicMock

from app.main import create_app


@pytest.fixture
def app():
    """Create a fresh Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """
    Flask test client — simulates HTTP requests without
    spinning up a real server. No port needed, no network.
    """
    return app.test_client()


class TestHealthCheck:

    def test_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_returns_healthy_status(self, client):
        response = client.get("/api/v1/health")
        data = response.get_json()
        assert data["status"] == "healthy"


class TestIngestEndpoint:

    def test_no_file_returns_400(self, client):
        response = client.post("/api/v1/ingest")
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_empty_filename_returns_400(self, client):
        data = {"file": (b"", "")}
        response = client.post(
            "/api/v1/ingest",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400

    def test_unsupported_file_type_returns_400(self, client):
        data = {"file": (b"fake content", "malware.exe")}
        response = client.post(
            "/api/v1/ingest",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("app.api.routes.VectorStore")
    @patch("app.api.routes.DocumentChunker")
    def test_successful_ingestion_returns_201(
        self, mock_chunker, mock_vector_store, client
    ):
        """
        Note the parameter order: decorators apply bottom-up
        but parameters go top-down:
          @patch DocumentChunker   → mock_chunker (2nd decorator, 1st param)
          @patch VectorStore       → mock_vector_store (1st decorator, 2nd param)
        """
        fake_chunks = [MagicMock() for _ in range(3)]
        mock_chunker.return_value.load_and_chunk.return_value = fake_chunks
        mock_vector_store.return_value.add_documents.return_value = ["id1", "id2", "id3"]

        data = {"file": (b"This is test content about RAG.", "test.txt")}
        response = client.post(
            "/api/v1/ingest",
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        body = response.get_json()
        assert body["chunks_created"] == 3
        assert body["filename"] == "test.txt"
        assert "message" in body

    @patch("app.api.routes.VectorStore")
    @patch("app.api.routes.DocumentChunker")
    def test_chunker_failure_returns_500(
        self, mock_chunker, mock_vector_store, client
    ):
        mock_chunker.return_value.load_and_chunk.side_effect = Exception(
            "Corrupt file"
        )

        data = {"file": (b"corrupt content", "broken.txt")}
        response = client.post(
            "/api/v1/ingest",
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 500
        body = response.get_json()
        assert "error" in body
        assert "detail" in body


class TestAskEndpoint:

    def test_empty_question_returns_400(self, client):
        response = client.post("/api/v1/ask", json={"question": ""})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_whitespace_question_returns_400(self, client):
        response = client.post("/api/v1/ask", json={"question": "   "})
        assert response.status_code == 400

    def test_missing_question_field_returns_400(self, client):
        response = client.post("/api/v1/ask", json={"wrong_field": "something"})
        assert response.status_code == 400

    def test_missing_body_returns_400(self, client):
        response = client.post("/api/v1/ask", content_type="application/json")
        assert response.status_code == 400

    @patch("app.api.routes.RAGGenerator")
    def test_successful_question_returns_200(self, mock_generator, client):
        mock_generator.return_value.answer.return_value = (
            "RAG is a technique that combines LLMs with external knowledge."
        )

        response = client.post("/api/v1/ask", json={"question": "What is RAG?"})

        assert response.status_code == 200
        body = response.get_json()
        assert body["question"] == "What is RAG?"
        assert "RAG" in body["answer"]
        assert "answer" in body

    @patch("app.api.routes.RAGGenerator")
    def test_generator_failure_returns_500(self, mock_generator, client):
        mock_generator.return_value.answer.side_effect = Exception("LLM API timeout")

        response = client.post("/api/v1/ask", json={"question": "What is RAG?"})

        assert response.status_code == 500
        body = response.get_json()
        assert "error" in body
        assert "detail" in body

    @patch("app.api.routes.RAGGenerator")
    def test_question_is_stripped_before_processing(self, mock_generator, client):
        """
        Whitespace around the question must be stripped before processing.
        Tests that strip() in routes.py works as expected.
        """
        mock_generator.return_value.answer.return_value = "Some answer."

        response = client.post(
            "/api/v1/ask",
            json={"question": "  What is RAG?  "}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["question"] == "What is RAG?"
