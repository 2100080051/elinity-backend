import os
from dotenv import load_dotenv
import boto3
load_dotenv(override=True)  # reload .env and override existing vars

# Ensure GOOGLE_APPLICATION_CREDENTIALS points to an absolute path
creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if creds:
    # Convert relative path to absolute based on project root
    if not os.path.isabs(creds):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        creds = os.path.join(project_root, creds)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds
    # Validate the credentials file exists
    if not os.path.exists(creds):
        raise FileNotFoundError(f"Google credentials file not found at {creds}")

from google.cloud import storage


def upload_to_gcs(local_path: str, remote_prefix: str) -> str:
    """
    Uploads a file to Google Cloud Storage and makes it public.

    Args:
        local_path: Path to the local file to upload.
        remote_prefix: Folder path in the bucket (e.g., 'personal_painter').

    Returns:
        Public URL of the uploaded blob.
    
    Raises:
        ValueError: If local_path or remote_prefix is not provided.
        ValueError: If GCS_BUCKET_NAME env var is not set.
    
    Notes:
        - The blob will be made public by default.
        - The local file will be deleted after upload.
    
    # Make the blob publicly accessible
    # blob.make_public()
    """ 
    if not local_path:
        raise ValueError("local_path is required.") 
    if not remote_prefix:
        raise ValueError("remote_prefix is required.")
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME env var not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    filename = os.path.basename(local_path)
    blob_path = f"{remote_prefix}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)

    return blob.public_url


def upload_bytes_to_gcs(data: bytes, filename: str, remote_prefix: str) -> str:
    """
    Uploads in-memory bytes to GCS and makes it public.
    """
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME env var not set.")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_path = f"{remote_prefix}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(data, content_type="image/png")
    # blob.make_public()
    return blob.public_url



class AWSStorage:
    """
    AWS Storage class for uploading files to AWS S3.
    """
    def __init__(self) -> None:
        self.client = boto3.client("s3")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        if not self.bucket_name:
            raise ValueError("AWS_BUCKET_NAME env var not set.")
        if not self.region:
            raise ValueError("AWS_REGION env var not set.")
        if not self.access_key:
            raise ValueError("AWS_ACCESS_KEY_ID env var not set.")
        if not self.secret_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY env var not set.")
        
    def _generate_s3_key(self, tenant_id: str, filename: str) -> str:
        """
        Helper to generate the S3 key using tenant_id and filename
        """
        return f"{tenant_id}/{filename}"

    def upload_bytes_to_aws(self, data: bytes, filename: str, tenant_id: str) -> str:
        """
        Uploads in-memory bytes to AWS S3 under a tenant-specific path.
        """
        blob_path = self._generate_s3_key(tenant_id, filename)
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=blob_path,
            Body=data, 
        )
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{blob_path}"

    def upload_file_to_aws(self, file_path: str, tenant_id: str) -> str:
        """
        Uploads a file to AWS S3 under a tenant-specific path.
        """
        filename = os.path.basename(file_path)
        blob_path = self._generate_s3_key(tenant_id, filename)
        self.client.upload_file(file_path, self.bucket_name, blob_path)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{blob_path}"
 