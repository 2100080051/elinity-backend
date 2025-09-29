import os
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv(override=True)  # reload .env and override existing vars


class FirebaseStorageClient:
    """
    Firebase Storage Client using Google Cloud Storage SDK.
    Supports uploading from bytes or file paths.
    """

    def __init__(self) -> None:
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds:
            if not os.path.isabs(creds):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
                creds = os.path.join(project_root, creds)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds

            if not os.path.exists(creds):
                raise FileNotFoundError(f"Google credentials file not found at {creds}")

        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME env var not set.")

        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _generate_path(self, tenant_id: str, filename: str) -> str:
        """
        Generate a Firebase Storage path using tenant_id and filename.
        """
        return f"{tenant_id}/{filename}"

    def upload_file(self, file_or_bytes, filename: str, tenant_id: str) -> str:
        """
        Upload either a local file (path) or in-memory bytes to Firebase Storage.
        Returns the public URL.
        """
        blob_path = self._generate_path(tenant_id, filename)
        blob = self.bucket.blob(blob_path)

        if isinstance(file_or_bytes, (bytes, bytearray)):
            # Upload bytes
            blob.upload_from_string(file_or_bytes, content_type="application/octet-stream")
        elif isinstance(file_or_bytes, str) and os.path.isfile(file_or_bytes):
            # Upload from file path
            blob.upload_from_filename(file_or_bytes)
        else:
            raise ValueError("file_or_bytes must be bytes or valid file path.")

        # By default Firebase URLs are public via token
        return blob.public_url
