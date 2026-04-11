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
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is not set")

    s3 = get_s3_client()
    s3_key = f"users/{user_id}/{file_name}"
    s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={"ContentType": "application/pdf"})
    return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

