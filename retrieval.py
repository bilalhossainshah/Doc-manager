from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")

def retrieve_answer(query: str, user_id: str):
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    
    persist_dir = f"{CHROMA_DB_DIR}/{user_id}"

    if not os.path.exists(persist_dir):
        return {
            "error": f"No documents found for user: {user_id}",
            "answer": None,
            
        }

    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    
    retriever = vectordb.as_retriever(
        search_kwargs={"k": 3}
    )

    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0
    )




    
    prompt_template = """
You are a helpful AI assistant.

Answer the question ONLY using the provided context.
Do not make up information.
If the answer is not present in the context, say: "Answer not found in the document."
provide the refrences of the source documents in the format: [source: document_name, chunk_id: chunk_id, page: page_number]

Give a clear, structured, and detailed answer.

Context:
{context}



Question: {question}



Answer:
"""

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )

   
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke({"query": query})
    print(f"✅ Answer generated: {result['result']}")

    return result["result"]


    Step 7: Source chunks extract karo (uncomment if needed)
    source_chunks = []
    for doc in result["source_documents"]:
        source_chunks.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "chunk_id": doc.metadata.get("chunk_id", "unknown"),
            "page": doc.metadata.get("page", "unknown")
        })



    return {
        "answer": result["result"],
        "source_chunks": source_chunks,
        "total_chunks_used": len(source_chunks)
    }
    def retrieve_answer(query: str, user_id: str):
        persist_dir = f"{CHROMA_DB_DIR}/{user_id}"
        return retrieve_answer(query, user_id)
        