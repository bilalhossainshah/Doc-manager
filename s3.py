import boto3
import os
from dotenv import load_dotenv

load_dotenv()


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("REGION")
    )


def upload_to_s3(file_path, file_name, user_id):
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name or not os.getenv("AWS_ACCESS_KEY"):
        # Fallback to local storage path when AWS S3 is not configured
        return f"/uploads/{user_id}_{file_name}"

    s3 = get_s3_client()
    s3_key = f"users/{user_id}/{file_name}"
    s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={"ContentType": "application/pdf"})
    return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

def download_from_s3(s3_key, local_path):
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is not set")

    s3 = get_s3_client()
    s3.download_file(bucket_name, s3_key, local_path)
    return local_path