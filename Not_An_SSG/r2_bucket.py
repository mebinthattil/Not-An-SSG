import boto3
import json
import os

# Cloudflare R2 Configuration
R2_ACCESS_KEY_ID = os.getenv("STORAGE_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("STORAGE_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME")
R2_ACCOUNT_ID = os.getenv("STORAGE_ACCOUNT_ID")
R2_ENDPOINT_URL = os.getenv("STORAGE_ENDPOINT_URL")
R2_REGION_NAME = os.getenv("STORAGE_REGION_NAME")
CDN_URL = os.getenv("CDN_URL")

# Create S3 client
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name=R2_REGION_NAME
)

def upload(file_path, verbose=False) -> str:
    try:
        # Upload file to R2
        file_key = (file_path.split('/')[-1])
        s3.upload_file(file_path, R2_BUCKET_NAME, file_key)
        if verbose:
            print(f"File uploaded successfully: {CDN_URL}/{file_key}")
        return f"{CDN_URL}/{file_key}"

    except Exception as e:
        print(f"Error uploading file: {e}")

def get_bucket_contents():
    response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)
    if "Contents" in response: #checks if empty
        return [obj["Key"] for obj in response["Contents"]]
    else:
        return None