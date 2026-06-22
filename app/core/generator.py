import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from app.config import get_settings
from app.db.vector_store import VectorStore

logger = logging.getLogger(__name__)


RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question using ONLY
the context provided below. If the context doesn't contain enough
information to answer, say "I don't have enough information to
answer that" — do not make up an answer.

Context:
{context}

Question:
{question}

Answer:"""
)


def format_docs(docs: list[Document]) -> str:
    """
    Converts a list of retrieved Document objects into a single
    text block the LLM can read.

    Each chunk is separated by a blank line so the LLM can
    visually distinguish where one chunk ends and another begins.
    """
    return "\n\n".join(doc.page_content for doc in docs)


class RAGGenerator:
    """
    Ties retrieval and generation together.

    Responsible for ONE thing:
    Given a question, retrieve context and generate an answer.
    """

    def __init__(self):
        settings = get_settings()

        self.llm = ChatOpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            model=settings.model_name,
            temperature=0,
        )

        vector_store = VectorStore()
        retriever = vector_store.as_retriever()

        self.chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | RAG_PROMPT
            | self.llm
            | StrOutputParser()
        )

        logger.info(f"RAGGenerator ready | model={settings.model_name}")

    def answer(self, question: str) -> str:
        """
        Runs the full RAG chain: retrieve context, generate answer.
        """
        logger.info(f"Generating answer | question='{question}'")
        result = self.chain.invoke(question)
        logger.info("Answer generated successfully")
        return result
