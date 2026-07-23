import os
from fastapi import APIRouter, UploadFile, File, Query
from s3 import upload_to_s3
from database import save_file_record
from ingestion import ingest_document
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


import logging

logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(user_id: str = Query(...), file: UploadFile = File(...)):
    """Upload PDF document, store in S3, and trigger document ingestion."""
    
    file_path = os.path.join(UPLOAD_DIR, user_id + "_" + file.filename)

    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    
    s3_url = upload_to_s3(file_path,  file.filename,user_id)

    
    save_file_record(user_id, file.filename, s3_url)

    
    ingest_document(file_path, user_id)
    logger.info("USER ID: %s", user_id)
    logger.info("FILE PATH: %s", file_path)
    logger.info("S3 URL: %s", s3_url)

    return {
        "message": "File uploaded and processed successfully",
        "s3_url": s3_url

    
    }
