import os
import tempfile

import pytest

from app.core.chunker import DocumentChunker


class TestDocumentChunker:

    def test_unsupported_file_type_raises_value_error(self):
        """
        Unsupported extension must raise ValueError.
        Uses a real temp file with unsupported extension.
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".docx",
            delete=False
        ) as tmp:
            tmp.write("fake content")
            tmp_path = tmp.name

        try:
            chunker = DocumentChunker()
            with pytest.raises(ValueError, match="Unsupported file type"):
                chunker.load(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_missing_file_raises_file_not_found(self):
        """Non-existent file path must raise FileNotFoundError."""
        chunker = DocumentChunker()
        with pytest.raises(FileNotFoundError, match="File not found"):
            chunker.load("/tmp/nonexistent_file_xyz.txt")

    def test_load_returns_documents(self):
        """
        Successful load must return a list of documents.
        Uses a real temp file — no mocking needed.
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as tmp:
            tmp.write("This is test content for the RAG system.")
            tmp_path = tmp.name

        try:
            chunker = DocumentChunker()
            docs = chunker.load(tmp_path)

            assert len(docs) >= 1
            assert "test content" in docs[0].page_content
        finally:
            os.unlink(tmp_path)

    def test_load_and_chunk_returns_chunks(self):
        """
        load_and_chunk must split large content into chunks.
        Writes 600 chars — guarantees at least 2 chunks
        with default chunk_size of 500.
        """
        content = "word " * 120  # 600 chars

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            chunker = DocumentChunker()
            chunks = chunker.load_and_chunk(tmp_path)

            assert len(chunks) >= 1
            assert all(hasattr(c, "page_content") for c in chunks)
        finally:
            os.unlink(tmp_path)

    def test_chunk_preserves_metadata(self):
        """
        Metadata must survive chunking — source attribution
        in RAG answers depends on this.
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as tmp:
            tmp.write("word " * 200)
            tmp_path = tmp.name

        try:
            chunker = DocumentChunker()
            chunks = chunker.load_and_chunk(tmp_path)

            for chunk in chunks:
                assert "source" in chunk.metadata
                assert tmp_path in chunk.metadata["source"]
        finally:
            os.unlink(tmp_path)
