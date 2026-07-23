import logging
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")


def ingest_document(file_path, user_id):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)

    logger.info("Chunks created: %d", len(chunks))
    if chunks:
        logger.info("Sample chunk content: %s...", chunks[0].page_content[:200])
        logger.info("Sample chunk metadata: %s", chunks[0].metadata)

    for i, chunk in enumerate(chunks):
        chunk.metadata["user_id"] = user_id
        chunk.metadata["source"] = file_path

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    persist_dir = f"{CHROMA_DB_DIR}/{user_id}"

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    vectordb.persist()
    logger.info("Stored in ChromaDB")

