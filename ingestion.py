from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader)

import os
from dotenv import load_dotenv

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

    print(f" Chunks created: {len(chunks)}")
    print(f" Sample chunk content: {chunks[0].page_content[:200]}...")
    print(f" Sample chunk metadata: {chunks[0].metadata}  ")

    
    for i, chunk in enumerate(chunks):
        chunk.metadata["user_id"] = user_id
        chunk.metadata["source"] = file_path
        # chunk.metadata["chunk_id"] = i   

    
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

    print("✅ Stored in ChromaDB")

