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


@router.post("/upload")
async def upload_file(user_id: str = Query(...), file: UploadFile = File(...)):
    
    file_path = os.path.join(UPLOAD_DIR, user_id + "_" + file.filename)

    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    
    s3_url = upload_to_s3(file_path,  file.filename,user_id)

    
    save_file_record(user_id, file.filename, s3_url)

    
    ingest_document(file_path, user_id)
    print("USER ID:", user_id)
    print("FILE PATH:", file_path)
    print("S3 URL:", s3_url)

    return {
        "message": "File uploaded and processed successfully",
        "s3_url": s3_url

    
    }
