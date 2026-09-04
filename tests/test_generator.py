import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


class TestFormatDocs:

    def test_single_doc_returns_content(self):
        """Single document returns its page_content."""
        from app.core.generator import format_docs

        doc = MagicMock()
        doc.page_content = "This is a test chunk."

        result = format_docs([doc])
        assert result == "This is a test chunk."

    def test_multiple_docs_joined_by_blank_line(self):
        """Multiple docs must be separated by double newline."""
        from app.core.generator import format_docs

        doc1 = MagicMock()
        doc1.page_content = "First chunk."
        doc2 = MagicMock()
        doc2.page_content = "Second chunk."

        result = format_docs([doc1, doc2])
        assert result == "First chunk.\n\nSecond chunk."

    def test_empty_list_returns_empty_string(self):
        """Empty doc list must return empty string."""
        from app.core.generator import format_docs

        result = format_docs([])
        assert result == ""

    def test_three_docs_joined_correctly(self):
        """Three docs must all be joined with double newlines."""
        from app.core.generator import format_docs

        docs = [MagicMock() for _ in range(3)]
        docs[0].page_content = "Chunk A."
        docs[1].page_content = "Chunk B."
        docs[2].page_content = "Chunk C."

        result = format_docs(docs)
        assert result == "Chunk A.\n\nChunk B.\n\nChunk C."


class TestRAGGenerator:

    @patch("app.core.generator.VectorStore")
    @patch("app.core.generator.ChatOpenAI")
    def test_initializes_successfully(
        self, mock_llm, mock_vector_store
    ):
        """RAGGenerator must initialize without errors."""
        from app.core.generator import RAGGenerator

        generator = RAGGenerator()
        assert generator is not None
        assert generator.chain is not None

    @patch("app.core.generator.VectorStore")
    @patch("app.core.generator.ChatOpenAI")
    def test_answer_returns_string(
        self, mock_llm, mock_vector_store
    ):
        """answer() must return a plain string."""
        from app.core.generator import RAGGenerator

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = (
            "RAG stands for Retrieval-Augmented Generation."
        )

        generator = RAGGenerator()
        generator.chain = mock_chain

        result = generator.answer("What is RAG?")

        assert isinstance(result, str)
        assert result == "RAG stands for Retrieval-Augmented Generation."
        mock_chain.invoke.assert_called_once_with("What is RAG?")

    @patch("app.core.generator.VectorStore")
    @patch("app.core.generator.ChatOpenAI")
    def test_answer_propagates_exceptions(
        self, mock_llm, mock_vector_store
    ):
        """answer() must propagate exceptions — not swallow them."""
        from app.core.generator import RAGGenerator

        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("LLM timeout")

        generator = RAGGenerator()
        generator.chain = mock_chain

        with pytest.raises(Exception, match="LLM timeout"):
            generator.answer("What is RAG?")

    @patch("app.core.generator.VectorStore")
    @patch("app.core.generator.ChatOpenAI")
    def test_answer_calls_chain_with_question(
        self, mock_llm, mock_vector_store
    ):
        """answer() must pass question directly to chain."""
        from app.core.generator import RAGGenerator

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Some answer."

        generator = RAGGenerator()
        generator.chain = mock_chain

        generator.answer("How does RAG work?")

        mock_chain.invoke.assert_called_once_with("How does RAG work?")


class TestRAGPrompt:

    def test_prompt_contains_context_placeholder(self):
        """RAG prompt must contain {context} placeholder."""
        from app.core.generator import RAG_PROMPT

        prompt_str = str(RAG_PROMPT)
        assert "context" in prompt_str

    def test_prompt_contains_question_placeholder(self):
        """RAG prompt must contain {question} placeholder."""
        from app.core.generator import RAG_PROMPT

        prompt_str = str(RAG_PROMPT)
        assert "question" in prompt_str
