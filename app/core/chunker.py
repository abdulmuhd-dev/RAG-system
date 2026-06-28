import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import get_settings

logger = logging.getLogger(__name__)

SUPPORTED_LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
}


class DocumentChunker:
    """
    Responsible for ONE thing:
    Load a file from disk → return a list of chunks.
    """

    def __init__(self):
        settings = get_settings()

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def load(self, file_path: str) -> list[Document]:
        """Load a file from disk into LangChain Document objects."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        loader_class = SUPPORTED_LOADERS.get(path.suffix.lower())

        if not loader_class:
            raise ValueError(
                f"Unsupported file type: '{path.suffix}'. "
                f"Supported types: {list(SUPPORTED_LOADERS.keys())}"
            )

        logger.info(f"Loading file: {file_path}")
        loader = loader_class(file_path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} page(s) from {path.name}")

        return documents

    def chunk(self, documents: list[Document]) -> list[Document]:
        """Split loaded documents into smaller chunks."""
        chunks = self.splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks

    def load_and_chunk(self, file_path: str) -> list[Document]:
        """Convenience method — load + chunk in one call."""
        documents = self.load(file_path)
        chunks = self.chunk(documents)
        return chunks
