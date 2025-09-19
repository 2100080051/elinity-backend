import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Load .env (for local dev)
load_dotenv(override=True)

# ---------------------------
# GOOGLE FIREBASE / GCS CONFIG
# ---------------------------

# Prefer GOOGLE_APPLICATION_CREDENTIALS env var (Render/Cloud)
# Fallback: local file keys/firebase.json
creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "keys/firebase.json")

# Convert relative path to absolute
if not os.path.isabs(creds):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    creds = os.path.join(project_root, creds)

# Update env var so Google client libraries pick it up
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds

# Validate credentials file exists
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
    """
    if not local_path or not remote_prefix:
        raise ValueError("Both local_path and remote_prefix are required.")

    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME env var not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Use filename from local_path under the given prefix
    filename = os.path.basename(local_path)
    blob = bucket.blob(f"{remote_prefix}/{filename}")

    # Upload the file
    blob.upload_from_filename(local_path)

    # Make file public
    blob.make_public()

    return blob.public_url


# ---------------------------
# AWS S3 CONFIG
# ---------------------------

class AWSStorage:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION")

        if not self.bucket_name:
            raise ValueError("AWS_BUCKET_NAME env var not set.")

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

    def upload_file(self, local_path: str, remote_prefix: str) -> str:
        """
        Uploads a file to AWS S3 and makes it public.

        Args:
            local_path: Path to the local file to upload.
            remote_prefix: Folder path in the bucket (e.g., 'personal_painter').

        Returns:
            Public URL of the uploaded object.
        Raises:
            ValueError: If local_path or remote_prefix is not provided.
        """
        if not local_path or not remote_prefix:
            raise ValueError("Both local_path and remote_prefix are required.")

        try:
            filename = os.path.basename(local_path)
            s3_key = f"{remote_prefix}/{filename}"

            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)

            object_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            return object_url

        except FileNotFoundError:
            raise FileNotFoundError("The local file was not found.")
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not available.")
        except ClientError as e:
            raise RuntimeError(f"Error uploading to S3: {e}")


# ---------------------------
# Firebase Storage Wrapper (Optional)
# ---------------------------

class FirebaseStorage:
    """
    Thin wrapper around Google Cloud Storage for Firebase buckets.
    Uses the same upload_to_gcs function but with default bucket prefix.
    """

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME env var not set.")

        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, local_path: str, remote_prefix: str) -> str:
        if not local_path or not remote_prefix:
            raise ValueError("Both local_path and remote_prefix are required.")

        filename = os.path.basename(local_path)
        blob = self.bucket.blob(f"{remote_prefix}/{filename}")
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
