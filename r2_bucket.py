import boto3
import json
import os

# Cloudflare R2 Configuration
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Create S3 client
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY
)

def upload(file_path):
    try:
        # Upload file to R2
        file_key = (file_path.split('/')[-1])
        s3.upload_file(file_path, R2_BUCKET_NAME, file_key)
        print(f"File uploaded successfully: https://your-cdn.com/{file_key}")

    except Exception as e:
        print(f"Error uploading file: {e}")

def get_bucket_contents():
    response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)
    if "Contents" in response: #checks if empty
        return [obj["Key"] for obj in response["Contents"]]
    else:
        return None