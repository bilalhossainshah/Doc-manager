from fastapi import APIRouter
from schemas import QueryRequest
from retrieval import retrieve_answer

router = APIRouter()

@router.post("/query")  
async def query_documents(request: QueryRequest):
    """Query ingested user documents using RAG pipeline."""
    result = retrieve_answer(
        query=request.question,
        user_id=request.user_id
    )
    return result