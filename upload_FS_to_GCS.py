#!/usr/bin/env python3
import sys
import os
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def main():
    # Set project ID and bucket name
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set")

    # Get the directory path of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Set local CSV file path
    source_file_name = os.path.join(current_dir, "FS_with_price.csv")

    # Set destination file name in GCS
    destination_blob_name = "financial-statements/FS_with_price.csv"

    # Set service account key file path
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

    # Upload file
    upload_blob(bucket_name, source_file_name, destination_blob_name)

if __name__ == "__main__":
    main()