import boto3
import os
from dotenv import load_dotenv
load_dotenv()




AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION = os.getenv("REGION")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)
def upload_to_s3(file_path,file_name, user_id):
    s3_key = f"users/{user_id}/{file_name}"
    s3.upload_file(file_path, BUCKET_NAME, s3_key,ExtraArgs={"ContentType": "application/pdf"})
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

