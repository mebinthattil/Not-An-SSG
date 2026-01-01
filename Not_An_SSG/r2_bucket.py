import boto3
import os

# Lazy-initialized S3 client, so we create client only when needed
# Helpful in cases where users won't be using this with storage buckets
_s3_client = None


def _get_s3_client():
    """
    get or create S3 client with lazy initialization.
    """
    global _s3_client
    if _s3_client is None:
        endpoint_url = os.getenv("STORAGE_ENDPOINT_URL")
        access_key = os.getenv("STORAGE_ACCESS_KEY_ID")
        secret_key = os.getenv("STORAGE_SECRET_ACCESS_KEY")
        region = os.getenv("STORAGE_REGION_NAME")
        
        if not all([endpoint_url, access_key, secret_key]):
            raise ValueError('''
                Storage credentials not configured. 
                Run 'not_an_ssg config setup' in the terminal to configure cloud storage. ''')
        
        _s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    return _s3_client


def upload(file_path, verbose=False) -> str:
    """Upload a file to the configured bucket."""
    try:
        s3 = _get_s3_client()
        bucket_name = os.getenv("STORAGE_BUCKET_NAME")
        cdn_url = os.getenv("CDN_URL", "")
        
        file_key = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, file_key)
        
        if verbose:
            print(f"File uploaded successfully: {cdn_url}/{file_key}")
        return f"{cdn_url}/{file_key}"

    except Exception as e:
        print(f"Error uploading file: {e}")
        return ""


def get_bucket_contents():
    """List all files in the configured bucket."""
    try:
        s3 = _get_s3_client()
        bucket_name = os.getenv("STORAGE_BUCKET_NAME")
        
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []
    except Exception as e:
        print(f"Error listing bucket contents: {e}")
        return []